# Quick Start Guide - Docker Setup

This guide will help you get up and running with the gem5 development environment using Docker.

## Prerequisites

- **Docker Desktop** installed and running
  - macOS: Download from https://www.docker.com/products/docker-desktop/
  - Linux: `sudo apt-get install docker.io docker-compose`
  - Windows: Download Docker Desktop for Windows

- **Docker Compose** (included with Docker Desktop)

## Method 1: Using Docker Compose (Recommended)

This is the easiest way to get started!

### Step 1: Start the Container

```bash
# Navigate to the project directory
cd /Users/ali/Documents/Documents/Projects.nosync/CSC368-simulate-out-of-order-processors

# Start the container
docker compose up
```

The first time you run this, it will:
- Download Ubuntu 24.04 image
- Install Terraform
- Set up SSH server
- Install Python and development tools
- Display ready message

**Keep this terminal window open** - the container runs here.

### Step 2: Access the Container

Open a **new terminal** and run:

```bash
# Access the container shell
docker exec -it csc368-gem5-dev bash
```

You're now inside the container!

### Step 3: Test Terraform

Inside the container:

```bash
# Check Terraform is installed
terraform --version

# Navigate to infrastructure
cd infrastructure

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit for local testing
nano terraform.tfvars
# or
vi terraform.tfvars
```

Edit the file to contain:
```hcl
vm_username = "root"
vm_address  = "localhost"
vm_password = "gem5pass"
```

### Step 4: Install gem5

Still inside the container:

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply (install gem5)
terraform apply
```

Type `yes` when prompted. This will install gem5 at `/opt/gem5`.

### Step 5: Stop the Container

When you're done:

```bash
# Exit the container shell
exit

# Stop the container (in the terminal running docker compose)
# Press Ctrl+C, then:
docker compose down
```

## Method 2: Using VS Code DevContainer

If you prefer VS Code:

### Step 1: Install VS Code Extension

1. Open VS Code
2. Install the **Dev Containers** extension
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Search for "Dev Containers"
   - Install by Microsoft

### Step 2: Open Project

```bash
# Open the project in VS Code
code /Users/ali/Documents/Documents/Projects.nosync/CSC368-simulate-out-of-order-processors
```

### Step 3: Reopen in Container

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: **"Dev Containers: Reopen in Container"**
3. Press Enter
4. Wait for container to build and start

### Step 4: Use the Terminal

VS Code will open a terminal **inside the container** automatically. You can now run Terraform commands directly!

## Method 3: SSH into the Container

If you want to SSH into the running container:

```bash
# Start the container (if not already running)
docker compose up -d  # -d runs in background

# SSH from your host machine
ssh root@localhost -p 2222
# Password: gem5pass
```

## Common Docker Commands

```bash
# Start container in background
docker compose up -d

# View logs
docker compose logs -f

# Stop container
docker compose down

# Restart container
docker compose restart

# Remove container and volumes (clean slate)
docker compose down -v

# Check if container is running
docker ps

# Access container shell
docker exec -it csc368-gem5-dev bash

# Run a single command in container
docker exec csc368-gem5-dev terraform --version
```

## Persistent Data

The docker-compose setup includes:
- **Project files:** Mounted at `/workspace` (changes are saved to your local machine)
- **gem5 installation:** Stored in Docker volume `gem5-build` (persists between container restarts)

## Troubleshooting

### Port Already in Use

If port 2222 is already in use, edit `docker-compose.yml`:

```yaml
ports:
  - "2223:22"  # Change 2222 to any other port
```

### Container Won't Start

```bash
# Check Docker is running
docker info

# Remove old containers
docker compose down
docker system prune -a

# Try again
docker compose up
```

### Can't Access Files

```bash
# Check volume mounts
docker exec -it csc368-gem5-dev ls -la /workspace

# Verify you're in the right directory
pwd
```

### SSH Connection Refused

```bash
# Check SSH service inside container
docker exec -it csc368-gem5-dev service ssh status

# Restart SSH
docker exec -it csc368-gem5-dev service ssh restart
```

### Terraform Errors

```bash
# Inside the container, clean Terraform state
cd /workspace/infrastructure
rm -rf .terraform
terraform init
```

## What's Next?

Once gem5 is installed:

1. **Create simulation configs** in `configs/`
2. **Add workloads** to `workloads/`
3. **Run simulations:**
   ```bash
   /opt/gem5/build/X86/gem5.opt \
     --outdir=results/test_sim \
     configs/your_config.py
   ```

4. **Analyze results:**
   ```bash
   cat results/test_sim/stats.txt
   ```

## Tips

- **Keep the container running** while developing
- **Use docker exec** to open multiple terminals in the same container
- **Commit your work** regularly - changes in `/workspace` are saved
- **Don't commit** `terraform.tfvars` - it's in `.gitignore`

## Need Help?

- Docker issues: Check Docker Desktop logs
- Terraform issues: Run `terraform init` and `terraform plan`
- gem5 issues: See https://www.gem5.org/documentation/
- Container setup: Check `.devcontainer/setup.sh` logs

Happy simulating!