# Cloud Storage Buckets

# Static assets bucket
resource "google_storage_bucket" "static" {
  name          = "${var.project_id}-static-assets"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["https://${var.domain}", "https://app.${var.domain}"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  versioning {
    enabled = true
  }
}

# Backup bucket
resource "google_storage_bucket" "backups" {
  name          = "${var.project_id}-backups"
  location      = var.region
  storage_class = "NEARLINE"
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
  
  versioning {
    enabled = true
  }
}

# Uploads bucket for user files
resource "google_storage_bucket" "uploads" {
  name          = "${var.project_id}-uploads"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["https://${var.domain}", "https://app.${var.domain}"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  versioning {
    enabled = true
  }
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "formflow-images"
  format        = "DOCKER"
  
  description = "Docker images for FormFlow AI"
  
  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    
    most_recent_versions {
      keep_count = 10
    }
  }
  
  cleanup_policies {
    id     = "delete-old-versions"
    action = "DELETE"
    
    condition {
      older_than = "2592000s" # 30 days
    }
  }
}