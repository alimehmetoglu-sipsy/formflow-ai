# Monitoring, Logging & Observability Configuration

# Log buckets for structured logging
resource "google_logging_project_bucket_config" "formflow_logs" {
  project        = var.project_id
  location       = var.region
  retention_days = 30
  bucket_id      = "formflow-logs"
  description    = "FormFlow AI application logs"
}

# Log sink for application errors
resource "google_logging_project_sink" "error_sink" {
  name        = "formflow-error-sink"
  destination = "logging.googleapis.com/projects/${var.project_id}/locations/${var.region}/buckets/formflow-logs"
  
  filter = <<-EOT
    resource.type="cloud_run_revision"
    (resource.labels.service_name="formflow-backend" OR resource.labels.service_name="formflow-frontend")
    severity>=ERROR
  EOT

  unique_writer_identity = true
}

# Notification channel for alerts (email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "FormFlow Admin Email"
  type         = "email"
  
  labels = {
    email_address = var.admin_email
  }
}

# Notification channel for Discord webhook (optional)
resource "google_monitoring_notification_channel" "discord" {
  display_name = "FormFlow Discord"
  type         = "webhook_tokenauth"
  
  labels = {
    url = var.discord_webhook_url
  }
  
  sensitive_labels {
    auth_token = var.discord_webhook_token
  }

  # Only create if Discord webhook is provided
  count = var.discord_webhook_url != "" ? 1 : 0
}

# Uptime check for main application
resource "google_monitoring_uptime_check_config" "app_uptime" {
  display_name = "FormFlow App Uptime"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.domain
    }
  }
  
  selected_regions = ["EUROPE", "USA"]
}

# Uptime check for API
resource "google_monitoring_uptime_check_config" "api_uptime" {
  display_name = "FormFlow API Uptime"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/health"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "api.${var.domain}"
    }
  }
  
  selected_regions = ["EUROPE", "USA"]
}

# Alert policy for uptime failures
resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "FormFlow Uptime Alert"
  combiner     = "OR"
  
  conditions {
    display_name = "App Uptime Check"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" resource.type=\"uptime_url\" resource.label.host=\"${var.domain}\""
      duration        = "300s"
      comparison      = "COMPARISON_EQUAL"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }
  
  conditions {
    display_name = "API Uptime Check"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" resource.type=\"uptime_url\" resource.label.host=\"api.${var.domain}\""
      duration        = "300s"
      comparison      = "COMPARISON_EQUAL"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }
  
  notification_channels = concat(
    [google_monitoring_notification_channel.email.id],
    var.discord_webhook_url != "" ? [google_monitoring_notification_channel.discord[0].id] : []
  )
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert policy for high error rates
resource "google_monitoring_alert_policy" "error_rate_alert" {
  display_name = "FormFlow High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Backend Error Rate"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"formflow-backend\" metric.type=\"run.googleapis.com/request_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 10
      
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.labels.service_name"]
      }
    }
  }
  
  notification_channels = concat(
    [google_monitoring_notification_channel.email.id],
    var.discord_webhook_url != "" ? [google_monitoring_notification_channel.discord[0].id] : []
  )
}

# Alert policy for database connection issues
resource "google_monitoring_alert_policy" "database_alert" {
  display_name = "FormFlow Database Issues"
  combiner     = "OR"
  
  conditions {
    display_name = "Database CPU Usage"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" resource.labels.database_id=\"${var.project_id}:${google_sql_database_instance.postgres.name}\" metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  conditions {
    display_name = "Database Memory Usage"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" resource.labels.database_id=\"${var.project_id}:${google_sql_database_instance.postgres.name}\" metric.type=\"cloudsql.googleapis.com/database/memory/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.9
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Custom dashboard
resource "google_monitoring_dashboard" "formflow_dashboard" {
  dashboard_json = jsonencode({
    displayName = "FormFlow AI Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Run Request Count"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_count\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "Requests/sec"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "Cloud Run Response Latency"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_latencies\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_DELTA"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Latency (ms)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          yPos   = 4
          widget = {
            title = "Database Connections"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloudsql_database\" metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Connections"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 4
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" metric.type=\"logging.googleapis.com/log_entry_count\" metric.labels.severity=\"ERROR\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Errors/sec"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
}