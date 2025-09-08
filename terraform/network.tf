# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "formflow-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

# Subnet for Cloud Run and other services
resource "google_compute_subnetwork" "subnet" {
  name          = "formflow-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.1.0.0/24"
  }
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.2.0.0/20"
  }
  
  private_ip_google_access = true
}

# VPC Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "formflow-connector"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.vpc.name
  
  min_instances = 2
  max_instances = 10
  
  machine_type = "e2-micro"
}

# Cloud NAT for outbound internet access
resource "google_compute_router" "router" {
  name    = "formflow-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "formflow-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "formflow-allow-internal"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "icmp"
  }
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  source_ranges = [
    "10.0.0.0/8"
  ]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "formflow-allow-health-checks"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000", "3000"]
  }
  
  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22"
  ]
  
  target_tags = ["health-check"]
}