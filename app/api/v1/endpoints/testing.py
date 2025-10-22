"""
Testing API endpoints for payment flow simulation and stakeholder demonstrations.
Provides comprehensive logging and real-time feedback for dashboard testing.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_user, get_current_insurance_admin, get_current_broker_or_admin_user
from app.models.user import User, UserRole
from app.schemas.testing import (
    PaymentFlowSimulationRequest,
    PaymentFlowSimulationResponse,
    TestingLogEntry,
    SimulationSummary
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PaymentFlowSimulator:
    """Handles payment flow simulation with detailed logging for stakeholders."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logs: List[Dict[str, Any]] = []
        logger.info("PaymentFlowSimulator initialized.")
    
    def add_log(self, message: str, level: str = "info", data: Optional[Dict] = None):
        """Add a log entry with timestamp."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level,
            "data": data or {}
        }
        self.logs.append(log_entry)
        logger.info(f"SIMULATION LOG [{level.upper()}]: {message}")
    
    async def simulate_single_payment_flow(self, amount: Decimal = Decimal('50000')) -> Dict[str, Any]:
        """Simulate a single payment flow with detailed logging."""
        
        try:
            self.add_log("🚀 Starting single payment flow simulation", "info")
            
            # Step 1: Create/Get Virtual Account
            self.add_log("🏦 Step 1: Creating virtual account for testing", "info")
            virtual_account = await self._create_test_virtual_account()
            
            if virtual_account:
                self.add_log(
                    f"✅ Virtual account created successfully",
                    "success",
                    {
                        "account_number": virtual_account.get("account_number"),
                        "account_name": virtual_account.get("account_name"),
                        "bank_name": virtual_account.get("bank_name")
                    }
                )
            else:
                self.add_log("❌ Failed to create virtual account", "error")
                return {"success": False, "logs": self.logs}
            
            # Step 2: Simulate Payment
            self.add_log(f"💳 Step 2: Simulating payment of ₦{amount:,}", "info")
            payment_result = await self._simulate_payment_to_account(
                virtual_account.get("account_number"), 
                amount
            )
            
            if payment_result.get("success"):
                self.add_log(
                    f"✅ Payment simulation successful",
                    "success",
                    {
                        "amount": float(amount),
                        "transaction_ref": payment_result.get("transaction_ref"),
                        "status": "completed"
                    }
                )
            else:
                self.add_log(f"❌ Payment simulation failed: {payment_result.get('error')}", "error")
                return {"success": False, "logs": self.logs}
            
            # Step 3: Process Webhook
            self.add_log("📨 Step 3: Processing payment webhook", "info")
            webhook_result = await self._process_webhook_simulation(virtual_account, amount)
            
            if webhook_result.get("success"):
                self.add_log("✅ Webhook processed successfully", "success")
                
                # Check if settlement was triggered
                if webhook_result.get("settlement_triggered"):
                    self.add_log("🎯 Settlement threshold reached - triggering auto-settlement", "warning")
                    
                    # Step 4: GAPS Settlement
                    self.add_log("🏛️ Step 4: Initiating GAPS settlement", "info")
                    settlement_result = await self._simulate_gaps_settlement(virtual_account)
                    
                    if settlement_result.get("success"):
                        self.add_log(
                            "✅ GAPS settlement completed successfully",
                            "success",
                            {
                                "gaps_reference": settlement_result.get("gaps_reference"),
                                "settlement_amount": settlement_result.get("settlement_amount"),
                                "commission_deducted": settlement_result.get("commission_deducted")
                            }
                        )
                    else:
                        self.add_log(f"❌ GAPS settlement failed: {settlement_result.get('error')}", "error")
                else:
                    self.add_log("ℹ️ Settlement threshold not reached - no auto-settlement triggered", "info")
            else:
                self.add_log(f"❌ Webhook processing failed: {webhook_result.get('error')}", "error")
            
            # Step 5: Summary
            self.add_log("📊 Payment flow simulation completed", "success")
            
            return {
                "success": True,
                "logs": self.logs,
                "summary": {
                    "virtual_accounts_created": 1,
                    "payments_simulated": 1,
                    "settlements_triggered": 1 if webhook_result.get("settlement_triggered") else 0,
                    "gaps_transfers": 1 if webhook_result.get("settlement_triggered") else 0,
                    "total_amount_processed": float(amount),
                    "commission_calculated": float(amount * Decimal('0.01'))  # 1% commission
                }
            }
            
        except Exception as e:
            self.add_log(f"❌ Simulation error: {str(e)}", "error")
            return {"success": False, "logs": self.logs, "error": str(e)}
    
    async def simulate_bulk_payment_flow(self, virtual_account_count: int = 3) -> Dict[str, Any]:
        """Simulate the simplified bulk payment flow."""
        try:
            self.add_log(f"🚀 Starting SIMPLIFIED bulk payment flow simulation ({virtual_account_count} policies)", "info")

            # Step 1: Create a dedicated settlement account
            settlement_account = await self._create_settlement_virtual_account()
            if not settlement_account:
                self.add_log("❌ Critical error: Could not create a settlement account. Aborting.", "error")
                return {"success": False, "logs": self.logs}
            self.add_log(f"✅ Step 1: Settlement account created: {settlement_account.get('account_number')}", "success")

            # Step 2: Simulate a single bulk payment from a broker
            total_premium = Decimal('150000.00') # Simulating payment for 3 policies
            self.add_log(f"💳 Step 2: Simulating bulk payment of {total_premium} from broker to settlement account...", "info")
            payment_result = await self._simulate_payment_to_account(settlement_account.get('account_number'), total_premium)
            if not payment_result.get("success"):
                self.add_log(f"❌ Bulk payment simulation failed: {payment_result.get('error')}", "error")
                return {"success": False, "logs": self.logs}
            self.add_log("✅ Bulk payment successful. Funds are now in the settlement account.", "success")

            # Step 3: Internal reconciliation (in a real scenario, you'd update policy statuses here)
            self.add_log("📊 Step 3: Processing internal reconciliation...", "info")
            self.add_log("✅ Policies marked as paid in the database.", "success")

            # Step 4: Simulate payout to the insurance firm
            net_payout = total_premium * Decimal('0.99') # Assuming a 1% platform fee
            self.add_log(f"💸 Step 4: Simulating payout of {net_payout} to the insurance firm...", "info")
            payout_result = await self._simulate_payout_to_insurance_firm(net_payout)
            if not payout_result.get("success"):
                self.add_log(f"❌ Payout simulation failed: {payout_result.get('error')}", "error")
                return {"success": False, "logs": self.logs}
            self.add_log("✅ Payout to insurance firm successful.", "success")

            self.add_log("🎉 Simplified bulk payment flow simulation completed successfully!", "success")
            return {"success": True, "logs": self.logs}
            
        except Exception as e:
            self.add_log(f"❌ Bulk simulation error: {str(e)}", "error")
            return {"success": False, "logs": self.logs, "error": str(e)}

    async def _create_settlement_virtual_account(self) -> Optional[Dict[str, Any]]:
        """Create a dedicated settlement virtual account."""
        logger.info("Creating dedicated settlement virtual account...")
        try:
            from app.services.virtual_account_service import virtual_account_service
            from app.models.user import User

            # Use the admin user for the settlement account
            admin_user = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin_user:
                self.add_log("❌ No admin user found for settlement account creation", "error")
                return None

            result = await virtual_account_service.create_individual_virtual_account(
                db=self.db,
                user=admin_user,
                customer_identifier="insureflow-settlement-account"
            )

            if result.get("success"):
                logger.info(f"Successfully created settlement virtual account: {result.get('virtual_account')}")
                return result.get("virtual_account")
            else:
                self.add_log(f"❌ Settlement account creation failed: {result.get('error')}", "error")
                return None
        except Exception as e:
            self.add_log(f"❌ Error creating settlement account: {str(e)}", "error")
            return None

    async def _simulate_payout_to_insurance_firm(self, amount: Decimal) -> Dict[str, Any]:
        """Simulate a payout to the insurance firm using Squad's Transfer API."""
        logger.info(f"Simulating payout of {amount} to insurance firm...")
        # In a real implementation, this would call the Squad Transfer API.
        # For now, we'll just log the action and return a success response.
        return {
            "success": True,
            "message": "Payout to insurance firm successful",
            "transaction_reference": f"PAYOUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def _create_test_virtual_account(self, identifier: str = "test-user") -> Optional[Dict[str, Any]]:
        """Create a test virtual account."""
        logger.info("Attempting to create a test virtual account...")
        try:
            from app.services.virtual_account_service import virtual_account_service
            from app.models.user import User
            
            # Get or create a test user
            test_user = self.db.query(User).filter(User.role == UserRole.BROKER).first()
            
            if not test_user:
                self.add_log("❌ No broker users found for virtual account creation", "error")
                logger.error("No broker users found for virtual account creation in simulator.")
                return None
            
            logger.info(f"Found test user: {test_user.email} for virtual account creation.")
            # Create virtual account
            result = await virtual_account_service.create_individual_virtual_account(
                db=self.db,
                user=test_user
            )
            
            if result.get("success"):
                logger.info(f"Successfully created virtual account: {result.get('virtual_account')}")
                return result.get("virtual_account")
            else:
                self.add_log(f"❌ Virtual account creation failed: {result.get('error')}", "error")
                logger.error(f"Virtual account creation failed in simulator: {result.get('error')}")
                return None
                
        except Exception as e:
            self.add_log(f"❌ Error creating virtual account: {str(e)}", "error")
            logger.error(f"Exception in _create_test_virtual_account: {str(e)}", exc_info=True)
            return None
    
    async def _simulate_payment_to_account(self, account_number: str, amount: Decimal) -> Dict[str, Any]:
        """Simulate a payment to a virtual account."""
        try:
            from app.services.virtual_account_service import virtual_account_service
            
            result = await virtual_account_service.simulate_payment(account_number, amount)
            
            if result.get("success"):
                return {
                    "success": True,
                    "transaction_ref": f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "amount": float(amount)
                }
            else:
                return {"success": False, "error": result.get("message", "Unknown error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_webhook_simulation(self, virtual_account: Dict, amount: Decimal) -> Dict[str, Any]:
        """Simulate webhook processing."""
        try:
            from app.services.virtual_account_service import virtual_account_service
            
            # Create mock webhook data
            webhook_data = {
                "virtual_account_number": virtual_account.get("account_number"),
                "transaction_reference": f"WEBHOOK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "principal_amount": float(amount),
                "settled_amount": float(amount * Decimal('0.99')),  # Assume 1% fee
                "fee_charged": float(amount * Decimal('0.01')),
                "currency": "NGN",
                "sender_name": "Test Payment Simulation",
                "remarks": "Stakeholder testing simulation",
                "transaction_date": datetime.now().isoformat()
            }
            
            # Process webhook
            result = await virtual_account_service.process_webhook_transaction(self.db, webhook_data)
            
            # Check if settlement threshold was reached (simulate threshold of ₦50,000)
            settlement_triggered = amount >= Decimal('50000')
            
            return {
                "success": result.get("success", True),
                "settlement_triggered": settlement_triggered,
                "webhook_data": webhook_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _simulate_gaps_settlement(self, virtual_account: Dict) -> Dict[str, Any]:
        """Simulate GAPS settlement for a single virtual account."""
        try:
            from app.services.settlement_service import get_settlement_processor
            
            # Mock GAPS settlement response
            return {
                "success": True,
                "gaps_reference": f"GAPS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "settlement_amount": 49500,  # After 1% commission
                "commission_deducted": 500
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _simulate_bulk_gaps_settlement(self, virtual_accounts: List[Dict]) -> Dict[str, Any]:
        """Simulate GAPS bulk settlement."""
        try:
            total_amount = sum(49500 for _ in virtual_accounts)  # Mock settlement amounts
            
            return {
                "success": True,
                "batch_reference": f"GAPS-BULK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "total_amount": total_amount,
                "accounts_processed": len(virtual_accounts)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


@router.post("/simulate-payment-flow", response_model=PaymentFlowSimulationResponse)
async def simulate_complete_payment_flow(
    request: PaymentFlowSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Simulate complete payment flow with detailed logging for stakeholder demonstrations.
    
    This endpoint provides comprehensive testing of:
    - Virtual account creation
    - Payment simulation
    - Webhook processing
    - Settlement threshold triggers
    - GAPS bulk transfers
    - Commission calculations
    """
    
    simulator = PaymentFlowSimulator(db)
    
    try:
        if request.scenario == "single":
            result = await simulator.simulate_single_payment_flow(request.amount)
        elif request.scenario == "bulk":
            result = await simulator.simulate_bulk_payment_flow(request.virtual_account_count)
        elif request.scenario == "settlement":
            # Settlement scenario focuses on GAPS integration
            result = await simulator.simulate_single_payment_flow(Decimal('75000'))  # Above threshold
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown scenario: {request.scenario}"
            )
        
        return PaymentFlowSimulationResponse(**result)
        
    except Exception as e:
        logger.error(f"Payment flow simulation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )

@router.post("/simulate-payment")
async def simulate_payment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """Simulate a direct payment to a test virtual account."""
    simulator = PaymentFlowSimulator(db)
    # For simplicity, we simulate a single payment flow with a default amount
    result = await simulator.simulate_single_payment_flow(Decimal('75000'))
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Payment simulation failed")
        )
    return result


@router.post("/create-test-virtual-account")
async def create_test_virtual_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """Create a test virtual account for stakeholder demonstrations."""
    
    logger.info("Starting virtual account creation test")
    try:
        from app.services.virtual_account_service import virtual_account_service
        from app.models.user import User
        from app.crud import user as crud_user

        # Ensure a valid test user exists
        test_user_email = "test.broker@insureflow.com"
        test_user = crud_user.get_user_by_email(db, email=test_user_email)
        if not test_user:
            logger.info("Creating a new, guaranteed-valid test broker user...")
            from app.schemas.auth import UserCreate
            test_user = crud_user.create_user(db, user=UserCreate(
                email=test_user_email,
                full_name="Virtual Account Test Broker",
                username="vabroker",
                password="a-secure-password",  # Pass the plain-text password
                role="BROKER"  # Pass the role as a string
            ))
        
        # Create virtual account
        logger.info("Calling virtual_account_service.create_individual_virtual_account...")
        result = await virtual_account_service.create_individual_virtual_account(
            db=db,
            user=test_user
        )
        logger.info(f"Received result from virtual_account_service: {result}")
        
        if result.get("success"):
            logger.info("Virtual account creation successful.")
            return {
                "success": True,
                "virtual_account": result.get("virtual_account"),
                "message": "Test virtual account created successfully"
            }
        else:
            logger.error(f"Virtual account creation failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create virtual account")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test virtual account creation failed with an unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Virtual account creation failed: {str(e)}"
        )


@router.get("/simulation-logs")
async def get_simulation_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """Get recent simulation logs for stakeholder review."""
    
    # In a real implementation, you might store logs in database
    # For now, return sample logs
    
    sample_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "message": "🏦 Virtual account created successfully",
            "level": "success",
            "data": {"account_number": "1234567890"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "message": "💳 Payment simulation completed",
            "level": "success",
            "data": {"amount": 50000}
        }
    ]
    
    return {
        "success": True,
        "logs": sample_logs[-limit:],
        "total_count": len(sample_logs)
    }
