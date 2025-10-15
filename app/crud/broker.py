from sqlalchemy.orm import Session
from app.models.broker import Broker
from app.schemas.broker import BrokerCreate
from app.schemas import broker as schemas_broker


def get_broker_by_user_id(db: Session, user_id: int):
    return db.query(Broker).filter(Broker.user_id == user_id).first()

def update_broker(db: Session, db_broker: Broker, broker_in: schemas_broker.BrokerUpdate):
    broker_data = broker_in.dict(exclude_unset=True)
    for key, value in broker_data.items():
        setattr(db_broker, key, value)
    db.add(db_broker)
    db.commit()
    db.refresh(db_broker)
    return db_broker


def create_broker_profile(db: Session, user_id: int, broker_data: dict) -> Broker:
    """
    Create a new broker profile and associate it with a user.
    """
    broker = Broker(
        user_id=user_id,
        **broker_data
    )
    db.add(broker)
    db.commit()
    db.refresh(broker)
    return broker 