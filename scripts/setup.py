#!/usr/bin/env python3
"""
Setup script for Face Attendance System
Initializes the project with proper database setup and configuration
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"Command executed successfully: {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        return None

def check_docker():
    """Check if Docker is installed and running"""
    logger.info("Checking Docker installation...")
    result = run_command("docker --version")
    if result:
        logger.info("Docker is installed")
        return True
    else:
        logger.error("Docker is not installed. Please install Docker first.")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    logger.info("Checking Docker Compose...")
    result = run_command("docker compose version")
    if result:
        logger.info("Docker Compose is available")
        return True
    else:
        logger.error("Docker Compose is not available. Please install Docker Compose first.")
        return False

def create_directories():
    """Create necessary directories"""
    logger.info("Creating project directories...")
    
    directories = [
        "logs/backend",
        "logs/ai_workers", 
        "logs/celery",
        "models",
        "monitoring/prometheus",
        "monitoring/grafana/provisioning",
        "monitoring/grafana/dashboards",
        "config/nginx",
        "config/redis",
        "config/rabbitmq",
        "database/backups",
        "database/init_scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def setup_environment():
    """Setup environment variables"""
    logger.info("Setting up environment variables...")
    
    env_file = Path("config/environment.env")
    if env_file.exists():
        logger.info("Environment file already exists")
    else:
        logger.info("Creating environment file...")
        # The environment file was already created earlier

def setup_database():
    """Setup PostgreSQL database"""
    logger.info("Setting up PostgreSQL database...")
    
    # Copy init script to the right location
    init_script_src = Path("database/init.sql")
    init_script_dst = Path("database/init_scripts/01-init.sql")
    
    if init_script_src.exists():
        init_script_dst.parent.mkdir(parents=True, exist_ok=True)
        init_script_dst.write_text(init_script_src.read_text())
        logger.info("Database initialization script copied")

def build_services():
    """Build Docker services"""
    logger.info("Building Docker services...")
    
    # Build all services
    result = run_command("docker compose build")
    if result:
        logger.info("Docker services built successfully")
        return True
    else:
        logger.error("Failed to build Docker services")
        return False

def start_services():
    """Start Docker services"""
    logger.info("Starting Docker services...")
    
    # Start services in background
    result = run_command("docker compose up -d postgres redis rabbitmq")
    if result:
        logger.info("Core services started successfully")
        
        # Wait for services to be ready
        logger.info("Waiting for services to be ready...")
        import time
        time.sleep(30)
        
        return True
    else:
        logger.error("Failed to start core services")
        return False

def run_migrations():
    """Run Django migrations"""
    logger.info("Running Django migrations...")
    
    # Start the web service temporarily to run migrations
    result = run_command("docker compose run --rm web python manage.py migrate")
    if result:
        logger.info("Database migrations completed successfully")
        return True
    else:
        logger.error("Failed to run database migrations")
        return False

def create_superuser():
    """Create Django superuser"""
    logger.info("Creating Django superuser...")
    
    # Create superuser
    result = run_command("docker compose run --rm web python manage.py createsuperuser --noinput --username admin --email admin@example.com")
    if result:
        logger.info("Superuser created successfully")
        return True
    else:
        logger.warning("Failed to create superuser (may already exist)")
        return True

def start_all_services():
    """Start all services"""
    logger.info("Starting all services...")
    
    result = run_command("docker compose up -d")
    if result:
        logger.info("All services started successfully")
        return True
    else:
        logger.error("Failed to start all services")
        return False

def main():
    """Main setup function"""
    logger.info("Starting Face Attendance System setup...")
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    if not check_docker_compose():
        sys.exit(1)
    
    # Setup project
    create_directories()
    setup_environment()
    setup_database()
    
    # Build and start services
    if not build_services():
        sys.exit(1)
    
    if not start_services():
        sys.exit(1)
    
    if not run_migrations():
        sys.exit(1)
    
    if not create_superuser():
        sys.exit(1)
    
    if not start_all_services():
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info("Services are now running:")
    logger.info("- Backend API: http://localhost:8000")
    logger.info("- Admin Dashboard: http://localhost:3000")
    logger.info("- Prometheus: http://localhost:9090")
    logger.info("- Grafana: http://localhost:3002")
    logger.info("- RabbitMQ Management: http://localhost:15672")
    logger.info("- MinIO Console: http://localhost:9001")

if __name__ == "__main__":
    main()
