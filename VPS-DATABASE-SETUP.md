# VPS Database Population Setup

## Overview
Automatic database population has been configured for VPS deployment. When you deploy to your VPS, the database will be automatically populated with realistic sample data.

## What Gets Created

### Insurance Companies (3)
- **Secure Life Insurance Nigeria** - Leading life insurance provider
- **Guardian Shield Insurance** - Comprehensive insurance solutions
- **Prestige Insurance Limited** - Premium insurance services

### Users
- **3 Admin Users** - One for each insurance company
- **5 Broker Users** - With detailed profiles and performance data
- **50 Customer Users** - Generated with realistic names and emails

### Sample Data
- **60-100 Policies** - Distributed across all brokers
- **Multiple Policy Types** - Life, Health, Auto, Home, Business, Travel
- **Realistic Premium Amounts** - In Nigerian Naira (₦)
- **Payment Records** - With Squad Co integration data
- **Commission Tracking** - For broker performance metrics

## Deployment Process

The updated `deploy-vps.sh` script now:

1. **Deploys containers** using `docker-compose.prod.yml`
2. **Runs health checks** on all services
3. **Executes database migrations** using Alembic
4. **Populates database** with sample data automatically
5. **Provides login credentials** for immediate testing

## Sample Login Credentials

### Admin Users
- `admin@securelife.ng` / `password123`
- `admin@guardianshield.ng` / `password123`
- `admin@prestigeinsurance.ng` / `password123`

### Broker Users
- `ethan.carter@brokers.ng` / `password123`
- `isabella.rossi@brokers.ng` / `password123`
- `ryan.kim@brokers.ng` / `password123`
- `sophia.zhang@brokers.ng` / `password123`
- `liam.davis@brokers.ng` / `password123`

## Dashboard Features Available

With the populated data, you'll immediately see:

- **Insurance firm dashboard** with broker performance metrics
- **Broker dashboards** with client portfolios and payment tracking
- **Realistic policy data** across multiple insurance types
- **Payment tracking** with Squad Co integration ready
- **Commission tracking** for brokers
- **Mix of payment statuses** (paid, pending, overdue)
- **Various billing cycles** (monthly, quarterly, annual)

## Manual Operations

### Test Locally
```bash
# Test database population locally
./scripts/test-populate.sh
```

### Repopulate Database
```bash
# If you need to repopulate the database on VPS
docker exec insureflow_backend python scripts/populate_database.py
```

### View Logs
```bash
# View deployment logs
docker compose -f docker-compose.prod.yml logs -f
```

## Database Schema

The population script creates data that covers:

- **User management** with role-based access (Admin, Broker, Customer)
- **Company structures** with proper relationships
- **Policy lifecycle** from creation to payment
- **Commission calculations** based on broker rates
- **Payment processing** with transaction tracking
- **Premium billing** with various cycles and statuses

## Benefits for Dashboard Development

This setup provides:

1. **Immediate data visibility** - No empty dashboards
2. **Realistic metrics** - Actual numbers for chart development
3. **Complete workflows** - End-to-end data for testing
4. **Performance testing** - Sufficient data volume for optimization
5. **User experience testing** - Multiple user roles and scenarios

## Security Notes

- All sample passwords are `password123`
- Change these credentials before production use
- The data is suitable for development and demo purposes
- Replace with real data for actual production deployment

## Next Steps

After deployment with populated data:

1. **Test login** with sample credentials
2. **Verify dashboard metrics** display correctly
3. **Test payment workflows** with the broker interface
4. **Validate Squad Co integration** with sample payment data
5. **Customize data** as needed for specific use cases 