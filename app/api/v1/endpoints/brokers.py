from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import dependencies, models
from app.crud import broker as crud_broker
from app.schemas import broker as schemas_broker

router = APIRouter()

@router.get("/", response_model=List[schemas_broker.Broker])
def list_brokers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    current_user: models.user.User = Depends(dependencies.get_current_broker_or_admin_user)
):
    """
    List all brokers. Requires broker or admin access.
    """
    brokers = crud_broker.get_brokers(db, skip=skip, limit=limit)
    return brokers

@router.get("/me", response_model=schemas_broker.Broker)
def read_broker_me(
    current_user: models.user.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.user.UserRole.BROKER:
        raise HTTPException(status_code=403, detail="Not a broker")
    
    broker_profile = crud_broker.get_broker_by_user_id(db, user_id=current_user.id)
    if not broker_profile:
        raise HTTPException(status_code=404, detail="Broker profile not found")
    return broker_profile

@router.put("/me", response_model=schemas_broker.Broker)
def update_broker_me(
    broker_in: schemas_broker.BrokerUpdate,
    current_user: models.user.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.user.UserRole.BROKER:
        raise HTTPException(status_code=403, detail="Not a broker")

    broker_profile = crud_broker.get_broker_by_user_id(db, user_id=current_user.id)
    if not broker_profile:
        raise HTTPException(status_code=404, detail="Broker profile not found")
        
    updated_broker = crud_broker.update_broker(db, db_broker=broker_profile, broker_in=broker_in)
    return updated_broker 