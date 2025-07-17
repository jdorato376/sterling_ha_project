resource "google_project_service" "vertex_ai" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
}

resource "google_cloud_run_v2_service" "ai_router" {
  name     = "ai-router"
  project  = var.project_id
  location = var.region

  template {
    containers {
      image = var.docker_image
      env {
        name  = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
    }
    service_account = var.run_sa_email
  }

  traffics {
    percent         = 100
    revision        = null
    type            = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}
