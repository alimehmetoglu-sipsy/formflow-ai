# Cloud SQL (PostgreSQL) Instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_id}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier              = "db-f1-micro"  # Start small, can scale later
    availability_type = "ZONAL"        # Change to REGIONAL for HA in production
    disk_type         = "PD_SSD"
    disk_size         = 10
    disk_autoresize   = true
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc.id
      
      authorized_networks {
        name  = "cloud-run"
        value = "0.0.0.0/0"  # Will restrict this later with Cloud Run
      }
    }
    
    backup_configuration {
      enabled                        = true
      start_time                    = "03:00"
      location                      = var.region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }
    
    database_flags {
      name  = "max_connections"
      value = "100"
    }
    
    database_flags {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
    
    maintenance_window {
      day          = 7  # Sunday
      hour         = 4  # 4 AM
      update_track = "stable"
    }
  }
  
  deletion_protection = true
}

# Database
resource "google_sql_database" "formflow_db" {
  name     = "formflow"
  instance = google_sql_database_instance.postgres.name
}

# Database User
resource "google_sql_user" "formflow_user" {
  name     = "formflow"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

# Generate secure random password
resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Redis Instance (Memorystore)
resource "google_redis_instance" "cache" {
  name           = "${var.project_id}-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  
  redis_version = "REDIS_7_0"
  display_name  = "FormFlow Cache"
  
  authorized_network = google_compute_network.vpc.id
  connect_mode      = "PRIVATE_SERVICE_ACCESS"
  
  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }
}

# Private Service Access for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}