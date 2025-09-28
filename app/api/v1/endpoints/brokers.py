from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import dependencies, models
from app.crud import broker as crud_broker
from app.schemas import broker as schemas_broker

router = APIRouter()

@router.get("/me")
def read_broker_me(
    current_user: models.user.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.user.UserRole.BROKER:
        raise HTTPException(status_code=403, detail="Not a broker")
    
    # Return basic user info as broker profile for now
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "organization_name": current_user.organization_name,
        "phone_number": current_user.phone_number,
        "is_active": current_user.is_active,
        "role": current_user.role.value
    }

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