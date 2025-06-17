# InsureFlow VPS Deployment Guide

This guide will help you deploy InsureFlow to your Hostinger VPS with Docker and Nginx.

## Prerequisites

- VPS with Docker and Docker Compose installed
- Nginx installed and running
- Domain name pointed to your VPS (optional but recommended)
- SSH access to your VPS

## Architecture

The VPS deployment uses:
- **FastAPI Backend**: Running on port 8000
- **Streamlit Dashboard**: Running on port 8501
- **PostgreSQL Database**: Running on port 5432
- **Redis**: Running on port 6379
- **Nginx**: Reverse proxy routing traffic between services

## Step 1: Upload Files to VPS

Upload your InsureFlow project to your VPS. You can use SCP, SFTP, or Git:

```bash
# Option 1: Using Git (recommended)
git clone https://github.com/yourusername/insureflow.git
cd insureflow

# Option 2: Using SCP
scp -r ./insureflow user@your-vps-ip:/home/user/
```

## Step 2: Set Up Environment Variables

1. Copy the production environment template:
```bash
cp env.production .env
```

2. Edit the `.env` file with your actual values:
```bash
nano .env
```

Required values to update:
- `POSTGRES_PASSWORD`: Strong password for PostgreSQL
- `JWT_SECRET_KEY`: Strong secret key for JWT tokens
- `SQUAD_SECRET_KEY`: Your Squad Co secret key
- `SQUAD_PUBLIC_KEY`: Your Squad Co public key

## Step 3: Deploy with Docker

Run the deployment script:
```bash
./deploy-vps.sh
```

This script will:
- Check prerequisites
- Stop any existing containers
- Build and start all services
- Perform health checks
- Display service URLs

## Step 4: Configure Nginx

1. Copy the Nginx configuration:
```bash
sudo cp nginx-vps.conf /etc/nginx/sites-available/insureflow
```

2. Edit the configuration with your domain:
```bash
sudo nano /etc/nginx/sites-available/insureflow
```
Replace `your-domain.com` with your actual domain name.

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/insureflow /etc/nginx/sites-enabled/
```

4. Test Nginx configuration:
```bash
sudo nginx -t
```

5. Reload Nginx:
```bash
sudo systemctl reload nginx
```

## Step 5: Set Up SSL (Optional but Recommended)

1. Install Certbot:
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

2. Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

3. Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Step 6: Verify Deployment

After deployment, your application will be available at:

- **Main Application**: `http://your-domain.com` (or `http://your-vps-ip`)
- **API Documentation**: `http://your-domain.com/docs`
- **Health Check**: `http://your-domain.com/health`

## Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f app
docker-compose -f docker-compose.prod.yml logs -f dashboard
```

### Restart Services
```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart app
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Service Health Checks

Check if services are running:
```bash
# FastAPI
curl http://localhost:8000/health

# Streamlit
curl http://localhost:8501

# PostgreSQL
docker exec insureflow_db pg_isready -U insureflow

# Redis
docker exec insureflow_redis redis-cli ping
```

### Common Issues

1. **Port conflicts**: Make sure ports 8000, 8501, 5432, and 6379 are not used by other services.

2. **Database connection issues**: Check if PostgreSQL is running and environment variables are correct.

3. **Nginx configuration errors**: Run `sudo nginx -t` to check for syntax errors.

4. **SSL certificate issues**: Make sure your domain is properly pointed to your VPS IP.

### View Container Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Access Container Shell
```bash
# FastAPI container
docker exec -it insureflow_app bash

# Database container
docker exec -it insureflow_db psql -U insureflow -d insureflow
```

## Security Considerations

1. **Firewall**: Configure UFW to only allow necessary ports:
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **Database**: PostgreSQL is exposed on port 5432. Consider restricting access or using Docker networks.

3. **Environment Variables**: Keep your `.env` file secure and never commit it to version control.

4. **Regular Updates**: Keep your system and Docker images updated.

## Backup Strategy

1. **Database Backup**:
```bash
docker exec insureflow_db pg_dump -U insureflow insureflow > backup.sql
```

2. **Restore Database**:
```bash
docker exec -i insureflow_db psql -U insureflow -d insureflow < backup.sql
```

3. **Volume Backup**: Consider backing up Docker volumes regularly.

## Support

If you encounter issues:
1. Check the logs using the commands above
2. Verify all environment variables are set correctly
3. Ensure all required ports are open
4. Check Nginx configuration syntax 