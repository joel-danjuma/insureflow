# InsureFlow Admin Dashboard Setup

## 🔐 Security Implementation

The InsureFlow internal admin dashboard now has **enhanced security** that restricts access to only **global platform administrators**. This prevents insurance company admins and broker admins from accessing sensitive platform revenue data.

## 🎯 Access Control

### **Who Can Access**
- ✅ **`ADMIN`** - Global InsureFlow platform administrators only

### **Who Cannot Access** 
- ❌ **`INSURANCE_ADMIN`** - Insurance company administrators
- ❌ **`BROKER_ADMIN`** - Broker administrators  
- ❌ **`INSURANCE_ACCOUNTANT`** - Insurance accountants
- ❌ **`BROKER_ACCOUNTANT`** - Broker accountants

## 🛠️ Creating Your First Admin User

### **Option 1: Using the Admin Creation Script**
```bash
# Run from project root
python scripts/create_admin_user.py
```

The script will prompt you for:
- Email address
- Username (optional, defaults to email prefix)
- Full name
- Password (hidden input with confirmation)

### **Option 2: Manual Database Insert**
```sql
-- Replace values with your desired credentials
-- Password should be bcrypt hashed
INSERT INTO users (
    username, 
    email, 
    hashed_password, 
    full_name, 
    role, 
    is_active, 
    is_verified,
    can_create_policies,
    can_make_payments
) VALUES (
    'insureflow_admin',
    'admin@insureflow.com',
    '$2b$12$...your_bcrypt_hashed_password...',
    'InsureFlow Administrator',
    'ADMIN',
    true,
    true,
    true,
    true
);
```

### **Option 3: Python Script for Password Hashing**
```python
from app.core.security import get_password_hash

# Hash your password
password = "your_secure_password"
hashed = get_password_hash(password)
print(f"Hashed password: {hashed}")
```

## 🌐 Admin Dashboard Endpoints

Once you have an admin user, you can access:

### **Main Dashboard**
```
GET /api/v1/admin/insureflow/dashboard
```
Comprehensive overview with platform health, commission analytics, and user management.

### **Transaction Monitoring**
```
GET /api/v1/admin/insureflow/transactions/logs
```
Detailed transaction logs with filtering and pagination.

### **Commission Analytics**
```
GET /api/v1/admin/insureflow/analytics/commission
GET /api/v1/admin/insureflow/commission/summary
```
InsureFlow revenue analytics and commission breakdown.

### **Platform Health**
```
GET /api/v1/admin/insureflow/analytics/platform-health
GET /api/v1/admin/insureflow/system/health-check
```
System monitoring and health metrics.

### **Financial Reports**
```
GET /api/v1/admin/insureflow/reports/financial
GET /api/v1/admin/insureflow/export/transactions
```
Accounting reports and data export capabilities.

### **User Management**
```
GET /api/v1/admin/insureflow/users/management-summary
```
Platform user analytics and management overview.

### **System Administration**
```
GET /api/v1/admin/insureflow/alerts/recent
POST /api/v1/admin/insureflow/alerts/create
GET /api/v1/admin/insureflow/system/audit-log
```
System alerts and audit logging.

## 🔑 Authentication Flow

### **1. Login**
```bash
curl -X POST /api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@insureflow.com&password=your_password"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### **2. Access Admin Endpoints**
```bash
curl -X GET /api/v1/admin/insureflow/dashboard \
  -H "Authorization: Bearer your_jwt_token_here"
```

## 🛡️ Security Features

### **Role-Based Access Control**
- New dependency: `get_current_insureflow_admin`
- Enforces **ADMIN role only** (not insurance/broker admins)
- Clear error messages for unauthorized access

### **Error Response for Non-Platform Admins**
```json
{
  "detail": "InsureFlow platform admin privileges required. Only global administrators can access internal platform data."
}
```

## 📊 What Admin Dashboard Provides

### **Revenue Intelligence**
- **Total InsureFlow commission** (0.75% of all transactions)
- **Monthly revenue trends** and growth rates
- **Top revenue-generating brokers**
- **Commission vs Habari split** analytics

### **Transaction Oversight**
- **Real-time transaction monitoring**
- **Failed transaction alerts**
- **Webhook success rates**
- **Settlement tracking**

### **Platform Health**
- **System uptime monitoring**
- **API response time tracking**
- **Error rate analytics**
- **User activity metrics**

### **Business Intelligence**
- **User growth analytics**
- **Broker performance rankings**
- **Policy transaction analysis**
- **Financial reconciliation reports**

## 🚀 Frontend Integration

### **React/Next.js Example**
```javascript
// Check if user can access admin dashboard
const canAccessAdmin = user?.role === 'ADMIN';

// Protect admin routes
if (!canAccessAdmin) {
  redirect('/dashboard'); // Redirect to regular dashboard
}

// Fetch admin data
const adminData = await fetch('/api/v1/admin/insureflow/dashboard', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

## 📈 Production Considerations

### **Additional Security Measures**
- **IP Whitelisting**: Restrict admin endpoints to specific IP addresses
- **Multi-Factor Authentication**: Add 2FA for admin users  
- **Rate Limiting**: Implement stricter rate limits on admin endpoints
- **Audit Logging**: Enable comprehensive audit logging
- **Session Management**: Shorter session timeouts for admin users

### **Monitoring & Alerts**
- Set up monitoring for admin endpoint access
- Alert on failed admin login attempts
- Monitor for unusual admin activity patterns
- Regular audit of admin user permissions

### **Data Protection**
- Regular backups of admin audit logs
- Secure storage of admin credentials
- Periodic admin access reviews
- Compliance with data protection regulations

---

## 🎯 Summary

The InsureFlow admin dashboard is now **properly secured** with platform-level access control. Only users with the global `ADMIN` role can access sensitive platform revenue data and system management features. This ensures that insurance company and broker administrators cannot view InsureFlow's internal business metrics while still maintaining their ability to manage their own organizations. 