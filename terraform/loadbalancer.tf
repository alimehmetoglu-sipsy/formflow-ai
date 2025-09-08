# Load Balancer and SSL Configuration for sipsy.ai

# Static IP address for the load balancer
resource "google_compute_global_address" "formflow_ip" {
  name = "formflow-lb-ip"
}

# SSL certificate for sipsy.ai domain
resource "google_compute_managed_ssl_certificate" "formflow_ssl" {
  name = "formflow-ssl-cert"

  managed {
    domains = [
      var.domain,
      "app.${var.domain}",
      "api.${var.domain}",
      "webhooks.${var.domain}"
    ]
  }
}

# Backend service for frontend (Next.js app)
resource "google_compute_backend_service" "frontend" {
  name        = "formflow-frontend-backend"
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }

  health_checks = [google_compute_health_check.frontend.id]
}

# Backend service for API (FastAPI backend)
resource "google_compute_backend_service" "backend" {
  name        = "formflow-backend-backend"
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.backend_neg.id
  }

  health_checks = [google_compute_health_check.backend.id]
}

# Network endpoint groups for Cloud Run services
resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  name                  = "formflow-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = "formflow-frontend"
  }
}

resource "google_compute_region_network_endpoint_group" "backend_neg" {
  name                  = "formflow-backend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = "formflow-backend"
  }
}

# Health checks
resource "google_compute_health_check" "frontend" {
  name = "formflow-frontend-health"

  http_health_check {
    request_path = "/"
    port         = "80"
  }
}

resource "google_compute_health_check" "backend" {
  name = "formflow-backend-health"

  http_health_check {
    request_path = "/health"
    port         = "80"
  }
}

# URL map for routing
resource "google_compute_url_map" "formflow" {
  name            = "formflow-lb"
  default_service = google_compute_backend_service.frontend.id

  host_rule {
    hosts        = ["api.${var.domain}", "webhooks.${var.domain}"]
    path_matcher = "backend"
  }

  host_rule {
    hosts        = [var.domain, "app.${var.domain}"]
    path_matcher = "frontend"
  }

  path_matcher {
    name            = "backend"
    default_service = google_compute_backend_service.backend.id
  }

  path_matcher {
    name            = "frontend"
    default_service = google_compute_backend_service.frontend.id
  }
}

# HTTPS proxy
resource "google_compute_target_https_proxy" "formflow" {
  name             = "formflow-https-proxy"
  url_map          = google_compute_url_map.formflow.id
  ssl_certificates = [google_compute_managed_ssl_certificate.formflow_ssl.id]
}

# HTTP proxy for redirect
resource "google_compute_target_http_proxy" "formflow_redirect" {
  name    = "formflow-http-proxy"
  url_map = google_compute_url_map.https_redirect.id
}

# URL map for HTTPS redirect
resource "google_compute_url_map" "https_redirect" {
  name = "formflow-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Forwarding rules
resource "google_compute_global_forwarding_rule" "https" {
  name       = "formflow-https-rule"
  target     = google_compute_target_https_proxy.formflow.id
  port_range = "443"
  ip_address = google_compute_global_address.formflow_ip.id
}

resource "google_compute_global_forwarding_rule" "http" {
  name       = "formflow-http-rule"
  target     = google_compute_target_http_proxy.formflow_redirect.id
  port_range = "80"
  ip_address = google_compute_global_address.formflow_ip.id
}

# Cloud Armor security policy
resource "google_compute_security_policy" "formflow_policy" {
  name        = "formflow-security-policy"
  description = "Security policy for FormFlow AI"

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "origin.region_code == 'CN' || origin.region_code == 'RU'"
      }
    }
    description = "Block traffic from certain countries"
  }

  rule {
    action   = "rate_based_ban"
    priority = "2000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limit per IP"
  }

  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }
}

# Apply security policy to backend service
resource "google_compute_backend_service_iam_binding" "backend_security" {
  service = google_compute_backend_service.backend.name
  role    = "roles/compute.securityAdmin"
  members = ["serviceAccount:formflow-backend@${var.project_id}.iam.gserviceaccount.com"]
}