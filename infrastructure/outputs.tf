output "vm_address" {
  description = "VM address used for installation"
  value       = var.vm_address
}

output "vm_username" {
  description = "VM username used for installation"
  value       = var.vm_username
  sensitive   = true
}

output "gem5_install_path" {
  description = "Path where gem5 is installed"
  value       = var.gem5_install_path
}

output "python_version" {
  description = "Python version installed"
  value       = var.python_version
}

output "installation_complete" {
  description = "Installation status"
  value       = "gem5 and Python installation completed on ${var.vm_address}"
}