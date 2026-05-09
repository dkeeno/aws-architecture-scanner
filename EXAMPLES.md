# AWS Architecture Scanner - Usage Examples

## Example 1: Scan Your Current VPC

Scan the VPC you just created to see all its components:

```python
# Use this in Claude Code after the MCP server is configured
scan_aws_architecture(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe"
)
```

**Expected Output:**
```json
{
  "region": "us-east-1",
  "scan_time": "2026-04-17T19:00:00",
  "vpcs": [
    {
      "id": "vpc-06129df33ed494bbe",
      "cidr": "10.0.0.0/16",
      "name": "my-first-vpc",
      "subnets": [
        {
          "id": "subnet-0b4c27d08477a97a0",
          "cidr": "10.0.1.0/24",
          "az": "us-east-1a",
          "name": "my-first-vpc-public-us-east-1a",
          "public": true
        },
        {
          "id": "subnet-08f472c5bb5374cc2",
          "cidr": "10.0.2.0/24",
          "az": "us-east-1b",
          "name": "my-first-vpc-public-us-east-1b",
          "public": true
        },
        {
          "id": "subnet-0d52bb8e9d8a668d7",
          "cidr": "10.0.11.0/24",
          "az": "us-east-1a",
          "name": "my-first-vpc-private-us-east-1a",
          "public": false
        },
        {
          "id": "subnet-0b2ed540ccd83a41e",
          "cidr": "10.0.12.0/24",
          "az": "us-east-1b",
          "name": "my-first-vpc-private-us-east-1b",
          "public": false
        }
      ],
      "internet_gateways": [
        {
          "id": "igw-0a098e281e50ddd1b",
          "name": "my-first-vpc-igw"
        }
      ],
      "nat_gateways": [
        {
          "id": "nat-0108f5a28d8d946cf",
          "subnet_id": "subnet-0b4c27d08477a97a0",
          "public_ip": "3.227.35.163",
          "name": "my-first-vpc-nat"
        }
      ],
      "route_tables": [...],
      "security_groups": [...]
    }
  ],
  "compute": {
    "ec2": [],
    "ecs": [],
    "eks": [],
    "lambda": []
  },
  "storage": {
    "s3": [],
    "rds": [],
    "efs": [],
    "ebs": []
  }
}
```

## Example 2: Generate Architecture Diagram

Create a visual diagram of your VPC:

```python
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc",
    filename="my_first_vpc_architecture",
    format="png"
)
```

**Expected Output:**
```
Diagram generated successfully: /Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc/my_first_vpc_architecture.png
```

**What the diagram shows:**
- VPC boundary with CIDR block (10.0.0.0/16)
- Internet Gateway connected to the internet
- Two public subnets in us-east-1a and us-east-1b
- Two private subnets in us-east-1a and us-east-1b
- NAT Gateway in public subnet with public IP
- Routing connections (IGW → public subnets, NAT → private subnets)

## Example 3: Generate SVG for Documentation

Create an SVG version for better quality in documentation:

```python
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc",
    filename="architecture_diagram",
    format="svg"
)
```

**SVG Benefits:**
- Scalable without quality loss
- Smaller file size
- Can be embedded in web pages
- Editable in vector graphics tools

## Example 4: Scan All VPCs in a Region

Get a comprehensive view of all VPCs in us-east-1:

```python
scan_aws_architecture(region="us-east-1")
```

This will return data for ALL VPCs in the region, useful for:
- Inventory management
- Multi-VPC environments
- Finding unused resources
- Security audits

## Example 5: Scan Production Environment

Scan a different region where your production VPCs are:

```python
scan_aws_architecture(region="us-west-2")
```

Then generate diagrams for each VPC:

```python
# For first VPC
generate_architecture_diagram(
    region="us-west-2",
    vpc_id="vpc-xxxxx",
    output_path="/Users/youruser/Documents/prod-diagrams",
    filename="prod_vpc_01",
    format="png"
)

# For second VPC
generate_architecture_diagram(
    region="us-west-2",
    vpc_id="vpc-yyyyy",
    output_path="/Users/youruser/Documents/prod-diagrams",
    filename="prod_vpc_02",
    format="png"
)
```

## Example 6: Document Complex Architecture

For a VPC with EC2, RDS, and EKS:

```python
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-complex-app",
    output_path="/Users/youruser/Documents/architecture-docs",
    filename="application_architecture_2026",
    format="png"
)
```

