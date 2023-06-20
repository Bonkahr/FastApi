from datetime import timedelta, datetime

from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel

from starlette import status

from passlib.context import CryptContext

from jose import jwt, JWTError

from database import db_dependency
from pydantic_model import CreateUserRequest
from models import Users

router = APIRouter(
    prefix='/auth',
    tags=['auth URLS']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# string generated with 'openssl rand -hex 32' terminal command (for JWT)
SECRET_KEY = 'abda313a46b25929e2397f14cb80e34f2ba412f332655076e7d92a3318dc4878'
ALGORITHM = 'HS256'


class Token(BaseModel):
    """
    Creates the response body of the token generated.
    """
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):
    """
    Searches the user from the database, decrypt the entered password and
    finds if they match.
    If the user exits and password matches, return True.
    :param username: The username of the user
    :param password: The password passed by the user
    :param db: the database
    :return: the user instance.
    """
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f'User with username: '
                                   f'{username} does not exist.')

    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Password Mismatch '
                                   f'for user: {username}')
    return user


def create_access_token(username: str, user_id: int, expiry_time: timedelta):
    """
    Generate user access token using user's email, and id.
    :param username: User's username
    :param user_id: User's id
    :param expiry_time: expiry time if the token
    :return: the generated token
    """
    encode = {'sub': username, 'id': user_id}
    expire = datetime.utcnow() + expiry_time
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')

        if not username and user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user.')


@router.get('/users', status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    """
    Query and return all registered users
    :param db: the database
    :return: all users
    """
    return db.query(Users).all()


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    """
    Create a user and save it to the database.
    :param db: The database
    :param create_user_request: the user instance
    :return: the user instance *not needed anyway*
    """
    create_user_model = Users(
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        username=create_user_request.username,
        email=create_user_request.email,
        is_active=True,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    try:
        db.add(create_user_model)
        db.commit()
    except:
        raise HTTPException(status_code=404, detail='Username or email '
                                                    'already in use.')


@router.post('/tokens', response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(db: db_dependency, form_data: Annotated[
    OAuth2PasswordRequestForm, Depends()]):
    """
    :param db:
    :param form_data:
    :return:
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.username, user.id, timedelta(
        minutes=120))

    return {'access_token': token, 'token_type': 'bearer'}
