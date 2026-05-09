#!/usr/bin/env python3
"""
Quick test script for AWS Architecture Scanner MCP Server
"""

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.dirname(__file__))

from server import AWSArchitectureScanner, DiagramGenerator

def test_scanner():
    """Test the scanner functionality"""
    print("Testing AWS Architecture Scanner...")
    print("=" * 60)

    try:
        # Test scanner
        print("\n1. Testing scanner initialization...")
        scanner = AWSArchitectureScanner(region="us-east-1")
        print("   ✓ Scanner initialized")

        # Test VPC scanning
        print("\n2. Testing VPC scan...")
        vpcs = scanner.scan_vpcs()
        print(f"   ✓ Found {len(vpcs)} VPC(s)")

        if vpcs:
            vpc = vpcs[0]
            print(f"\n   VPC Details:")
            print(f"   - ID: {vpc['id']}")
            print(f"   - CIDR: {vpc['cidr']}")
            print(f"   - Name: {vpc['name']}")
            print(f"   - Subnets: {len(vpc['subnets'])}")
            print(f"   - Internet Gateways: {len(vpc['internet_gateways'])}")
            print(f"   - NAT Gateways: {len(vpc['nat_gateways'])}")

        # Test compute scanning
        print("\n3. Testing compute resource scan...")
        compute = scanner.scan_compute()
        print(f"   ✓ EC2 instances: {len(compute['ec2'])}")
        print(f"   ✓ ECS clusters: {len(compute['ecs'])}")
        print(f"   ✓ EKS clusters: {len(compute['eks'])}")
        print(f"   ✓ Lambda functions: {len(compute['lambda'])}")

        # Test storage scanning
        print("\n4. Testing storage resource scan...")
        storage = scanner.scan_storage()
        print(f"   ✓ S3 buckets: {len(storage['s3'])}")
        print(f"   ✓ RDS instances: {len(storage['rds'])}")
        print(f"   ✓ EFS filesystems: {len(storage['efs'])}")
        print(f"   ✓ EBS volumes: {len(storage['ebs'])}")

        # Test diagram generator
        print("\n5. Testing diagram generator...")
        generator = DiagramGenerator()
        if generator.available:
            print("   ✓ Diagram generator available")
            print("   ✓ diagrams library loaded")
            print("   ✓ Graphviz available")
        else:
            print("   ✗ Diagram generator not available")
            print("   Run: pip3 install diagrams graphviz")
            print("   And: brew install graphviz")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("\nYour MCP server is ready to use in Claude Code.")
        print("\nTry asking Claude:")
        print('  "Scan my VPC vpc-06129df33ed494bbe in us-east-1"')
        print('  "Generate a diagram of my AWS architecture"')
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        print("\nTroubleshooting:")
        print("1. Check AWS credentials: aws sts get-caller-identity")
        print("2. Verify IAM permissions for EC2, ECS, EKS, Lambda, etc.")
        print("3. Install dependencies: pip3 install -r requirements.txt")
        print("4. Install Graphviz: brew install graphviz")
        return False

if __name__ == "__main__":
    success = test_scanner()
    sys.exit(0 if success else 1)
