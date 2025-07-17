variable "project_id" {}
variable "region" {
  default = "us-central1"
}
variable "zone" {
  default = "us-central1-a"
}
variable "docker_image" {}

variable "run_sa_email" {}
variable "alert_email" {}
