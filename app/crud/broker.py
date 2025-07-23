from sqlalchemy.orm import Session
from app.models import broker
from app.schemas import broker as schemas_broker

def get_broker_by_user_id(db: Session, user_id: int):
    return db.query(broker.Broker).filter(broker.Broker.user_id == user_id).first()

def update_broker(db: Session, db_broker: broker.Broker, broker_in: schemas_broker.BrokerUpdate):
    broker_data = broker_in.dict(exclude_unset=True)
    for key, value in broker_data.items():
        setattr(db_broker, key, value)
    db.add(db_broker)
    db.commit()
    db.refresh(db_broker)
    return db_broker 