#!/usr/bin/env python3
"""
Populate InsureFlow database with realistic dummy data for production/demo.
This script creates sample insurance companies, brokers, policies, premiums, and payments.
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.company import InsuranceCompany as Company
from app.models.broker import Broker
from app.models.policy import Policy, PolicyType, PolicyStatus, PaymentFrequency
from app.models.premium import Premium, PaymentStatus, BillingCycle
from app.models.payment import Payment, PaymentMethod, PaymentTransactionStatus

fake = Faker()

def create_insurance_companies(db: Session):
    """Create sample insurance companies. This function is idempotent."""
    companies_data = [
        {
            "name": "Secure Life Insurance Nigeria",
            "description": "Leading life insurance provider in Nigeria with over 30 years of experience.",
            "address": "14B Adeola Odeku Street, Victoria Island, Lagos",
            "contact_email": "info@securelife.ng",
            "contact_phone": "+234-1-234-5678",
            "website": "https://securelife.ng",
            "registration_number": "RC123456"
        },
        {
            "name": "Guardian Shield Insurance",
            "description": "Comprehensive insurance solutions for individuals and businesses.",
            "address": "Plot 1234, Central Business District, Abuja",
            "contact_email": "contact@guardianshield.ng",
            "contact_phone": "+234-9-876-5432",
            "website": "https://guardianshield.ng",
            "registration_number": "RC234567"
        },
        {
            "name": "Prestige Insurance Limited",
            "description": "Premium insurance services with focus on high-value clients.",
            "address": "5 Broad Street, Lagos Island, Lagos",
            "contact_email": "info@prestigeinsurance.ng",
            "contact_phone": "+234-1-555-0123",
            "website": "https://prestigeinsurance.ng",
            "registration_number": "RC345678"
        }
    ]
    
    final_companies = []
    for company_data in companies_data:
        existing_company = db.query(Company).filter_by(name=company_data['name']).first()
        if existing_company:
            print(f"ℹ️  Found existing company: {existing_company.name}")
            final_companies.append(existing_company)
        else:
            print(f"✅ Creating company: {company_data['name']}")
            company = Company(**company_data)
            db.add(company)
            final_companies.append(company)
    
    db.commit()
    # Re-fetch objects to ensure they are bound to the session
    for i, company in enumerate(final_companies):
        if not company.id:
            final_companies[i] = db.query(Company).filter_by(name=company.name).one()

    return final_companies

def create_admin_users(db: Session, companies):
    """Create admin users for insurance companies. This function is idempotent."""
    admins_data = [
        { "username": "admin_secure", "email": "admin@securelife.ng", "full_name": "Adebayo Johnson", "role": UserRole.ADMIN },
        { "username": "admin_guardian", "email": "admin@guardianshield.ng", "full_name": "Fatima Mohammed", "role": UserRole.ADMIN },
        { "username": "admin_prestige", "email": "admin@prestigeinsurance.ng", "full_name": "Chinedu Okafor", "role": UserRole.ADMIN }
    ]
    
    final_admins = []
    for admin_data in admins_data:
        existing_user = db.query(User).filter_by(email=admin_data['email']).first()
        if existing_user:
            print(f"ℹ️  Found existing admin user: {existing_user.email}")
            final_admins.append(existing_user)
        else:
            print(f"✅ Creating admin user: {admin_data['email']}")
            admin = User(**admin_data, hashed_password=get_password_hash("password123"), is_active=True, is_verified=True)
            db.add(admin)
            final_admins.append(admin)
    
    db.commit()
    return final_admins

def create_broker_users_and_profiles(db: Session, companies):
    """Create broker users and their detailed profiles. This function is idempotent."""
    broker_data = [
        {
            "user": { "username": "ethan_carter", "email": "ethan.carter@brokers.ng", "full_name": "Ethan Carter", "role": UserRole.BROKER },
            "broker": {
                "name": "Ethan Carter", "license_number": "BRK-001", "agency_name": "Carter Insurance Brokers",
                "contact_email": "ethan.carter@brokers.ng", "contact_phone": "+234-803-123-4567", "office_address": "Suite 12, Tafawa Balewa Square, Lagos Island",
                "specialization": "Life Insurance, Health Insurance", "experience_years": 8, "territory": "Lagos State", "default_commission_rate": Decimal("0.125"),
                "is_verified": True, "verification_date": datetime.utcnow() - timedelta(days=180), "license_expiry_date": datetime.utcnow() + timedelta(days=365),
                "bio": "Experienced insurance broker specializing in life and health insurance with 8 years in the industry."
            }
        },
        {
            "user": { "username": "isabella_rossi", "email": "isabella.rossi@brokers.ng", "full_name": "Isabella Rossi", "role": UserRole.BROKER },
            "broker": {
                "name": "Isabella Rossi", "license_number": "BRK-002", "agency_name": "Rossi Insurance Solutions",
                "contact_email": "isabella.rossi@brokers.ng", "contact_phone": "+234-805-987-6543", "office_address": "Block C, Admiralty Way, Lekki Phase 1, Lagos",
                "specialization": "Auto Insurance, Property Insurance", "experience_years": 12, "territory": "Lagos, Ogun State", "default_commission_rate": Decimal("0.15"),
                "is_verified": True, "verification_date": datetime.utcnow() - timedelta(days=200), "license_expiry_date": datetime.utcnow() + timedelta(days=500),
                "bio": "Senior insurance broker with expertise in auto and property insurance, serving clients across Lagos and Ogun states."
            }
        },
        {
            "user": { "username": "ryan_kim", "email": "ryan.kim@brokers.ng", "full_name": "Ryan Kim", "role": UserRole.BROKER },
            "broker": {
                "name": "Ryan Kim", "license_number": "BRK-003", "agency_name": "Kim Insurance Group",
                "contact_email": "ryan.kim@brokers.ng", "contact_phone": "+234-807-456-7890", "office_address": "7th Floor, Sterling Towers, Marina, Lagos",
                "specialization": "Business Insurance, Travel Insurance", "experience_years": 6, "territory": "Lagos, Abuja", "default_commission_rate": Decimal("0.10"),
                "is_verified": True, "verification_date": datetime.utcnow() - timedelta(days=120), "license_expiry_date": datetime.utcnow() + timedelta(days=400),
                "bio": "Business insurance specialist helping SMEs and corporates protect their assets and operations."
            }
        },
        {
            "user": { "username": "sophia_zhang", "email": "sophia.zhang@brokers.ng", "full_name": "Sophia Zhang", "role": UserRole.BROKER },
            "broker": {
                "name": "Sophia Zhang", "license_number": "BRK-004", "agency_name": "Zhang Financial Services",
                "contact_email": "sophia.zhang@brokers.ng", "contact_phone": "+234-809-234-5678", "office_address": "Plot 123, Wuse 2, Abuja",
                "specialization": "Life Insurance, Investment-Linked Policies", "experience_years": 10, "territory": "FCT Abuja, Niger State", "default_commission_rate": Decimal("0.135"),
                "is_verified": True, "verification_date": datetime.utcnow() - timedelta(days=300), "license_expiry_date": datetime.utcnow() + timedelta(days=600),
                "bio": "Financial advisor and insurance broker focusing on life insurance and investment products for high-net-worth individuals."
            }
        },
        {
            "user": { "username": "liam_davis", "email": "liam.davis@brokers.ng", "full_name": "Liam Davis", "role": UserRole.BROKER },
            "broker": {
                "name": "Liam Davis", "license_number": "BRK-005", "agency_name": "Davis Insurance Associates",
                "contact_email": "liam.davis@brokers.ng", "contact_phone": "+234-811-345-6789", "office_address": "Block B, Independence Layout, Enugu",
                "specialization": "Health Insurance, Family Protection", "experience_years": 5, "territory": "Enugu, Anambra State", "default_commission_rate": Decimal("0.115"),
                "is_verified": True, "verification_date": datetime.utcnow() - timedelta(days=90), "license_expiry_date": datetime.utcnow() + timedelta(days=300),
                "bio": "Young and dynamic broker specializing in health insurance and family protection plans for the growing middle class."
            }
        }
    ]
    
    final_brokers = []
    for data in broker_data:
        existing_user = db.query(User).filter_by(email=data['user']['email']).first()
        if existing_user and existing_user.broker_profile:
            print(f"ℹ️  Found existing broker: {existing_user.email}")
            final_brokers.append(existing_user.broker_profile)
            continue

        print(f"✅ Creating broker user and profile: {data['user']['email']}")
        
        # Create user
        user = User(
            **data["user"], 
            hashed_password=get_password_hash("password123"), 
            is_active=True, 
            is_verified=True,
            # Add address and phone from broker profile to main user model
            address=data["broker"]["office_address"],
            phone_number=data["broker"]["contact_phone"],
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=65) # Add a realistic DOB
        )
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create broker profile
        broker = Broker(**data["broker"], user_id=user.id, company_id=random.choice(companies).id)
        db.add(broker)
        final_brokers.append(broker)
    
    db.commit()
    return final_brokers

def create_customer_users(db: Session, count=50):
    """Create customer users. This function is idempotent."""
    customer_count = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    if customer_count >= count:
        print(f"ℹ️  Found {customer_count} customers. Skipping customer creation.")
        return db.query(User).filter(User.role == UserRole.CUSTOMER).all()

    customers_to_create = count - customer_count
    print(f"✅ Creating {customers_to_create} new customer users...")
    
    customers = []
    for _ in range(customers_to_create):
        customer = User(
            username=fake.user_name(), 
            email=fake.email(), 
            full_name=fake.name(),
            role=UserRole.CUSTOMER, 
            hashed_password=get_password_hash("password123"),
            is_active=True, 
            is_verified=random.choice([True, False]),
            # Add missing fields required by Squad
            phone_number=fake.phone_number(),
            address=fake.address().replace('\n', ', '),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            gender=random.choice(["male", "female"])
        )
        db.add(customer)
        customers.append(customer)
    
    db.commit()
    return db.query(User).filter(User.role == UserRole.CUSTOMER).all()

def create_policies(db: Session, companies, brokers, customers):
    """Create sample policies with realistic data. This function is idempotent."""
    if not customers:
        print("⚠️ No customers found, cannot create policies.")
        return []
        
    policies = []
    policy_types = list(PolicyType)
    
    for broker in brokers:
        num_policies = random.randint(12, 20)
        for i in range(num_policies):
            policy_number = f"POL-{broker.license_number[-3:]}-{2024}-{i+1:04d}"
            
            existing_policy = db.query(Policy).filter_by(policy_number=policy_number).first()
            if existing_policy:
                policies.append(existing_policy)
                continue

            policy_type = random.choice(policy_types)
            customer = random.choice(customers)
            company = random.choice(companies)
            
            start_date = fake.date_between(start_date="-1y", end_date="today")
            end_date = start_date + timedelta(days=365)
            
            coverage_amounts = {
                PolicyType.LIFE: random.randint(1000000, 10000000), PolicyType.HEALTH: random.randint(500000, 5000000),   
                PolicyType.AUTO: random.randint(2000000, 15000000), PolicyType.HOME: random.randint(5000000, 50000000),   
                PolicyType.BUSINESS: random.randint(10000000, 100000000), PolicyType.TRAVEL: random.randint(100000, 1000000),
            }
            
            payment_frequency = random.choices(
                [PaymentFrequency.MONTHLY, PaymentFrequency.QUARTERLY, PaymentFrequency.ANNUALLY], 
                weights=[60, 30, 10]
            )[0]
            
            policy = Policy(
                policy_name=f"{policy_type.name.capitalize()} Insurance",
                policy_number=policy_number, 
                policy_type=policy_type, 
                user_id=customer.id, 
                company_id=company.id,
                broker_id=broker.id, 
                status=random.choices([PolicyStatus.ACTIVE, PolicyStatus.PENDING], weights=[85, 15])[0],
                start_date=start_date, 
                due_date=end_date,
                end_date=end_date, 
                premium_amount=Decimal(str(round(coverage_amounts[policy_type] * 0.1, 2))),  # Calculate a premium
                coverage_amount=str(coverage_amounts[policy_type]),
                payment_frequency=payment_frequency,
                company_name=customer.full_name,  # Use customer's name as company name
                contact_person=customer.full_name,  # Use customer's name
                contact_email=customer.email,  # Use customer's email
                coverage_details=f'{{"type": "{policy_type.name}", "coverage": {coverage_amounts[policy_type]}, "currency": "NGN"}}',
                notes=f"Policy sold by {broker.name} for {policy_type.name} insurance coverage."
            )
            db.add(policy)
            policies.append(policy)
    
    print(f"✅ Creating {len(policies) - db.query(Policy).count()} new policies...")
    db.commit()
    return policies

def create_premiums_and_payments(db: Session, policies):
    """Create premiums and payment records for policies. This function is idempotent."""
    print("Checking for missing premiums and payments...")
    for policy in policies:
        existing_premiums_count = db.query(Premium).filter_by(policy_id=policy.id).count()
        if existing_premiums_count > 0:
            continue

        coverage_amount = int(policy.coverage_amount)
        premium_rates = {
            PolicyType.LIFE: 0.02, PolicyType.HEALTH: 0.05, PolicyType.AUTO: 0.08,      
            PolicyType.HOME: 0.03, PolicyType.BUSINESS: 0.04, PolicyType.TRAVEL: 0.10,
        }
        annual_premium = coverage_amount * premium_rates[policy.policy_type]
        
        billing_cycle = random.choices([BillingCycle.MONTHLY, BillingCycle.QUARTERLY, BillingCycle.ANNUAL], weights=[60, 30, 10])[0]
        cycle_divisors = { BillingCycle.MONTHLY: 12, BillingCycle.QUARTERLY: 4, BillingCycle.SEMI_ANNUAL: 2, BillingCycle.ANNUAL: 1 }
        premium_amount = annual_premium / cycle_divisors[billing_cycle]
        
        premium_due_date = policy.start_date
        current_date = date.today()
        premium_count = 0
        
        while premium_due_date <= current_date + timedelta(days=90):
            premium_count += 1
            premium_ref = f"PREM-{policy.policy_number}-{premium_count:03d}"
            
            if premium_due_date < current_date - timedelta(days=30):
                payment_status = random.choices([PaymentStatus.PAID, PaymentStatus.OVERDUE, PaymentStatus.CANCELLED], weights=[80, 15, 5])[0]
            elif premium_due_date < current_date:
                payment_status = random.choices([PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.OVERDUE], weights=[50, 35, 15])[0]
            else:
                payment_status = PaymentStatus.PENDING
            
            premium = Premium(
                policy_id=policy.id, 
                amount=Decimal(str(round(premium_amount, 2))), 
                currency="NGN", 
                due_date=premium_due_date,
                billing_cycle=billing_cycle, 
                payment_status=payment_status, 
                premium_reference=premium_ref, 
                grace_period_days=30
            )
            
            if payment_status == PaymentStatus.PAID:
                premium.paid_amount = premium.amount
                premium.payment_date = premium_due_date + timedelta(days=random.randint(-5, 10))
                premium.payment_reference = f"PAY-{premium_ref}"
            elif payment_status == PaymentStatus.OVERDUE:
                partial_payment = premium.amount * Decimal(str(random.uniform(0.0, 0.8)))
                premium.paid_amount = partial_payment
                premium.payment_date = premium_due_date + timedelta(days=random.randint(1, 20))
                premium.payment_reference = f"PAY-{premium_ref}-PARTIAL"
            
            # Add the premium to the session first
            db.add(premium)
            # VERY IMPORTANT: Flush the session to get the premium.id from the database
            db.flush()

            # If a payment was made, create the payment record and link it
            if payment_status in [PaymentStatus.PAID, PaymentStatus.OVERDUE] and premium.paid_amount and premium.paid_amount > 0:
                payment = Payment(
                    premium_id=premium.id, # Now premium.id is available
                    amount_paid=premium.paid_amount,
                    currency="NGN",
                    payment_method=random.choice(list(PaymentMethod)),
                    payment_date=premium.payment_date or datetime.now(),
                    status=PaymentTransactionStatus.SUCCESS,
                    transaction_reference=f"TXN-{fake.uuid4()[:8].upper()}",
                    external_reference=f"SQ-{fake.uuid4()[:12].upper()}",
                    squad_transaction_id=fake.uuid4(),
                    payer_name=policy.user.full_name,
                    payer_email=policy.user.email,
                    processing_fee=premium.paid_amount * Decimal("0.015"),
                    net_amount=premium.paid_amount * Decimal("0.985"),
                    processed_at=premium.payment_date or datetime.now()
                )
                db.add(payment)
            
            if billing_cycle == BillingCycle.MONTHLY: premium_due_date += timedelta(days=30)
            elif billing_cycle == BillingCycle.QUARTERLY: premium_due_date += timedelta(days=90)
            elif billing_cycle == BillingCycle.SEMI_ANNUAL: premium_due_date += timedelta(days=180)
            else: premium_due_date += timedelta(days=365)
    
    db.commit()

def update_broker_statistics(db: Session, brokers):
    """Update broker performance statistics based on their policies and payments."""
    if not brokers: return
    for broker in brokers:
        policies = db.query(Policy).filter(Policy.broker_id == broker.id).all()
        
        total_policies = len(policies)
        total_premiums = Decimal("0")
        total_commission = Decimal("0")
        
        for policy in policies:
            policy_premiums = db.query(Premium).filter(Premium.policy_id == policy.id).all()
            for premium in policy_premiums:
                if premium.payment_status == PaymentStatus.PAID and premium.amount:
                    total_premiums += premium.amount
                    if broker.default_commission_rate:
                        commission = premium.amount * broker.default_commission_rate
                        total_commission += commission
        
        broker.total_policies_sold = total_policies
        broker.total_premiums_collected = total_premiums
        broker.total_commission_earned = total_commission
        broker.last_activity = datetime.utcnow()
    
    db.commit()

def main():
    """Main function to populate the database with dummy data."""
    print("🚀 Starting database population...")
    
    # Get database session
    db = SessionLocal()
    
    try:
        print("🏢 Creating insurance companies...")
        companies = create_insurance_companies(db)
        print(f"✅ Created {len(companies)} insurance companies")
        
        print("👥 Creating admin users...")
        admins = create_admin_users(db, companies)
        print(f"✅ Created {len(admins)} admin users")
        
        print("🤝 Creating broker users and profiles...")
        brokers = create_broker_users_and_profiles(db, companies)
        print(f"✅ Created {len(brokers)} brokers")
        
        print("👤 Creating customer users...")
        customers = create_customer_users(db, count=50)
        print(f"✅ Created {len(customers)} customers")
        
        print("📋 Creating policies...")
        policies = create_policies(db, companies, brokers, customers)
        print(f"✅ Created {len(policies)} policies")
        
        print("💰 Creating premiums and payments...")
        create_premiums_and_payments(db, policies)
        print("✅ Created premiums and payment records")
        
        print("📈 Updating broker statistics...")
        update_broker_statistics(db, brokers)
        print("✅ Updated broker performance metrics")
        
        print("\n🎉 Database population completed successfully!")
        print("\n📋 Summary:")
        print(f"   • {len(companies)} Insurance Companies")
        print(f"   • {len(admins)} Admin Users")
        print(f"   • {len(brokers)} Brokers")
        print(f"   • {len(customers)} Customers")
        print(f"   • {len(policies)} Policies")
        print("   • Premiums and Payments for all policies")
        
        print("\n🔐 Default Login Credentials:")
        print("   Admin Users:")
        for admin in admins:
            print(f"     • {admin.email} / password123")
        print("   Broker Users:")
        for broker in brokers:
            print(f"     • {broker.user.email} / password123")
        
        print("\n🌟 Sample Dashboard Data Created:")
        print("   • Multiple brokers with varying performance")
        print("   • Various policy types with different payment statuses")
        print("   • Mix of paid, pending, and overdue premiums")
        print("   • Realistic insurance amounts in Naira")
        print("   • Commission tracking for brokers")
        
    except Exception as e:
        print(f"❌ Error during database population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
