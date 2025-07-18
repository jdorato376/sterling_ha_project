# Sterling HA Project - Comprehensive GCP Infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
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

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "bigquery.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "sterling_vpc" {
  name                    = "sterling-ha-vpc"
  auto_create_subnetworks = false
  depends_on             = [google_project_service.required_apis]
}

# Subnet
resource "google_compute_subnetwork" "sterling_subnet" {
  name          = "sterling-ha-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.sterling_vpc.id
  
  private_ip_google_access = true
}

# Cloud Router
resource "google_compute_router" "sterling_router" {
  name    = "sterling-ha-router"
  region  = var.region
  network = google_compute_network.sterling_vpc.id
}

# Cloud NAT
resource "google_compute_router_nat" "sterling_nat" {
  name                               = "sterling-ha-nat"
  router                             = google_compute_router.sterling_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Firewall rules
resource "google_compute_firewall" "sterling_firewall_internal" {
  name    = "sterling-ha-firewall-internal"
  network = google_compute_network.sterling_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8123"]
  }

  source_ranges = ["10.0.1.0/24"]
  target_tags   = ["sterling-ha"]
}

resource "google_compute_firewall" "sterling_firewall_external" {
  name    = "sterling-ha-firewall-external"
  network = google_compute_network.sterling_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8123"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["sterling-ha", "http-server", "https-server"]
}

# Service Account
resource "google_service_account" "sterling_sa" {
  account_id   = "sterling-ha-sa"
  display_name = "Sterling HA Service Account"
  description  = "Service account for Sterling HA VM and services"
}

# IAM bindings for service account
resource "google_project_iam_member" "sterling_sa_roles" {
  for_each = toset([
    "roles/compute.instanceAdmin.v1",
    "roles/aiplatform.user",
    "roles/artifactregistry.reader",
    "roles/cloudbuild.builds.editor",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/bigquery.dataViewer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.sterling_sa.email}"
}

# VM Instance with Shielded VM
resource "google_compute_instance" "ha_vm" {
  name         = "sterling-ha-vm"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = google_compute_network.sterling_vpc.name
    subnetwork = google_compute_subnetwork.sterling_subnet.name
    # No external IP - will use Cloud NAT
  }

  # Shielded VM configuration
  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  service_account {
    email  = google_service_account.sterling_sa.email
    scopes = ["cloud-platform"]
  }

  tags = ["sterling-ha", "http-server", "https-server"]

  metadata_startup_script = <<-EOF
    #!/bin/bash
    # Update system
    apt-get update
    apt-get install -y docker.io docker-compose python3 python3-pip git
    
    # Install Home Assistant OS (placeholder - would need actual HAOS setup)
    systemctl enable docker
    systemctl start docker
    
    # Pull and run Sterling HA container
    docker pull gcr.io/${var.project_id}/sterling-ha-addon:latest || true
    
    # Setup monitoring agent
    curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
    bash add-google-cloud-ops-agent-repo.sh --also-install
  EOF

  depends_on = [
    google_compute_subnetwork.sterling_subnet,
    google_service_account.sterling_sa
  ]
}

# Load Balancer
resource "google_compute_global_address" "sterling_lb_ip" {
  name = "sterling-ha-lb-ip"
}

resource "google_compute_health_check" "sterling_health_check" {
  name = "sterling-ha-health-check"

  http_health_check {
    port         = 8123
    request_path = "/"
  }
}

resource "google_compute_backend_service" "sterling_backend" {
  name        = "sterling-ha-backend"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10

  health_checks = [google_compute_health_check.sterling_health_check.id]

  backend {
    group = google_compute_instance_group.sterling_ig.id
  }
}

resource "google_compute_instance_group" "sterling_ig" {
  name = "sterling-ha-ig"
  zone = var.zone

  instances = [google_compute_instance.ha_vm.id]

  named_port {
    name = "http"
    port = 8123
  }
}

# Artifact Registry
resource "google_artifact_registry_repository" "sterling_repo" {
  repository_id = "sterling-ha-repo"
  location      = var.region
  format        = "DOCKER"
  description   = "Sterling HA Docker images"
  
  depends_on = [google_project_service.required_apis]
}

# BigQuery dataset for billing and analytics
resource "google_bigquery_dataset" "sterling_analytics" {
  dataset_id  = "sterling_ha_analytics"
  location    = var.region
  description = "Sterling HA analytics and billing data"
  
  depends_on = [google_project_service.required_apis]
}

# Outputs
output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.sterling_vpc.name
}

output "vm_external_ip" {
  description = "External IP of the VM"
  value       = google_compute_global_address.sterling_lb_ip.address
}

output "service_account_email" {
  description = "Email of the service account"
  value       = google_service_account.sterling_sa.email
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.sterling_repo.name
}
