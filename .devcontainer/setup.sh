#!/bin/bash
set -e

echo "========================================================================"
echo "  CSC368 gem5 Development & Simulation Container Setup"
echo "========================================================================"

# Update package list
export DEBIAN_FRONTEND=noninteractive
apt-get update

# Install SSH server first
echo "Installing SSH server..."
apt-get install -y openssh-server sudo

# Configure SSH for password authentication
mkdir -p /var/run/sshd
echo "root:gem5pass" | chpasswd
echo "vscode:gem5pass" | chpasswd || true

# Enable password authentication
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config || true
sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config || true
sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config || true
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config || true
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

# Start SSH service
service ssh start || /usr/sbin/sshd

# Install basic development tools
echo "Installing development tools..."
apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    vim \
    curl \
    wget \
    htop \
    tree \
    net-tools

# Install Python and tools
echo "Installing Python..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python-is-python3

# Install useful Python packages
pip3 install --break-system-packages numpy matplotlib pandas || pip3 install numpy matplotlib pandas

# Ensure SSH starts on container start
echo "#!/bin/bash" > /usr/local/bin/start-ssh.sh
echo "service ssh start 2>/dev/null || /usr/sbin/sshd" >> /usr/local/bin/start-ssh.sh
chmod +x /usr/local/bin/start-ssh.sh

# Add to bashrc to auto-start SSH
echo "/usr/local/bin/start-ssh.sh 2>/dev/null" >> /root/.bashrc

echo ""
echo "========================================================================"
echo "  Container Setup Complete!"
echo "========================================================================"
echo ""
echo "Platform: $(uname -m)"
echo "SSH Server: Running on port 22"
echo "Root password: gem5pass"
echo ""
echo "To connect Terraform to this container:"
echo "  1. From inside this container:"
echo "     cd terraform"
echo "     cp terraform.tfvars.example terraform.tfvars"
echo '     Edit: vm_host = "localhost"'
echo '           vm_user = "root"'
echo '           vm_password = "gem5pass"'
echo "     terraform init"
echo "     terraform apply"
echo ""
echo "  2. Container will install gem5 and run simulations locally!"
echo ""
echo "Quick commands:"
echo "  - Test terraform: cd terraform && terraform --version"
echo "  - Check SSH: service ssh status"
echo "  - Run terraform: cd terraform && terraform apply"
echo ""
echo "========================================================================"
