from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel, Field

from starlette import status

from models import Users
from database import db_dependency
from .auth import get_current_user, bcrypt_context

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix='/user',
    tags=['User URLS']
)


class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_len=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def user_info(db: db_dependency, user: user_dependency):
    """
    Get the current user information
    :param db: database
    :param user: current user.
    :return: User information
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    return current_user


@router.put('/change_password', status_code=status.HTTP_201_CREATED)
async def change_password(user: user_dependency, db: db_dependency,
                          change_password_request: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')

    current_user_model = db.query(Users).filter(Users.id == user.get(
        'id')).first()

    if not bcrypt_context.verify(change_password_request.current_password,
                                 current_user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Your password is not correct')
    current_user_model.hashed_password = bcrypt_context.hash(
        change_password_request.new_password
    )
    db.add(current_user_model)
    db.commit()
