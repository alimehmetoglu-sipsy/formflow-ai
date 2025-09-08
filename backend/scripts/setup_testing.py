#!/usr/bin/env python3
"""
Setup script for testing FormFlow AI webhook integration
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Docker is not installed or not in PATH")
    return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is installed")
            return True
        else:
            # Try docker compose (newer syntax)
            result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker Compose is installed (new syntax)")
                return True
    except FileNotFoundError:
        pass
    
    print("❌ Docker Compose is not available")
    return False

def start_services():
    """Start Docker services"""
    print("🚀 Starting Docker services...")
    
    try:
        # Try new docker compose syntax first
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"],
            cwd="../",
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Fallback to old syntax
            result = subprocess.run(
                ["docker-compose", "up", "-d", "--build"],
                cwd="../", 
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            print("✅ Services started successfully")
            return True
        else:
            print(f"❌ Failed to start services: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting services: {str(e)}")
        return False

def wait_for_health():
    """Wait for services to become healthy"""
    print("⏳ Waiting for services to become healthy...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend service is healthy")
                
                # Check readiness
                response = requests.get("http://localhost:8000/api/v1/ready", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ready":
                        print("✅ All services are ready")
                        return True
                    else:
                        print(f"⏳ Services not ready yet: {data.get('errors', 'Unknown')}")
                
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}, waiting 5 seconds...")
            time.sleep(5)
    
    print("❌ Services did not become ready in time")
    return False

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = Path("../.env")
    env_example = Path("../.env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from .env.example...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created")
        print("💡 Edit .env file to add your API keys")
    else:
        print("✅ .env file already exists")

def test_api():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    endpoints = [
        ("Health Check", "http://localhost:8000/api/v1/health"),
        ("Readiness Check", "http://localhost:8000/api/v1/ready"),
        ("Webhook Test", "http://localhost:8000/api/v1/webhooks/test"),
        ("API Docs", "http://localhost:8000/docs")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {url}")
            else:
                print(f"⚠️ {name}: {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: {url} (Error: {str(e)})")

def setup_ngrok():
    """Setup ngrok for webhook testing"""
    print("\n🌐 Ngrok Setup Instructions:")
    print("1. Install ngrok: https://ngrok.com/download")
    print("2. Run: ngrok http 8000")
    print("3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
    print("4. Use this URL + '/api/v1/webhooks/typeform' as your webhook URL")
    print("5. Configure in Typeform webhook settings")
    
    ngrok_url = input("\n📝 Enter your ngrok URL (or press Enter to skip): ").strip()
    
    if ngrok_url:
        webhook_url = f"{ngrok_url}/api/v1/webhooks/typeform"
        print(f"\n🔗 Your webhook URL: {webhook_url}")
        
        # Test webhook
        test_webhook = input("🧪 Test webhook now? (y/n): ").strip().lower()
        if test_webhook == 'y':
            subprocess.run([sys.executable, "test_webhook.py", webhook_url])

def main():
    """Main setup function"""
    print("🚀 FormFlow AI Testing Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_docker():
        print("Please install Docker first: https://docs.docker.com/get-docker/")
        return
    
    if not check_docker_compose():
        print("Please install Docker Compose: https://docs.docker.com/compose/install/")
        return
    
    # Setup environment
    setup_environment()
    
    # Start services
    if not start_services():
        return
    
    # Wait for health
    if not wait_for_health():
        print("❌ Services are not healthy, check logs with: docker-compose logs")
        return
    
    # Test API
    test_api()
    
    # Ngrok setup
    setup_ngrok()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📚 Next steps:")
    print("1. Visit http://localhost:8000/docs for API documentation")
    print("2. Use test_webhook.py to test webhook integration")
    print("3. Configure your Typeform webhook with your ngrok URL")
    print("4. Check the logs with: docker-compose logs -f backend")

if __name__ == "__main__":
    main()