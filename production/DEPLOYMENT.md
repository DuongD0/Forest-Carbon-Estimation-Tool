# Production Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Domain name with DNS configured
- SSL certificates
- Auth0 account configured
- Stripe account (if using payments)

## Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Step 2: Application Deployment
```bash
# Clone repository
git clone https://github.com/your-org/forest-carbon-estimation-tool.git
cd forest-carbon-estimation-tool

# Copy production configuration
cp production/.env.backend.prod backend/.env
cp production/.env.frontend.prod frontend/.env

# Update configuration files with your settings
nano backend/.env
nano frontend/.env

# Create required directories
mkdir -p uploads logs backups letsencrypt monitoring

# Deploy with production configuration
docker-compose -f docker-compose.yml -f production/docker-compose.prod.yml up -d
```

## Step 3: Database Setup
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user (optional)
docker-compose exec backend python -c "
from app.db.session import SessionLocal
from app import crud, schemas
db = SessionLocal()
user_in = schemas.UserCreate(
    email='admin@your-domain.com',
    first_name='Admin',
    last_name='User',
    organization='Your Organization'
)
user = crud.user.create(db, obj_in=user_in)
print(f'Created admin user: {user.email}')
"
```

## Step 4: SSL Configuration
```bash
# If using Let's Encrypt with Traefik (automatic)
# Certificates will be generated automatically

# If using custom certificates
sudo mkdir -p /etc/ssl/certs /etc/ssl/private
sudo cp your-domain.com.crt /etc/ssl/certs/
sudo cp your-domain.com.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/your-domain.com.key
```

## Step 5: Monitoring Setup
```bash
# Access Grafana dashboard
# https://monitoring.your-domain.com
# Default login: admin / CHANGE_THIS_ADMIN_PASSWORD

# Import dashboard configurations
# Copy monitoring dashboards from ./monitoring/dashboards/
```

## Step 6: Backup Configuration
```bash
# Set up automated backups
crontab -e

# Add backup cron job (daily at 2 AM)
0 2 * * * /path/to/backup-script.sh
```

## Step 7: Health Checks
```bash
# Check all services are running
docker-compose ps

# Check application health
curl https://api.your-domain.com/
curl https://your-domain.com/

# Check database connection
docker-compose exec backend python -c "
from app.db.session import SessionLocal
db = SessionLocal()
print('Database connection: OK')
"
```

## Maintenance Commands
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Update application
git pull
docker-compose build
docker-compose up -d

# Database backup
docker-compose exec db pg_dump -U forest_user forest_carbon_db > backup_$(date +%Y%m%d).sql

# Database restore
docker-compose exec -T db psql -U forest_user forest_carbon_db < backup_20240101.sql
```

## Troubleshooting
- Check Docker logs: `docker-compose logs [service_name]`
- Verify environment variables: `docker-compose config`
- Test database connection: `docker-compose exec db psql -U forest_user forest_carbon_db`
- Check SSL certificates: `openssl x509 -in cert.crt -text -noout`
- Monitor resource usage: `docker stats`
