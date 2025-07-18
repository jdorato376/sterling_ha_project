# Sterling HA Project - Infrastructure as Code
# Phase 191–200: Terraform for VM, VPC, firewall, NAT, and service accounts

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

# VPC Network
resource "google_compute_network" "sterling_vpc" {
  name                    = "sterling-ha-vpc"
  auto_create_subnetworks = false
  description             = "VPC for Sterling HA Project"
}

# Subnet
resource "google_compute_subnetwork" "sterling_subnet" {
  name          = "sterling-ha-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.sterling_vpc.id
  
  private_ip_google_access = true
  description = "Subnet for Sterling HA instances"
}

# Cloud Router for NAT
resource "google_compute_router" "sterling_router" {
  name    = "sterling-ha-router"
  region  = var.region
  network = google_compute_network.sterling_vpc.id
  
  description = "Router for Sterling HA NAT gateway"
}

# Cloud NAT
resource "google_compute_router_nat" "sterling_nat" {
  name                               = "sterling-ha-nat"
  router                             = google_compute_router.sterling_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall Rules
resource "google_compute_firewall" "sterling_http" {
  name    = "sterling-ha-allow-http"
  network = google_compute_network.sterling_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["80", "8123"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["sterling-ha-http"]
  description   = "Allow HTTP traffic for Home Assistant"
}

resource "google_compute_firewall" "sterling_https" {
  name    = "sterling-ha-allow-https"
  network = google_compute_network.sterling_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["sterling-ha-https"]
  description   = "Allow HTTPS traffic"
}

resource "google_compute_firewall" "sterling_ssh" {
  name    = "sterling-ha-allow-ssh"
  network = google_compute_network.sterling_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["sterling-ha-ssh"]
  description   = "Allow SSH access"
}

# VM Instance with Shielded VM and Home Assistant OS
resource "google_compute_instance" "sterling_ha_vm" {
  name         = "sterling-ha-vm"
  machine_type = "e2-medium"
  zone         = var.zone
  
  tags = ["sterling-ha-http", "sterling-ha-https", "sterling-ha-ssh"]
  
  boot_disk {
    initialize_params {
      # Note: HAOS image would need to be imported first
      image = "projects/cos-cloud/global/images/family/cos-stable"
      size  = 32
      type  = "pd-standard"
    }
  }
  
  network_interface {
    network    = google_compute_network.sterling_vpc.name
    subnetwork = google_compute_subnetwork.sterling_subnet.name
    
    # Remove external IP for private instance
    # access_config {} # Uncomment for external IP
  }
  
  # Shielded VM configuration
  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
  
  metadata = {
    enable-oslogin = "TRUE"
  }
  
  metadata_startup_script = <<-EOF
    #!/bin/bash
    # Placeholder for Home Assistant OS setup
    echo "Sterling HA VM started" > /var/log/sterling-startup.log
  EOF
  
  service_account {
    email  = google_service_account.sterling_sa.email
    scopes = ["cloud-platform"]
  }
  
  labels = {
    project = "sterling-ha"
    purpose = "home-assistant"
  }
}

# Service Account for the VM
resource "google_service_account" "sterling_sa" {
  account_id   = "sterling-ha-vm-sa"
  display_name = "Sterling HA VM Service Account"
  description  = "Service account for Sterling HA VM"
}

# IAM bindings for the service account
resource "google_project_iam_member" "sterling_sa_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.sterling_sa.email}"
}

resource "google_project_iam_member" "sterling_sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.sterling_sa.email}"
}

# Load Balancer (optional)
resource "google_compute_global_address" "sterling_lb_ip" {
  name        = "sterling-ha-lb-ip"
  description = "Static IP for Sterling HA Load Balancer"
}

# Outputs
output "vpc_name" {
  value = google_compute_network.sterling_vpc.name
}

output "subnet_name" {
  value = google_compute_subnetwork.sterling_subnet.name
}

output "vm_name" {
  value = google_compute_instance.sterling_ha_vm.name
}

output "vm_internal_ip" {
  value = google_compute_instance.sterling_ha_vm.network_interface[0].network_ip
}

output "service_account_email" {
  value = google_service_account.sterling_sa.email
}

output "load_balancer_ip" {
  value = google_compute_global_address.sterling_lb_ip.address
}
