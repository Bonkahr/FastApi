from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Path

from starlette import status

from models import Todo, Users
from database import db_dependency

from .auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix='/admin',
    tags=['Admin URLS']
)


async def user_role(db, user) -> str:
    """
    Returns the role if the current user
    :param db: database
    :param user: current user instance
    :return: the role of the current user
    """
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    print(current_user.role)
    return current_user.role


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    """
    Get all todos in the database
    :param user: current user
    :param db:  instance
    :return: all the todos in the database.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')

    if await user_role(db, user) == 'admin':
        return db.query(Todo).all()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='You are not authorized for this information.')


@router.delete('/todo/{todo_id}')
async def delete_todo(user: user_dependency, db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()

    if await user_role(db, user) == 'admin' and todo_model:
        if todo_model:
            db.delete(todo_model)
            db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                                detail=f'No todo with id of {todo_id}')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='You are not authorized for this information.')
