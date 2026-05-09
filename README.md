# AWS Architecture Scanner MCP Server

Scans AWS environments and generates professional architecture diagrams showing VPC networking, compute, storage, and security resources.

## Features

### Scans the following AWS resources:

**VPC Networking:**
- VPCs with CIDR blocks
- Public and private subnets across availability zones
- Internet Gateways
- NAT Gateways
- Route tables and routing configuration
- Security Groups

**Compute:**
- EC2 instances (running and stopped)
- ECS clusters with task counts
- EKS clusters with versions
- Lambda functions with VPC configuration

**Storage:**
- S3 buckets (region-filtered)
- RDS database instances
- EFS file systems
- EBS volumes attached to instances

### Diagram Generation:

Creates professional PNG or SVG architecture diagrams using the Python `diagrams` library with official AWS icons showing:
- VPC boundaries and CIDR blocks
- Subnet grouping by type (public/private) and AZ
- Network connectivity (IGW → public subnets, NAT → private subnets)
- Compute resources placed in appropriate subnets
- Storage services with connections
- Visual hierarchy and clustering

## Installation

### 1. Install Python dependencies

```bash
cd ~/.mcp-servers/aws-architecture-scanner
pip3 install -r requirements.txt
```

### 2. Install Graphviz (required by diagrams library)

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Download from https://graphviz.org/download/

### 3. Configure AWS credentials

Ensure AWS credentials are configured:
```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### 4. Add to Claude Code MCP settings

Add to your project's `.claude/settings.json` or global `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "aws-architecture-scanner": {
      "command": "python3",
      "args": ["/Users/youruser/.mcp-servers/aws-architecture-scanner/server.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## MCP Tools

### 1. `scan_aws_architecture`

Scans AWS environment and returns JSON data structure of all discovered resources.

**Parameters:**
- `region` (string, optional): AWS region to scan (default: us-east-1)
- `vpc_id` (string, optional): Specific VPC ID to scan (scans all VPCs if not provided)

**Returns:** JSON object containing:
- VPCs with subnets, gateways, route tables, security groups
- Compute resources (EC2, ECS, EKS, Lambda)
- Storage resources (S3, RDS, EFS, EBS)

**Example:**
```python
scan_aws_architecture(region="us-east-1", vpc_id="vpc-06129df33ed494bbe")
```

### 2. `generate_architecture_diagram`

Scans AWS environment and generates a visual architecture diagram.

**Parameters:**
- `region` (string, optional): AWS region to scan (default: us-east-1)
- `vpc_id` (string, optional): Specific VPC ID to diagram
- `output_path` (string, **required**): Directory path to save the diagram
- `filename` (string, optional): Output filename without extension (default: "aws_architecture")
- `format` (string, optional): Output format - "png" or "svg" (default: "png")

**Returns:** Success message with output file path

**Example:**
```python
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents/diagrams",
    filename="my_vpc_architecture",
    format="png"
)
```

## Usage Examples

### Example 1: Scan your current VPC

```bash
# In Claude Code, use the MCP tool:
scan_aws_architecture(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe"
)
```

### Example 2: Generate diagram for your VPC

```bash
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc",
    filename="my_first_vpc_diagram",
    format="png"
)
```

### Example 3: Scan all VPCs in a region

```bash
scan_aws_architecture(region="us-west-2")
```

## Output

### Scan Output (JSON)
```json
{
  "region": "us-east-1",
  "scan_time": "2026-04-17T18:45:00",
  "vpcs": [
    {
      "id": "vpc-06129df33ed494bbe",
      "cidr": "10.0.0.0/16",
      "name": "my-first-vpc",
      "subnets": [...],
      "internet_gateways": [...],
      "nat_gateways": [...],
      "route_tables": [...],
      "security_groups": [...]
    }
  ],
  "compute": {
    "ec2": [...],
    "ecs": [...],
    "eks": [...],
    "lambda": [...]
  },
  "storage": {
    "s3": [...],
    "rds": [...],
    "efs": [...],
    "ebs": [...]
  }
}
```

### Diagram Output
- Professional PNG or SVG file
- Shows VPC boundaries with CIDR blocks
- Groups subnets by availability zone
- Displays connectivity between resources
- Uses official AWS service icons
- Clean, hierarchical layout

## IAM Permissions Required

The AWS credentials must have read permissions for:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeNatGateways",
        "ec2:DescribeRouteTables",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ecs:ListClusters",
        "ecs:DescribeClusters",
        "eks:ListClusters",
        "eks:DescribeCluster",
        "lambda:ListFunctions",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "rds:DescribeDBInstances",
        "elasticfilesystem:DescribeFileSystems",
        "elasticfilesystem:DescribeMountTargets"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Issue: "diagrams library not installed"
**Solution:**
```bash
pip3 install diagrams graphviz
brew install graphviz  # macOS
```

### Issue: "No module named 'graphviz'"
**Solution:** Install Graphviz system package (not just Python library)
```bash
brew install graphviz  # macOS
sudo apt-get install graphviz  # Linux
```

### Issue: "Unable to assume role" or permission errors
**Solution:** Check AWS credentials and IAM permissions:
```bash
aws sts get-caller-identity
aws iam get-user
```

### Issue: Diagram shows only some resources
**Solution:** Check that resources are in the correct region and VPC. Use `vpc_id` parameter to filter specific VPC.

### Issue: S3 buckets not appearing
**Solution:** S3 buckets are region-filtered. Only buckets in the specified region will appear.

## Advanced Usage

### Scan multiple regions

```python
for region in ["us-east-1", "us-west-2", "eu-west-1"]:
    scan_aws_architecture(region=region)
```

### Generate diagrams for all VPCs

```python
# First scan to get VPC IDs
scan_result = scan_aws_architecture(region="us-east-1")

# Parse JSON and generate diagram for each VPC
for vpc in scan_result["vpcs"]:
    generate_architecture_diagram(
        region="us-east-1",
        vpc_id=vpc["id"],
        output_path="/path/to/output",
        filename=f"vpc_{vpc['name']}",
        format="png"
    )
```

## Limitations

- **Single region per scan**: Scans one region at a time (not multi-region by default)
- **Diagram complexity**: Very large environments (50+ resources) may produce cluttered diagrams
- **S3 bucket limit**: Shows maximum 5 S3 buckets per diagram for readability
- **No cross-region connections**: Does not show VPC peering or Transit Gateway connections
- **Read-only**: Only scans existing resources, does not create or modify AWS infrastructure

## Future Enhancements

Potential features for future versions:
- Multi-region scanning with consolidated diagrams
- VPC peering and Transit Gateway visualization
- Security group rule visualization with port/protocol details
- Cost estimation for visualized resources
- Export to other formats (Terraform, CloudFormation)
- Mermaid diagram format for markdown documentation
- Interactive HTML diagrams
- Change detection (compare scans over time)

## Contributing

This MCP server is part of your local development environment. Modify `server.py` to add features or fix issues.

## License

For personal use in your AWS environment.
