#!/usr/bin/env python3
"""
AWS Architecture Scanner MCP Server
Scans AWS environments and generates visual architecture diagrams
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSArchitectureScanner:
    """Scans AWS resources and builds architecture data"""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client("ec2", region_name=region)
        self.ecs = boto3.client("ecs", region_name=region)
        self.eks = boto3.client("eks", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.s3 = boto3.client("s3")
        self.rds = boto3.client("rds", region_name=region)
        self.efs = boto3.client("efs", region_name=region)

    def scan_vpcs(self) -> List[Dict[str, Any]]:
        """Scan VPCs and related networking resources"""
        try:
            vpcs_response = self.ec2.describe_vpcs()
            vpcs = []

            for vpc in vpcs_response.get("Vpcs", []):
                vpc_id = vpc["VpcId"]
                vpc_data = {
                    "id": vpc_id,
                    "cidr": vpc["CidrBlock"],
                    "name": self._get_name_tag(vpc.get("Tags", [])),
                    "subnets": [],
                    "internet_gateways": [],
                    "nat_gateways": [],
                    "route_tables": [],
                    "security_groups": [],
                }

                # Get subnets
                subnets_response = self.ec2.describe_subnets(
                    Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                )
                for subnet in subnets_response.get("Subnets", []):
                    vpc_data["subnets"].append(
                        {
                            "id": subnet["SubnetId"],
                            "cidr": subnet["CidrBlock"],
                            "az": subnet["AvailabilityZone"],
                            "name": self._get_name_tag(subnet.get("Tags", [])),
                            "public": subnet.get("MapPublicIpOnLaunch", False),
                        }
                    )

                # Get Internet Gateways
                igw_response = self.ec2.describe_internet_gateways(
                    Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
                )
                for igw in igw_response.get("InternetGateways", []):
                    vpc_data["internet_gateways"].append(
                        {
                            "id": igw["InternetGatewayId"],
                            "name": self._get_name_tag(igw.get("Tags", [])),
                        }
                    )

                # Get NAT Gateways
                nat_response = self.ec2.describe_nat_gateways(
                    Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                )
                for nat in nat_response.get("NatGateways", []):
                    if nat["State"] == "available":
                        vpc_data["nat_gateways"].append(
                            {
                                "id": nat["NatGatewayId"],
                                "subnet_id": nat["SubnetId"],
                                "public_ip": nat["NatGatewayAddresses"][0][
                                    "PublicIp"
                                ]
                                if nat.get("NatGatewayAddresses")
                                else None,
                                "name": self._get_name_tag(nat.get("Tags", [])),
                            }
                        )

                # Get Route Tables
                rt_response = self.ec2.describe_route_tables(
                    Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                )
                for rt in rt_response.get("RouteTables", []):
                    vpc_data["route_tables"].append(
                        {
                            "id": rt["RouteTableId"],
                            "name": self._get_name_tag(rt.get("Tags", [])),
                            "routes": [
                                {
                                    "destination": r.get("DestinationCidrBlock", ""),
                                    "target": r.get("GatewayId")
                                    or r.get("NatGatewayId")
                                    or "local",
                                }
                                for r in rt.get("Routes", [])
                            ],
                        }
                    )

                # Get Security Groups
                sg_response = self.ec2.describe_security_groups(
                    Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                )
                for sg in sg_response.get("SecurityGroups", []):
                    vpc_data["security_groups"].append(
                        {
                            "id": sg["GroupId"],
                            "name": sg["GroupName"],
                            "description": sg["Description"],
                        }
                    )

                vpcs.append(vpc_data)

            return vpcs

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error scanning VPCs: {e}")
            return []

    def scan_compute(self, vpc_id: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Scan compute resources (EC2, ECS, EKS, Lambda)"""
        compute = {"ec2": [], "ecs": [], "eks": [], "lambda": []}

        try:
            # EC2 Instances
            filters = [{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
            if vpc_id:
                filters.append({"Name": "vpc-id", "Values": [vpc_id]})

            ec2_response = self.ec2.describe_instances(Filters=filters)
            for reservation in ec2_response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    compute["ec2"].append(
                        {
                            "id": instance["InstanceId"],
                            "type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                            "subnet_id": instance.get("SubnetId"),
                            "vpc_id": instance.get("VpcId"),
                            "name": self._get_name_tag(instance.get("Tags", [])),
                            "private_ip": instance.get("PrivateIpAddress"),
                            "public_ip": instance.get("PublicIpAddress"),
                        }
                    )

            # ECS Clusters
            ecs_clusters = self.ecs.list_clusters()
            for cluster_arn in ecs_clusters.get("clusterArns", []):
                cluster_details = self.ecs.describe_clusters(clusters=[cluster_arn])
                for cluster in cluster_details.get("clusters", []):
                    compute["ecs"].append(
                        {
                            "name": cluster["clusterName"],
                            "arn": cluster["clusterArn"],
                            "status": cluster["status"],
                            "running_tasks": cluster.get("runningTasksCount", 0),
                        }
                    )

            # EKS Clusters
            eks_clusters = self.eks.list_clusters()
            for cluster_name in eks_clusters.get("clusters", []):
                cluster_details = self.eks.describe_cluster(name=cluster_name)
                cluster = cluster_details.get("cluster", {})
                if not vpc_id or cluster.get("resourcesVpcConfig", {}).get(
                    "vpcId"
                ) == vpc_id:
                    compute["eks"].append(
                        {
                            "name": cluster["name"],
                            "arn": cluster["arn"],
                            "status": cluster["status"],
                            "version": cluster.get("version"),
                            "vpc_id": cluster.get("resourcesVpcConfig", {}).get(
                                "vpcId"
                            ),
                        }
                    )

            # Lambda Functions
            lambda_response = self.lambda_client.list_functions()
            for function in lambda_response.get("Functions", []):
                vpc_config = function.get("VpcConfig", {})
                function_vpc_id = vpc_config.get("VpcId")
                if not vpc_id or function_vpc_id == vpc_id:
                    compute["lambda"].append(
                        {
                            "name": function["FunctionName"],
                            "arn": function["FunctionArn"],
                            "runtime": function.get("Runtime"),
                            "vpc_id": function_vpc_id,
                            "subnet_ids": vpc_config.get("SubnetIds", []),
                        }
                    )

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error scanning compute resources: {e}")

        return compute

    def scan_storage(self, vpc_id: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Scan storage resources (S3, RDS, EFS, EBS)"""
        storage = {"s3": [], "rds": [], "efs": [], "ebs": []}

        try:
            # S3 Buckets
            s3_response = self.s3.list_buckets()
            for bucket in s3_response.get("Buckets", []):
                try:
                    location = self.s3.get_bucket_location(Bucket=bucket["Name"])
                    bucket_region = location.get("LocationConstraint") or "us-east-1"
                    if bucket_region == self.region:
                        storage["s3"].append(
                            {
                                "name": bucket["Name"],
                                "creation_date": bucket["CreationDate"].isoformat(),
                            }
                        )
                except ClientError:
                    pass

            # RDS Instances
            rds_response = self.rds.describe_db_instances()
            for db in rds_response.get("DBInstances", []):
                db_vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                if not vpc_id or db_vpc_id == vpc_id:
                    storage["rds"].append(
                        {
                            "identifier": db["DBInstanceIdentifier"],
                            "engine": db["Engine"],
                            "status": db["DBInstanceStatus"],
                            "vpc_id": db_vpc_id,
                            "endpoint": db.get("Endpoint", {}).get("Address"),
                        }
                    )

            # EFS File Systems
            efs_response = self.efs.describe_file_systems()
            for fs in efs_response.get("FileSystems", []):
                # Get mount targets to determine VPC
                mt_response = self.efs.describe_mount_targets(
                    FileSystemId=fs["FileSystemId"]
                )
                mount_targets = mt_response.get("MountTargets", [])
                if mount_targets:
                    fs_vpc_id = mount_targets[0].get("VpcId")
                    if not vpc_id or fs_vpc_id == vpc_id:
                        storage["efs"].append(
                            {
                                "id": fs["FileSystemId"],
                                "name": fs.get("Name", ""),
                                "state": fs["LifeCycleState"],
                                "vpc_id": fs_vpc_id,
                            }
                        )

            # EBS Volumes
            ebs_response = self.ec2.describe_volumes()
            for volume in ebs_response.get("Volumes", []):
                attachments = volume.get("Attachments", [])
                if attachments:
                    instance_id = attachments[0].get("InstanceId")
                    storage["ebs"].append(
                        {
                            "id": volume["VolumeId"],
                            "size": volume["Size"],
                            "type": volume["VolumeType"],
                            "state": volume["State"],
                            "instance_id": instance_id,
                        }
                    )

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error scanning storage resources: {e}")

        return storage

    def _get_name_tag(self, tags: List[Dict]) -> str:
        """Extract Name tag from resource tags"""
        for tag in tags:
            if tag["Key"] == "Name":
                return tag["Value"]
        return ""


class DiagramGenerator:
    """Generates architecture diagrams from scanned AWS resources"""

    def __init__(self):
        try:
            from diagrams import Diagram, Cluster, Edge
            from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway, NATGateway
            from diagrams.aws.compute import EC2, ECS, EKS, Lambda
            from diagrams.aws.storage import S3, EFS, EBS
            from diagrams.aws.database import RDS

            self.Diagram = Diagram
            self.Cluster = Cluster
            self.Edge = Edge
            self.VPC = VPC
            self.PublicSubnet = PublicSubnet
            self.PrivateSubnet = PrivateSubnet
            self.InternetGateway = InternetGateway
            self.NATGateway = NATGateway
            self.EC2 = EC2
            self.ECS = ECS
            self.EKS = EKS
            self.Lambda = Lambda
            self.S3 = S3
            self.RDS = RDS
            self.EFS = EFS
            self.EBS = EBS
            self.available = True
        except (ImportError, Exception) as e:
            logger.warning(f"diagrams library not available: {e}. Diagram generation will be disabled.")
            self.available = False

    def generate(
        self,
        vpcs: List[Dict],
        compute: Dict[str, List[Dict]],
        storage: Dict[str, List[Dict]],
        output_path: str,
        filename: str = "aws_architecture",
        format: str = "png",
    ) -> str:
        """Generate architecture diagram"""
        if not self.available:
            return "Error: diagrams library not installed. Run: pip install diagrams"

        try:
            full_path = os.path.join(output_path, filename)

            with self.Diagram(
                "AWS Architecture",
                filename=full_path,
                outformat=format,
                show=False,
                direction="TB",
            ):
                internet = self.InternetGateway("Internet")

                for vpc_data in vpcs:
                    vpc_name = vpc_data["name"] or vpc_data["id"]
                    with self.Cluster(f"VPC: {vpc_name}\n{vpc_data['cidr']}"):
                        # Create IGW
                        igws = []
                        for igw in vpc_data["internet_gateways"]:
                            igw_node = self.InternetGateway(
                                igw["name"] or igw["id"][:12]
                            )
                            igws.append(igw_node)
                            internet >> igw_node

                        # Group subnets by AZ
                        public_subnets = [s for s in vpc_data["subnets"] if s["public"]]
                        private_subnets = [
                            s for s in vpc_data["subnets"] if not s["public"]
                        ]

                        # Create NAT Gateways
                        nat_nodes = []
                        for nat in vpc_data["nat_gateways"]:
                            nat_node = self.NATGateway(
                                f"{nat['name'] or 'NAT'}\n{nat.get('public_ip', '')[:15]}"
                            )
                            nat_nodes.append(nat_node)

                        # Public subnets
                        public_subnet_nodes = []
                        for subnet in public_subnets:
                            with self.Cluster(
                                f"Public: {subnet['name'] or subnet['id'][:15]}\n{subnet['cidr']} ({subnet['az']})"
                            ):
                                subnet_node = self.PublicSubnet(subnet["id"][:12])
                                public_subnet_nodes.append(subnet_node)

                                # Connect IGW to public subnets
                                if igws:
                                    igws[0] >> subnet_node

                                # Add NAT if in this subnet
                                for nat in vpc_data["nat_gateways"]:
                                    if nat["subnet_id"] == subnet["id"]:
                                        subnet_node >> [
                                            n
                                            for n in nat_nodes
                                            if nat["id"] in str(n)
                                        ]

                                # Add EC2 instances in this subnet
                                for ec2 in compute["ec2"]:
                                    if ec2.get("subnet_id") == subnet["id"]:
                                        ec2_node = self.EC2(
                                            f"{ec2['name'] or ec2['id'][:12]}\n{ec2['type']}"
                                        )
                                        subnet_node >> ec2_node

                        # Private subnets
                        for subnet in private_subnets:
                            with self.Cluster(
                                f"Private: {subnet['name'] or subnet['id'][:15]}\n{subnet['cidr']} ({subnet['az']})"
                            ):
                                subnet_node = self.PrivateSubnet(subnet["id"][:12])

                                # Connect NAT to private subnets
                                if nat_nodes:
                                    nat_nodes[0] >> subnet_node

                                # Add EC2 instances in this subnet
                                for ec2 in compute["ec2"]:
                                    if ec2.get("subnet_id") == subnet["id"]:
                                        ec2_node = self.EC2(
                                            f"{ec2['name'] or ec2['id'][:12]}\n{ec2['type']}"
                                        )
                                        subnet_node >> ec2_node

                                # Add RDS instances
                                for rds in storage["rds"]:
                                    if rds.get("vpc_id") == vpc_data["id"]:
                                        rds_node = self.RDS(
                                            f"{rds['identifier']}\n{rds['engine']}"
                                        )
                                        subnet_node >> rds_node

                        # Add EKS clusters
                        for eks in compute["eks"]:
                            if eks.get("vpc_id") == vpc_data["id"]:
                                self.EKS(f"{eks['name']}\nv{eks.get('version', '')}")

                        # Add Lambda functions
                        for func in compute["lambda"]:
                            if func.get("vpc_id") == vpc_data["id"]:
                                self.Lambda(f"{func['name']}\n{func.get('runtime', '')}")

                # Add S3 buckets (outside VPC)
                if storage["s3"]:
                    with self.Cluster("S3 Buckets"):
                        for bucket in storage["s3"][:5]:  # Limit to 5 for readability
                            self.S3(bucket["name"][:20])

            output_file = f"{full_path}.{format}"
            return f"Diagram generated successfully: {output_file}"

        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            return f"Error generating diagram: {str(e)}"


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool requests"""
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "scan_aws_architecture",
                    "description": "Scan AWS environment and generate architecture data",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "AWS region to scan (default: us-east-1)",
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Optional: Specific VPC ID to scan",
                            },
                        },
                    },
                },
                {
                    "name": "generate_architecture_diagram",
                    "description": "Generate visual architecture diagram from scanned AWS resources",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "AWS region to scan",
                                "default": "us-east-1",
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Optional: Specific VPC ID to diagram",
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Directory path to save the diagram",
                            },
                            "filename": {
                                "type": "string",
                                "description": "Output filename (without extension)",
                                "default": "aws_architecture",
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format: png or svg",
                                "enum": ["png", "svg"],
                                "default": "png",
                            },
                        },
                        "required": ["output_path"],
                    },
                },
            ]
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "scan_aws_architecture":
            region = args.get("region", "us-east-1")
            vpc_id = args.get("vpc_id")

            scanner = AWSArchitectureScanner(region=region)
            vpcs = scanner.scan_vpcs()

            # Filter to specific VPC if provided
            if vpc_id:
                vpcs = [v for v in vpcs if v["id"] == vpc_id]

            compute = scanner.scan_compute(vpc_id=vpc_id)
            storage = scanner.scan_storage(vpc_id=vpc_id)

            result = {
                "region": region,
                "scan_time": datetime.utcnow().isoformat(),
                "vpcs": vpcs,
                "compute": compute,
                "storage": storage,
            }

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str),
                    }
                ]
            }

        elif tool_name == "generate_architecture_diagram":
            region = args.get("region", "us-east-1")
            vpc_id = args.get("vpc_id")
            output_path = args["output_path"]
            filename = args.get("filename", "aws_architecture")
            format_type = args.get("format", "png")

            scanner = AWSArchitectureScanner(region=region)
            vpcs = scanner.scan_vpcs()

            if vpc_id:
                vpcs = [v for v in vpcs if v["id"] == vpc_id]

            compute = scanner.scan_compute(vpc_id=vpc_id)
            storage = scanner.scan_storage(vpc_id=vpc_id)

            generator = DiagramGenerator()
            result = generator.generate(
                vpcs=vpcs,
                compute=compute,
                storage=storage,
                output_path=output_path,
                filename=filename,
                format=format_type,
            )

            return {"content": [{"type": "text", "text": result}]}

    return {"error": f"Unknown method: {method}"}


async def main():
    """Main MCP server loop"""
    logger.info("AWS Architecture Scanner MCP Server starting...")

    while True:
        try:
            line = input()
            if not line:
                continue

            request = json.loads(line)
            response = await handle_request(request)
            print(json.dumps(response))

        except EOFError:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    asyncio.run(main())
