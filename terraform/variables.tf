variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "formflow-ai-prod"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "europe-west1-b"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "domain" {
  description = "Primary domain"
  type        = string
  default     = "sipsy.ai"
}

variable "admin_email" {
  description = "Admin email for monitoring alerts"
  type        = string
  default     = "admin@sipsy.ai"
}

variable "discord_webhook_url" {
  description = "Discord webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "discord_webhook_token" {
  description = "Discord webhook token for authentication"
  type        = string
  default     = ""
  sensitive   = true
}

variable "github_app_installation_id" {
  description = "GitHub App installation ID for Cloud Build"
  type        = string
  default     = ""
}