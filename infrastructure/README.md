# gem5 & Python Infrastructure Setup

This Terraform configuration automates the installation of gem5 and Python on a remote VM for running gem5 simulations.

## Prerequisites

1. **Terraform installed** on your local machine
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **SSH access** to your VM with username/password authentication enabled

3. **VM requirements**:
   - Ubuntu 20.04 or later
   - Sudo access for the user
   - At least 10GB free disk space
   - Internet connectivity

## Setup Instructions

### 1. Configure your VM credentials

Copy the example variables file and add your credentials:

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your actual VM details:

```hcl
vm_username = "your-username"
vm_address  = "192.168.1.100"  # or hostname
vm_password = "your-password"
```

**IMPORTANT**: Never commit `terraform.tfvars` to version control! It's already in `.gitignore`.

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the required providers.

### 3. Review the execution plan

```bash
terraform plan
```

This shows what Terraform will do without making changes.

### 4. Apply the configuration

```bash
terraform apply
```

Type `yes` when prompted. This will:
- Connect to your VM via SSH
- Update package lists
- Install Python 3.13 and dependencies
- Install build tools (gcc, g++, scons, m4)
- Install gem5 dependencies (protobuf, HDF5, libpng, etc.)
- Clone the gem5 repository
- Build gem5 for X86 architecture

**Note**: Building gem5 can take 30-60 minutes depending on your VM's CPU cores.

### 5. Verify installation

After successful completion, check the outputs:

```bash
terraform output
```

SSH into your VM and verify:

```bash
ssh your-username@vm-address
python3.13 --version
ls -la /opt/gem5/build/X86/
```

## Configuration Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `vm_username` | SSH username for the VM | - | Yes |
| `vm_address` | IP address or hostname | - | Yes |
| `vm_password` | SSH password | - | Yes |
| `ssh_port` | SSH port | 22 | No |
| `python_version` | Python version to install | 3.13 | No |
| `gem5_install_path` | gem5 installation directory | /opt/gem5 | No |

## What Gets Installed

### Python
- Python 3.13 (or specified version)
- Python development headers
- pip package manager
- venv module

### gem5 Dependencies
- Build tools: gcc, g++, scons, m4
- Protocol buffers (libprotobuf)
- Google Performance Tools (tcmalloc)
- HDF5 libraries
- PNG library
- zlib
- Boost libraries

### gem5
- Full gem5 source code (cloned from GitHub)
- X86 optimized build (`gem5.opt`)

## Troubleshooting

### Build fails
If gem5 build fails, you can manually complete it:

```bash
ssh your-username@vm-address
cd /opt/gem5
python3 $(which scons) build/X86/gem5.opt -j$(nproc)
```

### SSH connection timeout
- Verify VM is running and accessible
- Check firewall rules allow SSH
- Verify credentials are correct

### Permission denied
- Ensure user has sudo privileges
- Check SSH password authentication is enabled

## Cleanup

To remove the installation state from Terraform (does NOT delete files on VM):

```bash
terraform destroy
```

To actually remove gem5 from the VM:

```bash
ssh your-username@vm-address
sudo rm -rf /opt/gem5
```

## Security Notes

- Store `terraform.tfvars` securely
- Consider using SSH keys instead of passwords
- Restrict VM network access as appropriate
- Regularly update the VM and packages

## Next Steps

After installation, you can:
1. Copy your gem5 configuration scripts to the VM
2. Run simulations using `/opt/gem5/build/X86/gem5.opt`
3. Set up your workload files
4. Configure simulation parameters

## Support

For issues related to:
- **Terraform**: Check [Terraform documentation](https://www.terraform.io/docs)
- **gem5**: See [gem5 documentation](https://www.gem5.org/documentation/)
- **This setup**: Contact your system administrator