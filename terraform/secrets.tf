# Secret Manager for sensitive data

# Database password secret
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# OpenAI API key secret
resource "google_secret_manager_secret" "openai_key" {
  secret_id = "openai-api-key"
  
  replication {
    auto {}
  }
}

# LemonSqueezy API key secret
resource "google_secret_manager_secret" "lemonsqueezy_key" {
  secret_id = "lemonsqueezy-api-key"
  
  replication {
    auto {}
  }
}

# Resend API key secret
resource "google_secret_manager_secret" "resend_key" {
  secret_id = "resend-api-key"
  
  replication {
    auto {}
  }
}

# JWT Secret key
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-key"
  
  replication {
    auto {}
  }
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

# Typeform webhook secret
resource "google_secret_manager_secret" "typeform_webhook_secret" {
  secret_id = "typeform-webhook-secret"
  
  replication {
    auto {}
  }
}

# GitHub token for Cloud Build
resource "google_secret_manager_secret" "github_token" {
  secret_id = "github-token"
  
  replication {
    auto {}
  }
}

# Database connection string
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "db-connection-string"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret = google_secret_manager_secret.db_connection_string.id
  secret_data = "postgresql://formflow:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}/formflow?sslmode=require"
}

# Grant Cloud Run service account access to secrets
resource "google_secret_manager_secret_iam_member" "backend_secrets" {
  for_each = toset([
    google_secret_manager_secret.db_password.id,
    google_secret_manager_secret.openai_key.id,
    google_secret_manager_secret.lemonsqueezy_key.id,
    google_secret_manager_secret.resend_key.id,
    google_secret_manager_secret.jwt_secret.id,
    google_secret_manager_secret.typeform_webhook_secret.id,
    google_secret_manager_secret.db_connection_string.id
  ])
  
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:formflow-backend@${var.project_id}.iam.gserviceaccount.com"
}