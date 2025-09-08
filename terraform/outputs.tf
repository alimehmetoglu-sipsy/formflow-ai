# Terraform Outputs

output "project_id" {
  value       = var.project_id
  description = "GCP Project ID"
}

output "region" {
  value       = var.region
  description = "GCP Region"
}

output "vpc_connector" {
  value       = google_vpc_access_connector.connector.name
  description = "VPC Connector for Cloud Run"
}

output "vpc_connector_id" {
  value       = google_vpc_access_connector.connector.id
  description = "VPC Connector full ID"
}

output "db_instance_name" {
  value       = google_sql_database_instance.postgres.name
  description = "Cloud SQL instance name"
}

output "db_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL connection name for Cloud Run"
}

output "db_private_ip" {
  value       = google_sql_database_instance.postgres.private_ip_address
  description = "Cloud SQL private IP address"
  sensitive   = true
}

output "redis_host" {
  value       = google_redis_instance.cache.host
  description = "Redis host address"
  sensitive   = true
}

output "redis_port" {
  value       = google_redis_instance.cache.port
  description = "Redis port"
}

output "static_bucket" {
  value       = google_storage_bucket.static.url
  description = "Static assets bucket URL"
}

output "uploads_bucket" {
  value       = google_storage_bucket.uploads.url
  description = "User uploads bucket URL"
}

output "backups_bucket" {
  value       = google_storage_bucket.backups.url
  description = "Backups bucket URL"
}

output "artifact_registry" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
  description = "Artifact Registry URL for Docker images"
}

output "backend_service_account" {
  value       = "formflow-backend@${var.project_id}.iam.gserviceaccount.com"
  description = "Backend service account email"
}

output "deployer_service_account" {
  value       = "formflow-deployer@${var.project_id}.iam.gserviceaccount.com"
  description = "Deployer service account email"
}

output "secret_ids" {
  value = {
    db_password              = google_secret_manager_secret.db_password.secret_id
    openai_key              = google_secret_manager_secret.openai_key.secret_id
    lemonsqueezy_key        = google_secret_manager_secret.lemonsqueezy_key.secret_id
    resend_key              = google_secret_manager_secret.resend_key.secret_id
    jwt_secret              = google_secret_manager_secret.jwt_secret.secret_id
    typeform_webhook_secret = google_secret_manager_secret.typeform_webhook_secret.secret_id
    db_connection_string    = google_secret_manager_secret.db_connection_string.secret_id
  }
  description = "Secret Manager secret IDs"
}

# Load Balancer outputs
output "load_balancer_ip" {
  value       = google_compute_global_address.formflow_ip.address
  description = "Load balancer IP address"
}

output "ssl_certificate_status" {
  value       = google_compute_managed_ssl_certificate.formflow_ssl.managed[0].status
  description = "SSL certificate provisioning status"
}

output "nameservers" {
  value       = google_dns_managed_zone.formflow_zone.name_servers
  description = "DNS nameservers to configure at domain registrar"
}

output "dns_zone_name" {
  value       = google_dns_managed_zone.formflow_zone.name
  description = "Cloud DNS zone name"
}

output "setup_instructions" {
  value = <<-EOT
    
    ========================================
    FormFlow AI - Infrastructure Created
    ========================================
    
    Load Balancer IP: ${google_compute_global_address.formflow_ip.address}
    DNS Zone: ${google_dns_managed_zone.formflow_zone.dns_name}
    
    Next Steps:
    
    1. Configure DNS at your domain registrar (GoDaddy):
       Update nameservers to:
       ${join("\n       ", google_dns_managed_zone.formflow_zone.name_servers)}
    
    2. Add API keys to Secret Manager:
       - OpenAI API Key
       - LemonSqueezy API Key
       - Resend API Key
       - Typeform Webhook Secret
    
    3. Build and push Docker images:
       docker build -t ${var.region}-docker.pkg.dev/${var.project_id}/formflow-images/backend:latest ./backend
       docker build -t ${var.region}-docker.pkg.dev/${var.project_id}/formflow-images/frontend:latest ./frontend
       
       docker push ${var.region}-docker.pkg.dev/${var.project_id}/formflow-images/backend:latest
       docker push ${var.region}-docker.pkg.dev/${var.project_id}/formflow-images/frontend:latest
    
    4. Deploy to Cloud Run:
       Use the deployment scripts in /scripts directory
    
    5. SSL Certificate will auto-provision after DNS propagation
    
    Domains configured:
    - https://${var.domain} → Frontend
    - https://app.${var.domain} → Frontend  
    - https://api.${var.domain} → Backend
    - https://webhooks.${var.domain} → Backend
    
    ========================================
  EOT
}