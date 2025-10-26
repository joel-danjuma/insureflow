"""
CRUD operations for Virtual Account model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.virtual_account import VirtualAccount, VirtualAccountStatus, VirtualAccountType
from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionStatus
from app.models.user import User


def get_virtual_account(db: Session, virtual_account_id: int) -> Optional[VirtualAccount]:
    """Get a virtual account by ID."""
    return db.query(VirtualAccount).filter(VirtualAccount.id == virtual_account_id).first()


def get_virtual_account_by_number(db: Session, virtual_account_number: str) -> Optional[VirtualAccount]:
    """Get a virtual account by account number."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.virtual_account_number == virtual_account_number
    ).first()


def get_virtual_account_by_customer_identifier(db: Session, customer_identifier: str) -> Optional[VirtualAccount]:
    """Get a virtual account by Squad customer identifier."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.customer_identifier == customer_identifier
    ).first()


def get_virtual_account_by_user(db: Session, user_id: int) -> Optional[VirtualAccount]:
    """Get the first virtual account for a user."""
    return db.query(VirtualAccount).filter(VirtualAccount.user_id == user_id).first()


def get_active_virtual_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[VirtualAccount]:
    """Get all active virtual accounts."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.status == VirtualAccountStatus.ACTIVE
    ).offset(skip).limit(limit).all()


def get_virtual_accounts_by_type(
    db: Session, 
    account_type: VirtualAccountType, 
    skip: int = 0, 
    limit: int = 100
) -> List[VirtualAccount]:
    """Get virtual accounts by type (individual or business)."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.account_type == account_type
    ).offset(skip).limit(limit).all()


def get_virtual_accounts_with_balance_above(
    db: Session, 
    minimum_balance: Decimal
) -> List[VirtualAccount]:
    """Get virtual accounts with balance above specified amount."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.current_balance >= minimum_balance
    ).all()


def get_virtual_accounts_for_settlement(db: Session) -> List[VirtualAccount]:
    """Get virtual accounts that are ready for auto-settlement."""
    return db.query(VirtualAccount).filter(
        VirtualAccount.auto_settlement == True,
        VirtualAccount.current_balance >= VirtualAccount.settlement_threshold,
        VirtualAccount.status == VirtualAccountStatus.ACTIVE
    ).all()


def create_virtual_account(db: Session, virtual_account_data: dict) -> VirtualAccount:
    """Create a new virtual account."""
    virtual_account = VirtualAccount(**virtual_account_data)
    db.add(virtual_account)
    db.commit()
    db.refresh(virtual_account)
    return virtual_account


def update_virtual_account_balance(
    db: Session, 
    virtual_account_id: int, 
    credit_amount: Decimal = None,
    debit_amount: Decimal = None
) -> Optional[VirtualAccount]:
    """Update virtual account balance."""
    virtual_account = get_virtual_account(db, virtual_account_id)
    if not virtual_account:
        return None
    
    if credit_amount:
        virtual_account.total_credits += credit_amount
        virtual_account.current_balance += credit_amount
    
    if debit_amount:
        virtual_account.total_debits += debit_amount
        virtual_account.current_balance -= debit_amount
    
    db.commit()
    db.refresh(virtual_account)
    return virtual_account


def update_virtual_account_status(
    db: Session, 
    virtual_account_id: int, 
    status: VirtualAccountStatus
) -> Optional[VirtualAccount]:
    """Update virtual account status."""
    virtual_account = get_virtual_account(db, virtual_account_id)
    if not virtual_account:
        return None
    
    virtual_account.status = status
    db.commit()
    db.refresh(virtual_account)
    return virtual_account


def update_virtual_account_commission_rates(
    db: Session,
    virtual_account_id: int,
    platform_commission_rate: Decimal = None,
    insureflow_commission_rate: Decimal = None,
    habari_commission_rate: Decimal = None
) -> Optional[VirtualAccount]:
    """Update commission rates for a virtual account."""
    virtual_account = get_virtual_account(db, virtual_account_id)
    if not virtual_account:
        return None
    
    if platform_commission_rate is not None:
        virtual_account.platform_commission_rate = platform_commission_rate
    
    if insureflow_commission_rate is not None:
        virtual_account.insureflow_commission_rate = insureflow_commission_rate
    
    if habari_commission_rate is not None:
        virtual_account.habari_commission_rate = habari_commission_rate
    
    db.commit()
    db.refresh(virtual_account)
    return virtual_account


def get_virtual_account_transactions(
    db: Session, 
    virtual_account_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[VirtualAccountTransaction]:
    """Get transactions for a virtual account."""
    return db.query(VirtualAccountTransaction).filter(
        VirtualAccountTransaction.virtual_account_id == virtual_account_id
    ).order_by(VirtualAccountTransaction.transaction_date.desc()).offset(skip).limit(limit).all()


def get_pending_transactions(db: Session) -> List[VirtualAccountTransaction]:
    """Get all pending transactions."""
    return db.query(VirtualAccountTransaction).filter(
        VirtualAccountTransaction.status == TransactionStatus.PENDING
    ).all()


def get_settlement_ready_transactions(db: Session) -> List[VirtualAccountTransaction]:
    """Get transactions that are ready for settlement."""
    return db.query(VirtualAccountTransaction).filter(
        VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
        VirtualAccountTransaction.merchant_settlement_date.is_(None),
        VirtualAccountTransaction.frozen_transaction == False
    ).all()


def get_total_commission_for_habari(db: Session) -> Decimal:
    """Calculate total commission amount for Habari across all accounts."""
    result = db.query(
        db.func.sum(VirtualAccount.total_credits * VirtualAccount.habari_commission_rate)
    ).scalar()
    return result or Decimal('0')


def get_total_commission_for_insureflow(db: Session) -> Decimal:
    """Calculate total commission amount for InsureFlow across all accounts."""
    result = db.query(
        db.func.sum(VirtualAccount.total_credits * VirtualAccount.insureflow_commission_rate)
    ).scalar()
    return result or Decimal('0')


def get_total_platform_commission(db: Session) -> Decimal:
    """Calculate total platform commission across all accounts."""
    result = db.query(
        db.func.sum(VirtualAccount.total_credits * VirtualAccount.platform_commission_rate)
    ).scalar()
    return result or Decimal('0')


def get_broker_performance_metrics(db: Session, user_id: int) -> dict:
    """Get performance metrics for a broker's virtual accounts."""
    virtual_accounts = get_virtual_account_by_user(db, user_id)
    
    total_credits = sum(va.total_credits for va in virtual_accounts)
    # Note: Broker commission would be separate from platform commission
    # This would be actual broker commissions paid out by the insurance company
    total_commission = Decimal('0')  # Would need separate broker commission tracking
    total_accounts = len(virtual_accounts)
    active_accounts = len([va for va in virtual_accounts if va.status == VirtualAccountStatus.ACTIVE])
    
    return {
        "total_credits": total_credits,
        "total_commission_earned": total_commission,
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "average_balance": total_credits / total_accounts if total_accounts > 0 else Decimal('0')
    }


def delete_virtual_account(db: Session, virtual_account_id: int) -> bool:
    """Delete a virtual account (soft delete by changing status)."""
    virtual_account = get_virtual_account(db, virtual_account_id)
    if not virtual_account:
        return False
    
    # Soft delete by changing status
    virtual_account.status = VirtualAccountStatus.CLOSED
    db.commit()
    return True 