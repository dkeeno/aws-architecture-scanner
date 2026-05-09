# Quick Start Guide - AWS Architecture Scanner

## What You Just Created

An MCP server that can:
1. **Scan** your AWS environment to discover all resources
2. **Generate** professional architecture diagrams automatically
3. **Visualize** VPCs, subnets, EC2, EKS, RDS, S3, and more

## Installation Status

✅ Python server created at: `~/.mcp-servers/aws-architecture-scanner/server.py`  
✅ Dependencies installed: `boto3`, `diagrams`, `graphviz`  
⏳ Graphviz system package: Installing via Homebrew  
✅ MCP server registered in Claude Code settings  

## Complete Graphviz Installation

If Graphviz didn't install automatically, run:

```bash
brew install graphviz
```

Verify installation:
```bash
which dot
dot -V
```

Expected output:
```
/opt/homebrew/bin/dot
dot - graphviz version X.X.X
```

## Test the MCP Server

### Test 1: Scan Your VPC

In Claude Code, ask:
```
Use the aws-architecture-scanner MCP server to scan my VPC vpc-06129df33ed494bbe in us-east-1
```

Or directly call the tool:
```
scan_aws_architecture(region="us-east-1", vpc_id="vpc-06129df33ed494bbe")
```

### Test 2: Generate Diagram

Ask Claude Code:
```
Generate an architecture diagram for my VPC vpc-06129df33ed494bbe and save it to the current directory
```

Or directly:
```
generate_architecture_diagram(
    region="us-east-1",
    vpc_id="vpc-06129df33ed494bbe",
    output_path="/Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc",
    filename="my_vpc_diagram",
    format="png"
)
```

## What the Diagram Will Show

For your newly created VPC, the diagram will display:

```
Internet
   ↓
Internet Gateway (igw-0a098e281e50ddd1b)
   ↓
┌─────────────────────────────────────────────────────────┐
│ VPC: my-first-vpc (10.0.0.0/16)                         │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │ Public Subnet    │         │ Public Subnet    │     │
│  │ 10.0.1.0/24      │         │ 10.0.2.0/24      │     │
│  │ us-east-1a       │         │ us-east-1b       │     │
│  │                  │         │                  │     │
│  │  [NAT Gateway]   │         │                  │     │
│  │  3.227.35.163    │         │                  │     │
│  └──────────────────┘         └──────────────────┘     │
│          ↓                                              │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │ Private Subnet   │         │ Private Subnet   │     │
│  │ 10.0.11.0/24     │         │ 10.0.12.0/24     │     │
│  │ us-east-1a       │         │ us-east-1b       │     │
│  └──────────────────┘         └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Available MCP Tools

### 1. `scan_aws_architecture`
**Purpose:** Scan AWS and return JSON data  
**Parameters:**
- `region` (optional): AWS region, default "us-east-1"
- `vpc_id` (optional): Specific VPC to scan

**Returns:** Complete resource inventory in JSON

### 2. `generate_architecture_diagram`
**Purpose:** Scan AWS and create visual diagram  
**Parameters:**
- `region` (optional): AWS region, default "us-east-1"
- `vpc_id` (optional): Specific VPC to diagram
- `output_path` (required): Directory to save diagram
- `filename` (optional): File name without extension, default "aws_architecture"
- `format` (optional): "png" or "svg", default "png"

**Returns:** Path to generated diagram file

## Next Steps

### 1. Generate Your First Diagram
```bash
# In Claude Code, say:
"Generate a diagram of my VPC vpc-06129df33ed494bbe"
```

### 2. Add EC2 Instances to Test
```bash
# Launch an EC2 instance in your VPC, then rescan:
"Scan my VPC again and generate a new diagram showing the EC2 instance"
```

### 3. Scan Different Regions
```bash
scan_aws_architecture(region="us-west-2")
```

### 4. Create Documentation
- Generate PNG for presentations
- Generate SVG for high-quality documentation
- Include in architecture review documents
- Share with team members

## Common Commands

```bash
# Scan all VPCs in us-east-1
scan_aws_architecture(region="us-east-1")

# Diagram specific VPC as PNG
generate_architecture_diagram(
    vpc_id="vpc-xxx",
    output_path="/path/to/output",
    format="png"
)

# Diagram specific VPC as SVG (scalable)
generate_architecture_diagram(
    vpc_id="vpc-xxx",
    output_path="/path/to/output",
    format="svg"
)

# Scan different region
scan_aws_architecture(region="eu-west-1")
```

## Troubleshooting

### "diagrams library not installed"
```bash
pip3 install diagrams graphviz
```

### "dot not found" error
```bash
brew install graphviz
```

### "No resources found"
- Check AWS credentials: `aws sts get-caller-identity`
- Verify region is correct
- Verify VPC ID exists: `aws ec2 describe-vpcs --region us-east-1`

### MCP server not appearing
1. Restart Claude Code
2. Check settings file: `~/.claude/settings.json` or project `.claude/settings.json`
3. Verify server path is correct

### Permission denied errors
Check IAM permissions include:
- `ec2:Describe*`
- `ecs:List*`, `ecs:Describe*`
- `eks:List*`, `eks:Describe*`
- `lambda:List*`
- `s3:List*`, `s3:GetBucketLocation`
- `rds:Describe*`
- `elasticfilesystem:Describe*`

## Resources

- **Server Code:** `~/.mcp-servers/aws-architecture-scanner/server.py`
- **Full Documentation:** `~/.mcp-servers/aws-architecture-scanner/README.md`
- **Examples:** `~/.mcp-servers/aws-architecture-scanner/EXAMPLES.md`
- **Settings:** `.claude/settings.json`

## Example Workflow

1. **Create infrastructure** (Terraform, CloudFormation, or manually)
2. **Scan** using `scan_aws_architecture()`
3. **Generate diagram** using `generate_architecture_diagram()`
4. **Review** the visual representation
5. **Document** by including diagram in docs/README
6. **Update** diagram after each infrastructure change
7. **Version control** diagrams alongside code

## Support

For issues or questions:
- Check README.md for detailed documentation
- Review EXAMPLES.md for usage patterns
- Verify AWS credentials and permissions
- Check Graphviz installation: `dot -V`

---

**You now have a powerful tool to automatically document your AWS infrastructure!**

Test it by generating a diagram of the VPC you just created with Terraform.
