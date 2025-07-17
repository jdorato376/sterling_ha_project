provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_cloud_run_v2_service" "ai_router" {
  name     = "ai-router"
  location = var.region

  template {
    containers {
      image = var.docker_image
      ports {
        container_port = 8080
      }
    }
  }
}

resource "google_artifact_registry_repository" "docker_repo" {
  format        = "DOCKER"
  location      = var.region
  repository_id = "ai-router-images"
}
