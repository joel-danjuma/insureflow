from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import dependencies, models
from app.crud import broker as crud_broker
from app.schemas import broker as schemas_broker

router = APIRouter()

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