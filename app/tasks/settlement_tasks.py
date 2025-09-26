"""
Background tasks for settlement processing.
"""
import asyncio
import logging
from datetime import datetime

from app.core.database import get_db
from app.services.settlement_service import settlement_service

logger = logging.getLogger(__name__)

async def daily_settlement_task():
    """
    Daily settlement task to be run by scheduler.
    Processes all pending settlements automatically.
    """
    logger.info("Starting daily settlement task")
    
    db = next(get_db())
    try:
        result = await settlement_service.process_daily_settlements(db)
        
        if result.get("success"):
            logger.info(f"Daily settlement completed successfully: {result.get('settlements_processed', 0)} settlements processed")
        else:
            logger.error(f"Daily settlement failed: {result.get('error')}")
            
        return result
    except Exception as e:
        logger.error(f"Daily settlement task failed with exception: {str(e)}")
        return {"error": f"Task failed: {str(e)}"}
    finally:
        db.close()

async def hourly_settlement_check():
    """
    Hourly check for high-value transactions that need immediate settlement.
    """
    logger.info("Starting hourly settlement check")
    
    db = next(get_db())
    try:
        from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionStatus
        from app.core.config import settings
        from decimal import Decimal
        
        # Check for high-value transactions (above threshold * 10)
        high_value_threshold = Decimal(str(settings.SETTLEMENT_THRESHOLD * 10))
        
        high_value_transactions = db.query(VirtualAccountTransaction).filter(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            VirtualAccountTransaction.settlement_status == 'pending',
            VirtualAccountTransaction.settled_amount >= high_value_threshold
        ).all()
        
        if high_value_transactions:
            logger.info(f"Found {len(high_value_transactions)} high-value transactions for immediate settlement")
            
            # Group by firm and process
            firms_to_settle = {}
            for transaction in high_value_transactions:
                from app.models.virtual_account import VirtualAccount
                
                virtual_account = db.query(VirtualAccount).filter(
                    VirtualAccount.id == transaction.virtual_account_id
                ).first()
                
                if virtual_account and virtual_account.policy:
                    firm_id = virtual_account.policy.company_id
                    if firm_id not in firms_to_settle:
                        firms_to_settle[firm_id] = []
                    firms_to_settle[firm_id].append(transaction)
            
            # Process settlements for each firm
            results = []
            for firm_id, transactions in firms_to_settle.items():
                result = await settlement_service._process_firm_settlement(db, firm_id, transactions)
                results.append(result)
                
                if result.get("success"):
                    logger.info(f"High-value settlement completed for firm {firm_id}")
                else:
                    logger.error(f"High-value settlement failed for firm {firm_id}: {result.get('error')}")
            
            return {"success": True, "high_value_settlements": len(results), "results": results}
        else:
            logger.info("No high-value transactions found for immediate settlement")
            return {"success": True, "message": "No high-value transactions to process"}
            
    except Exception as e:
        logger.error(f"Hourly settlement check failed: {str(e)}")
        return {"error": f"Hourly check failed: {str(e)}"}
    finally:
        db.close()

async def settlement_status_monitor():
    """
    Monitor settlement status and send alerts for failed settlements.
    """
    logger.info("Starting settlement status monitor")
    
    db = next(get_db())
    try:
        from app.models.virtual_account_transaction import VirtualAccountTransaction
        from datetime import timedelta
        
        # Check for transactions pending settlement for more than 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        stale_transactions = db.query(VirtualAccountTransaction).filter(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            VirtualAccountTransaction.settlement_status == 'pending',
            VirtualAccountTransaction.transaction_date < cutoff_time
        ).all()
        
        if stale_transactions:
            logger.warning(f"Found {len(stale_transactions)} stale transactions pending settlement")
            
            # Could send alerts here (email, Slack, etc.)
            # For now, just log the details
            total_amount = sum(t.settled_amount for t in stale_transactions)
            logger.warning(f"Total amount in stale settlements: ₦{total_amount}")
            
            return {
                "success": True,
                "stale_transactions_found": len(stale_transactions),
                "total_stale_amount": float(total_amount)
            }
        else:
            logger.info("No stale transactions found")
            return {"success": True, "message": "No stale transactions"}
            
    except Exception as e:
        logger.error(f"Settlement status monitor failed: {str(e)}")
        return {"error": f"Monitor failed: {str(e)}"}
    finally:
        db.close()

# Task scheduler setup (to be used with APScheduler or similar)
def setup_settlement_scheduler():
    """
    Set up scheduled tasks for settlement processing.
    This function should be called during app startup.
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        import atexit
        
        scheduler = AsyncIOScheduler()
        
        # Daily settlement at 2 AM
        scheduler.add_job(
            daily_settlement_task,
            CronTrigger(hour=2, minute=0),
            id='daily_settlement',
            name='Daily Settlement Processing',
            replace_existing=True
        )
        
        # Hourly high-value check
        scheduler.add_job(
            hourly_settlement_check,
            CronTrigger(minute=0),
            id='hourly_settlement_check',
            name='Hourly High-Value Settlement Check',
            replace_existing=True
        )
        
        # Settlement monitor every 6 hours
        scheduler.add_job(
            settlement_status_monitor,
            CronTrigger(hour='0,6,12,18', minute=30),
            id='settlement_monitor',
            name='Settlement Status Monitor',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Settlement scheduler started successfully")
        
        # Ensure scheduler shuts down when app exits
        atexit.register(lambda: scheduler.shutdown())
        
        return scheduler
        
    except ImportError:
        logger.warning("APScheduler not installed. Settlement scheduling disabled.")
        logger.warning("Install APScheduler to enable automatic settlements: pip install apscheduler")
        return None
    except Exception as e:
        logger.error(f"Failed to setup settlement scheduler: {str(e)}")
        return None
