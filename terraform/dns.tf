# DNS Configuration for sipsy.ai

# Cloud DNS zone for sipsy.ai
resource "google_dns_managed_zone" "formflow_zone" {
  name        = "formflow-zone"
  dns_name    = "${var.domain}."
  description = "DNS zone for FormFlow AI"
  
  dnssec_config {
    state = "on"
  }
}

# A record for root domain
resource "google_dns_record_set" "root" {
  name = google_dns_managed_zone.formflow_zone.dns_name
  type = "A"
  ttl  = 300

  managed_zone = google_dns_managed_zone.formflow_zone.name

  rrdatas = [google_compute_global_address.formflow_ip.address]
}

# A record for app subdomain
resource "google_dns_record_set" "app" {
  name = "app.${google_dns_managed_zone.formflow_zone.dns_name}"
  type = "A"
  ttl  = 300

  managed_zone = google_dns_managed_zone.formflow_zone.name

  rrdatas = [google_compute_global_address.formflow_ip.address]
}

# A record for API subdomain
resource "google_dns_record_set" "api" {
  name = "api.${google_dns_managed_zone.formflow_zone.dns_name}"
  type = "A"
  ttl  = 300

  managed_zone = google_dns_managed_zone.formflow_zone.name

  rrdatas = [google_compute_global_address.formflow_ip.address]
}

# A record for webhooks subdomain
resource "google_dns_record_set" "webhooks" {
  name = "webhooks.${google_dns_managed_zone.formflow_zone.dns_name}"
  type = "A"
  ttl  = 300

  managed_zone = google_dns_managed_zone.formflow_zone.name

  rrdatas = [google_compute_global_address.formflow_ip.address]
}

# CNAME record for www
resource "google_dns_record_set" "www" {
  name = "www.${google_dns_managed_zone.formflow_zone.dns_name}"
  type = "CNAME"
  ttl  = 300

  managed_zone = google_dns_managed_zone.formflow_zone.name

  rrdatas = [var.domain]
}