**The diagram will show:**
- VPC structure with subnets
- EC2 instances placed in appropriate subnets
- RDS databases in private subnets
- EKS cluster configuration
- Lambda functions if using VPC integration
- S3 buckets (shown separately as they're not VPC-bound)
- Security groups and network boundaries

## Example 7: Before and After Comparison

Scan before making infrastructure changes:

```python
# Before changes
scan_result_before = scan_aws_architecture(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe"
)

generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents",
    filename="before_changes",
    format="png"
)

# Make infrastructure changes...
# (add EC2 instances, RDS databases, etc.)

# After changes
scan_result_after = scan_aws_architecture(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe"
)

generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents",
    filename="after_changes",
    format="png"
)
```

Compare the two diagrams to visualize what changed.

## Example 8: Generate Documentation Package

Create a complete documentation package:

```python
import os
import json

vpc_id = "vpc-06129df33ed494bbe"
output_dir = "/Users/youruser/Documents/vpc-documentation"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Scan architecture
scan_result = scan_aws_architecture(
    region="us-east-1",
    vpc_id=vpc_id
)

# Save JSON data
with open(f"{output_dir}/architecture_data.json", "w") as f:
    f.write(json.dumps(scan_result, indent=2))

# Generate PNG diagram
generate_architecture_diagram(
    region="us-east-1",
    vpc_id=vpc_id,
    output_path=output_dir,
    filename="architecture_diagram",
    format="png"
)

# Generate SVG diagram
generate_architecture_diagram(
    region="us-east-1",
    vpc_id=vpc_id,
    output_path=output_dir,
    filename="architecture_diagram",
    format="svg"
)
```

**Result:** Complete documentation package with:
- `architecture_data.json` - Raw scan data
- `architecture_diagram.png` - Visual diagram
- `architecture_diagram.svg` - Scalable vector diagram

## Tips and Best Practices

### 1. Regular Scanning
Schedule regular scans to keep documentation up-to-date:
```bash
# Weekly scan
scan_aws_architecture(region="us-east-1") > weekly_scan_$(date +%Y%m%d).json
```

### 2. Version Control
Store diagrams and scan data in git for change tracking:
```bash
git add diagrams/*.png
git commit -m "Update architecture diagrams - added RDS instances"
```

### 3. Multi-Region Strategy
Scan all regions where you have resources:
```python
regions = ["us-east-1", "us-west-2", "eu-west-1"]
for region in regions:
    generate_architecture_diagram(
        region=region,
        output_path=f"/docs/{region}",
        filename=f"architecture_{region}",
        format="png"
    )
```

### 4. Team Collaboration
Share diagrams in documentation platforms:
- Include in Confluence/Notion pages
- Embed in README files
- Attach to Jira tickets
- Include in architecture review documents

### 5. Security Audits
Use scan data for security reviews:
```python
# Scan and check for:
# - Public EC2 instances in private subnets
# - RDS databases in public subnets
# - Missing NAT Gateways
# - Overly permissive security groups
```

## Common Use Cases

| Use Case | Command | Output |
|----------|---------|--------|
| Quick VPC overview | `scan_aws_architecture(vpc_id="vpc-xxx")` | JSON data |
| Architecture documentation | `generate_architecture_diagram(...)` | PNG/SVG diagram |
| Pre-deployment validation | Scan → verify → deploy | Validation report |
| Post-deployment verification | Scan after Terraform apply | Updated diagram |
| Incident response | Scan during outage | Current state snapshot |
| Cost optimization | Scan → identify unused resources | Resource inventory |
| Compliance audit | Scan → check against standards | Audit report |
| Onboarding new engineers | Generate diagrams → share | Visual documentation |

## Integration Examples

### With Terraform
```bash
# After terraform apply
terraform output -json > outputs.json
# Use VPC ID from outputs to generate diagram
```

### With CI/CD
```yaml
# GitHub Actions example
- name: Generate Architecture Diagram
  run: |
    python3 -c "
    from mcp_client import scan_aws_architecture, generate_architecture_diagram
    generate_architecture_diagram(
        region='us-east-1',
        vpc_id='${{ secrets.VPC_ID }}',
        output_path='./diagrams',
        filename='current_architecture',
        format='png'
    )
    "
- name: Upload Diagram
  uses: actions/upload-artifact@v2
  with:
    name: architecture-diagram
    path: ./diagrams/*.png
```

### With Documentation Sites
```markdown
# Infrastructure Architecture

Last updated: 2026-04-17

![AWS Architecture](./my_first_vpc_architecture.png)

## VPC Details
- **VPC ID**: vpc-06129df33ed494bbe
- **CIDR**: 10.0.0.0/16
- **Region**: us-east-1
- **Availability Zones**: us-east-1a, us-east-1b
```

## Troubleshooting Scan Issues

### No resources found
```python
# Check region
scan_aws_architecture(region="correct-region")

# Check VPC ID
scan_aws_architecture(vpc_id="vpc-correct-id")

# Check AWS credentials
import boto3
print(boto3.client('sts').get_caller_identity())
```

### Diagram generation fails
```bash
# Verify Graphviz installation
which dot
dot -V

# Verify Python libraries
pip3 list | grep -E "diagrams|graphviz"

# Check output directory exists and is writable
ls -la /path/to/output
```

### Partial data returned
```python
# Check IAM permissions
# Ensure read access to: EC2, ECS, EKS, Lambda, S3, RDS, EFS
```
