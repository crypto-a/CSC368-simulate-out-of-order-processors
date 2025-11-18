variable "vm_username" {
  description = "SSH username for the VM"
  type        = string
  sensitive   = true
}

variable "vm_address" {
  description = "IP address or hostname of the VM"
  type        = string
}

variable "vm_password" {
  description = "SSH password for the VM"
  type        = string
  sensitive   = true
}

variable "ssh_port" {
  description = "SSH port for the VM"
  type        = number
  default     = 22
}

variable "python_version" {
  description = "Python version to install"
  type        = string
  default     = "3.13"
}

variable "gem5_install_path" {
  description = "Path where gem5 will be installed"
  type        = string
  default     = "/opt/gem5"
}