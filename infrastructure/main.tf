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

      "echo 'Installing Python and dependencies...'",
      "sudo apt-get install -y software-properties-common",
      "sudo apt-get install -y python3 python3-dev python3-venv python3-pip",

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
      "python3 -m pip install --upgrade pip --break-system-packages",
      "cd ~/CSC368-simulate-out-of-order-processors && python3 -m pip install -r requirements.txt --break-system-packages || echo 'Note: Some dependencies may have failed to install'",

      "echo '===== Setting up workloads ====='",
      "cd ~/CSC368-simulate-out-of-order-processors && chmod +x infrastructure/setup_workloads.sh",
      "cd ~/CSC368-simulate-out-of-order-processors && bash infrastructure/setup_workloads.sh",

      "echo '===== Installation completed ====='",
      "echo 'Verifying installations...'",
      "python3 --version",
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

  # Run Part 4 simulations with automatic option selection
  provisioner "remote-exec" {
    inline = [
      "echo '===== Running Part 4 Simulations ====='",
      "cd ~/CSC368-simulate-out-of-order-processors",
      "echo 'Starting simulations with nice priority...'",
      "echo 'This will run all 36 simulations (4 at a time)...'",

      "# Use nohup to prevent disconnection issues and echo 1 to select option 1 (all simulations)",
      "nohup nice -n -10 bash -c 'echo 1 | python3 scripts/run_part4_sim.py > /tmp/part4_sim.log 2>&1' &",
      "echo \"Simulations started in background\"",
      "echo \"Monitor progress: tail -f ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt\"",
      "echo \"Check status: cat ~/CSC368-simulate-out-of-order-processors/data/part4/status.json\"",
      "sleep 2",
      "",
      "# Wait for simulations to complete (check if master_log contains 'All simulations complete')",
      "echo 'Waiting for simulations to complete...'",
      "echo 'This may take 1-4 hours depending on your VM performance...'",
      "",
      "# Wait with a timeout and better status checking",
      "export WAIT_TIME=0",
      "export MAX_WAIT=14400",
      "while [ $$WAIT_TIME -lt $$MAX_WAIT ]; do",
      "  if grep -q 'All simulations complete' ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt 2>/dev/null; then",
      "    echo 'Simulations completed successfully!'",
      "    cat ~/CSC368-simulate-out-of-order-processors/data/part4/status.json 2>/dev/null | grep -E '\"(completed|failed)\"' || true",
      "    break",
      "  fi",
      "  sleep 30",
      "  export WAIT_TIME=`expr $$WAIT_TIME + 30`",
      "  COMPLETED=`grep -c 'COMPLETED:' ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt 2>/dev/null || echo 0`",
      "  echo \"Progress: $$COMPLETED completed (waited $${WAIT_TIME}s of $${MAX_WAIT}s max)\"",
      "done",

      "if [ $$WAIT_TIME -ge $$MAX_WAIT ]; then",
      "  echo 'Timeout reached after 4 hours - simulations may still be running'",
      "  echo 'You can check status with: ./scripts/check_status.sh'",
      "  echo 'And retrieve data manually with: ./scripts/retrieve_data.sh'",
      "fi",

      "echo '===== Simulations finished or timeout reached ====='",

      "# Try to retrieve data immediately if completed",
      "if grep -q 'All simulations complete' ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt 2>/dev/null; then",
      "  echo 'Data is ready for retrieval'",
      "  echo 'Files created:'",
      "  find ~/CSC368-simulate-out-of-order-processors/data/part4 -name 'stats.txt' | wc -l | xargs echo 'Stats files:'",
      "else",
      "  echo 'Simulations may still be running in background'",
      "fi"
    ]
  }

  # Copy data retrieval script to VM for optional use
  provisioner "file" {
    source      = "${path.module}/../scripts/retrieve_data.sh"
    destination = "/tmp/retrieve_data_vm.sh"
  }

  # Final attempt to retrieve data
  provisioner "local-exec" {
    command = <<-EOT
      echo "Attempting to retrieve simulation data..."

      # Check if simulations are complete on VM
      if ssh -p ${var.ssh_port} ${var.vm_username}@${var.vm_address} \
         "grep -q 'All simulations complete' ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt 2>/dev/null"; then
        echo "Simulations confirmed complete, retrieving data..."
        ${path.module}/../scripts/retrieve_data.sh
      else
        echo "================================================="
        echo "Simulations may still be running on the VM"
        echo ""
        echo "To check status later:"
        echo "  VM_USER=${var.vm_username} VM_HOST=${var.vm_address} ./scripts/check_status.sh"
        echo ""
        echo "To retrieve data when complete:"
        echo "  VM_USER=${var.vm_username} VM_HOST=${var.vm_address} ./scripts/retrieve_data.sh"
        echo "================================================="
      fi
    EOT

    environment = {
      VM_USER         = var.vm_username
      VM_HOST         = var.vm_address
      VM_PASSWORD     = var.vm_password
      SSH_PORT        = var.ssh_port
      REMOTE_DATA_DIR = "~/CSC368-simulate-out-of-order-processors/data/part4"
      LOCAL_DATA_DIR  = "${path.module}/../data/part4"
    }
  }
}
