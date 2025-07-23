# InsureFlow VPS Deployment Guide

This guide will help you deploy InsureFlow to your VPS with Docker and Nginx.

## Prerequisites

- VPS with Docker and Docker Compose installed
- Nginx installed and running
- Domain name pointed to your VPS (optional but recommended)
- SSH access to your VPS

## Architecture

The VPS deployment uses:
- **Next.js Frontend**: Running on port 3000
- **FastAPI Backend**: Running on port 8000
- **PostgreSQL Database**: Running on port 5432
- **Redis**: Running on port 6379 (if used)
- **Nginx**: Reverse proxy routing traffic, directing UI traffic to the frontend and `/api` traffic to the backend.

## Step 1: Upload Files to VPS

Upload your InsureFlow project to your VPS. The recommended method is using Git.

```bash
# Clone your repository
git clone https://github.com/yourusername/insureflow.git
cd insureflow

# Or if already cloned, pull the latest changes
git pull origin main
```

## Step 2: Set Up Environment Variables

1. Copy the production environment template. **This is a critical step for production security.**
```bash
cp env.production .env
```

2. Edit the `.env` file with your actual values:
```bash
nano .env
```

Required values to update:
- `POSTGRES_PASSWORD`: A strong password for your PostgreSQL database.
- `SECRET_KEY`: A strong, unique secret key for JWT tokens.
- `SQUAD_SECRET_KEY`: Your Squad Co secret key.
- `SQUAD_PUBLIC_KEY`: Your Squad Co public key.
- `BACKEND_CORS_ORIGINS`: Add your production domain (e.g., `https://your-domain.com`).

## Step 3: Deploy with Docker

Run the updated deployment script:
```bash
./deploy-vps.sh
```

This script will:
- Check for prerequisites like Docker and a `.env` file.
- Stop any existing containers.
- Build and start the `frontend` and `backend` services.
- Perform health checks on the new services.
- Display the final URLs (as seen through Nginx).

## Step 4: Configure Nginx

1. Copy the Nginx configuration to the appropriate directory:
```bash
sudo cp nginx-vps.conf /etc/nginx/sites-available/insureflow
```

2. Edit the configuration to include your domain name:
```bash
sudo nano /etc/nginx/sites-available/insureflow
```
Replace `your_domain.com` with your actual domain name.

3. Enable the Nginx site by creating a symbolic link:
```bash
sudo ln -s /etc/nginx/sites-available/insureflow /etc/nginx/sites-enabled/
```

4. Test your Nginx configuration for syntax errors:
```bash
sudo nginx -t
```

5. If the test is successful, reload Nginx to apply the changes:
```bash
sudo systemctl reload nginx
```

## Step 5: Set Up SSL (Recommended)

Follow the instructions in the original guide to install Certbot and obtain an SSL certificate for your domain. This is a crucial step for any production application.

## Step 6: Verify Deployment

After deployment, your application should be available at:

- **Main Application**: `http://your-domain.com` (or `https://` if SSL is configured)
- **API Documentation**: `http://your-domain.com/api/v1/docs`

## Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service (e.g., frontend or backend)
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart a specific service
docker-compose restart frontend
```

### Stop Services
```bash
docker-compose down
```

### Update Application
```bash
# 1. Pull latest changes from Git
git pull origin main

# 2. Rebuild and restart the services
./deploy-vps.sh
```

## Troubleshooting

### Service Health Checks
You can manually check if services are responding inside the VPS:
```bash
# Next.js Frontend
curl http://localhost:3000

# FastAPI Backend
curl http://localhost:8000/api/v1/docs

# PostgreSQL
docker exec insureflow_db pg_isready -U insureflow

# Redis
docker exec insureflow_redis redis-cli ping
```

### Common Issues
- **CORS errors**: Ensure your production domain is listed in `BACKEND_CORS_ORIGINS` in your `.env` file.
- **502 Bad Gateway from Nginx**: This usually means the `frontend` or `backend` service is down. Check the logs (`docker-compose logs -f <service_name>`) to diagnose the issue.
- **Database connection issues**: Double-check that the database credentials in your `.env` file are correct.

### View Container Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Backend (FastAPI) container
docker exec -it insureflow_app bash

# Frontend (Next.js) container
docker exec -it insureflow-frontend-1 bash # Note: container name may vary, check with `docker ps`

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