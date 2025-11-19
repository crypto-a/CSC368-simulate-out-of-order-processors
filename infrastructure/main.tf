resource "null_resource" "install_gem5_and_python" {
  # Trigger reinstallation if variables change
  triggers = {
    vm_address        = var.vm_address
    vm_username       = var.vm_username
    python_version    = var.python_version
    gem5_install_path = var.gem5_install_path
  }

  # Connection configuration
  connection {
    type     = "ssh"
    host     = var.vm_address
    user     = var.vm_username
    password = var.vm_password
    port     = var.ssh_port
    timeout  = "10m"
  }

  # Install Python and dependencies
  provisioner "remote-exec" {
    inline = [
      "echo '===== Starting installation ====='",
      "echo 'Updating package lists...'",
      "sudo apt-get update -y",

      "echo 'Installing Python ${var.python_version} and dependencies...'",
      "sudo apt-get install -y software-properties-common",
      "sudo add-apt-repository -y ppa:deadsnakes/ppa || true",
      "sudo apt-get update -y",
      "sudo apt-get install -y python${var.python_version} python${var.python_version}-dev python${var.python_version}-venv python3-pip",

      "echo 'Installing build tools and dependencies...'",
      "sudo apt-get install -y build-essential git scons gcc g++ m4",

      "echo 'Installing gem5 dependencies...'",
      "sudo apt-get install -y libprotobuf-dev protobuf-compiler",
      "sudo apt-get install -y libgoogle-perftools-dev",
      "sudo apt-get install -y libhdf5-dev libhdf5-serial-dev",
      "sudo apt-get install -y libpng-dev",
      "sudo apt-get install -y zlib1g-dev",
      "sudo apt-get install -y libboost-all-dev",

      "echo 'Creating gem5 installation directory...'",
      "sudo mkdir -p ${var.gem5_install_path}",
      "sudo chown $USER:$USER ${var.gem5_install_path}",

      "echo 'Cloning gem5 repository...'",
      "cd ${var.gem5_install_path}",
      "if [ ! -d '.git' ]; then",
      "  git clone https://github.com/gem5/gem5.git .",
      "else",
      "  echo 'gem5 repository already exists, pulling latest changes...'",
      "  git pull",
      "fi",

      "echo 'Building gem5 (this may take a while)...'",
      "echo '' | python3 $(which scons) build/X86/gem5.opt -j$(nproc) || echo 'Note: gem5 build may require manual intervention'",

      "echo '===== Cloning CSC368 simulation repository ====='",
      "cd ~",
      "if [ -d 'CSC368-simulate-out-of-order-processors' ]; then",
      "  echo 'Repository already exists, pulling latest changes...'",
      "  cd CSC368-simulate-out-of-order-processors",
      "  git pull",
      "else",
      "  echo 'Cloning repository...'",
      "  git clone https://github.com/crypto-a/CSC368-simulate-out-of-order-processors.git",
      "  cd CSC368-simulate-out-of-order-processors",
      "fi",

      "echo '===== Installing Python dependencies ====='",
      "python3 -m pip install --upgrade pip",
      "python3 -m pip install -r requirements.txt || echo 'Note: Some dependencies may have failed to install'",

      "echo '===== Installation completed ====='",
      "echo 'Verifying installations...'",
      "python${var.python_version} --version",
      "echo 'gem5 location: ${var.gem5_install_path}'",
      "ls -la ${var.gem5_install_path}/build/X86/ || echo 'gem5 build not found - may need manual build'",
      "echo 'Project location: ~/CSC368-simulate-out-of-order-processors'",
      "echo ''",
      "echo '===== To run simulations ====='",
      "echo 'cd ~/CSC368-simulate-out-of-order-processors'",
      "echo 'nice -n -10 python3 scripts/run_part4_sim.py'",
      "echo ''",
      "echo 'Note: The main script runs at higher priority (nice -n -10)'",
      "echo '      gem5 processes will run at normal/lower priority'"
    ]
  }

  # Copy simulation script
  provisioner "file" {
    source      = "${path.module}/../scripts/run-simulation.sh"
    destination = "/tmp/run-simulation.sh"
  }

  # Run simulation test
  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/run-simulation.sh",
      "GEM5_PATH=${var.gem5_install_path} /tmp/run-simulation.sh"
    ]
  }
}
