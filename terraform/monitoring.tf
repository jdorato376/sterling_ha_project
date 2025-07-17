resource "google_monitoring_notification_channel" "email" {
  display_name = "Ops Email"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "router_errors" {
  display_name = "AI Router Error Rate"
  combiner     = "OR"
  notification_channels = [google_monitoring_notification_channel.email.id]

  conditions {
    display_name = "5xx errors"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"ai-router\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code=\"5xx\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1
    }
  }
}
