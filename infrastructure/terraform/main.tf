# Phase 191–200: Terraform for VM, firewall, and SA
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_instance" "ha_vm" {
  name         = "sterling-ha-vm"
  machine_type = "f1-micro"
  zone         = "${var.region}-a"
  boot_disk {
    initialize_params {
      image = "home-assistant-io/homeassistant-os-odroid-c4"
      size  = 20
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }
  tags = ["http-server","https-server"]
}
