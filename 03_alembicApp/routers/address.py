import sys

from typing import Optional

from fastapi import Depends, APIRouter

from starlette import status

from sqlalchemy.orm import Session

from pydantic import BaseModel

import models
from database import engine, SessionLocal
from .auth import get_current_user, get_user_exception

sys.path.append('...')

router = APIRouter(
    prefix='/address',
    tags=['Address'],
    responses={404: {'description': 'Not found'}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Address(BaseModel):
    address_1: str
    address_2: str
    city: str
    state: str
    country: str
    postal_code: str


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_address(address: Address,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    address_model = models.Address()
    address_model.address_1 = address.address_1
    address_model.address_2 = address.address_2
    address_model.city = address.city
    address_model.state = address.state
    address_model.postal_code = address.postal_code

    db.add(address_model)
    db.flush()

    user_model = db.query(models.Users)\
        .filter(models.Users.id == user.get('id')).first()

    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()
