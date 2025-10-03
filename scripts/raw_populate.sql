-- Raw SQL script to populate database with minimal data
-- This avoids all SQLAlchemy compatibility issues

-- Create insurance company if not exists
INSERT INTO insurance_companies (name, registration_number, address, contact_email, contact_phone, website, description, created_at, updated_at)
SELECT 'Secure Life Insurance Nigeria', 'RC123456', '14B Adeola Odeku Street, Victoria Island, Lagos', 'info@securelife.ng', '+234-1-234-5678', 'https://securelife.ng', 'Leading life insurance provider in Nigeria', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM insurance_companies WHERE name = 'Secure Life Insurance Nigeria');

-- Create Sarah Johnson (Insurance Admin) if not exists
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'sarah.johnson', 'sarah.johnson@sovereigntrust.com', '$2b$12$v/HSutJrWBK2Lz1uAGYd7eeNu4pCif5NmoQbeP39GW27euY/hMn7i', 'Sarah Johnson', 'INSURANCE_ADMIN', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'sarah.johnson@sovereigntrust.com');

-- Create John Broker if not exists
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'john.broker', 'john.broker@scib.ng', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'John Broker', 'BROKER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'john.broker@scib.ng');

-- Create broker profile for John
INSERT INTO brokers (user_id, name, license_number, agency_name, contact_email, contact_phone, office_address, commission_type, default_commission_rate, total_policies_sold, total_premiums_collected, total_commission_earned, is_active, is_verified, created_at, updated_at)
SELECT u.id, 'SCIB', 'BRK-2023-001', 'Sovereign Capital Investment Banking', 'john.broker@scib.ng', '+234-801-234-5678', 'Lagos, Nigeria', 'percentage', 0.125, 0, 0, 0, true, true, NOW(), NOW()
FROM users u 
WHERE u.email = 'john.broker@scib.ng' 
AND NOT EXISTS (SELECT 1 FROM brokers WHERE user_id = u.id);

-- Create customer users
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'customer1', 'customer1@example.com', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'Customer 1', 'CUSTOMER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer1@example.com');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'customer2', 'customer2@example.com', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'Customer 2', 'CUSTOMER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer2@example.com');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'customer3', 'customer3@example.com', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'Customer 3', 'CUSTOMER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer3@example.com');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'customer4', 'customer4@example.com', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'Customer 4', 'CUSTOMER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer4@example.com');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at, updated_at)
SELECT 'customer5', 'customer5@example.com', '$2b$12$kHc7N2CyjPqdoeIKRITMGuFOCgYPrud0nSvvTE6Q1Z1QLH2hGuwg.', 'Customer 5', 'CUSTOMER', true, true, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'customer5@example.com');

-- Create policies with realistic data
-- Policy 1: Life Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0001', 'LIFE', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE + INTERVAL '275 days', 
    450000, 8000000,
    'Life Corp Ltd', c.full_name, c.email, '+234-800-000-0001',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer1@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0001');

-- Policy 2: Auto Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0002', 'AUTO', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE + INTERVAL '305 days', 
    320000, 5500000,
    'Auto Shield Inc', c.full_name, c.email, '+234-800-000-0002',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer2@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0002');

-- Policy 3: Health Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0003', 'HEALTH', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE + INTERVAL '245 days', 
    180000, 2500000,
    'Health Plus Ltd', c.full_name, c.email, '+234-800-000-0003',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer3@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0003');

-- Policy 4: Life Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0004', 'LIFE', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE + INTERVAL '320 days', 
    620000, 12000000,
    'Premium Life Co', c.full_name, c.email, '+234-800-000-0004',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer4@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0004');

-- Policy 5: Auto Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0005', 'AUTO', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE + INTERVAL '335 days', 
    280000, 4200000,
    'Drive Safe Ltd', c.full_name, c.email, '+234-800-000-0005',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer5@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0005');

-- Policy 6: Health Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0006', 'HEALTH', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '75 days', CURRENT_DATE + INTERVAL '290 days', 
    220000, 3200000,
    'Wellness Corp', c.full_name, c.email, '+234-800-000-0006',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer1@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0006');

-- Policy 7: Life Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0007', 'LIFE', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '150 days', CURRENT_DATE + INTERVAL '215 days', 
    380000, 7500000,
    'Secure Future Ltd', c.full_name, c.email, '+234-800-000-0007',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer2@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0007');

-- Policy 8: Auto Insurance
INSERT INTO policies (
    policy_number, policy_type, user_id, company_id, broker_id, 
    status, start_date, end_date, premium_amount, coverage_amount,
    company_name, contact_person, contact_email, contact_phone,
    created_at, updated_at
)
SELECT 
    'POL-001-2024-0008', 'AUTO', 
    c.id, ic.id, b.id,
    'ACTIVE', CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE + INTERVAL '345 days', 
    410000, 6800000,
    'Road Guardian Inc', c.full_name, c.email, '+234-800-000-0008',
    NOW(), NOW()
FROM users c, insurance_companies ic, brokers b
WHERE c.email = 'customer3@example.com' 
AND ic.name = 'Secure Life Insurance Nigeria'
AND b.license_number = 'BRK-2023-001'
AND NOT EXISTS (SELECT 1 FROM policies WHERE policy_number = 'POL-001-2024-0008');

-- Create premiums for each policy (2-3 premiums per policy)
-- Policy 1 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 450000, CURRENT_DATE - INTERVAL '60 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0001'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '60 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 450000, CURRENT_DATE + INTERVAL '30 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0001'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '30 days');

-- Policy 2 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 320000, CURRENT_DATE - INTERVAL '30 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0002'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '30 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 320000, CURRENT_DATE + INTERVAL '60 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0002'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '60 days');

-- Policy 3 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 180000, CURRENT_DATE - INTERVAL '90 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0003'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '90 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 180000, CURRENT_DATE + INTERVAL '15 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0003'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '15 days');

-- Policy 4 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 620000, CURRENT_DATE - INTERVAL '15 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0004'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '15 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 620000, CURRENT_DATE + INTERVAL '45 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0004'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '45 days');

-- Policy 5 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 280000, CURRENT_DATE, 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0005'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE);

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 280000, CURRENT_DATE + INTERVAL '90 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0005'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '90 days');

-- Policy 6 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 220000, CURRENT_DATE - INTERVAL '45 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0006'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '45 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 220000, CURRENT_DATE + INTERVAL '75 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0006'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '75 days');

-- Policy 7 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 380000, CURRENT_DATE - INTERVAL '120 days', 'paid', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0007'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE - INTERVAL '120 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 380000, CURRENT_DATE + INTERVAL '10 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0007'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '10 days');

-- Policy 8 premiums
INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 410000, CURRENT_DATE + INTERVAL '10 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0008'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '10 days');

INSERT INTO premiums (policy_id, amount, due_date, payment_status, billing_cycle, currency, created_at, updated_at)
SELECT p.id, 410000, CURRENT_DATE + INTERVAL '100 days', 'pending', 'monthly', 'NGN', NOW(), NOW()
FROM policies p WHERE p.policy_number = 'POL-001-2024-0008'
AND NOT EXISTS (SELECT 1 FROM premiums WHERE policy_id = p.id AND due_date = CURRENT_DATE + INTERVAL '100 days');

-- Display summary
SELECT 'Database population completed!' as message;
SELECT COUNT(*) as total_policies FROM policies;
SELECT COUNT(*) as total_premiums FROM premiums;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_brokers FROM brokers;
