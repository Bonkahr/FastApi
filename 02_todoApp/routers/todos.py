from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Depends

from starlette import status

from models import Todo
from database import db_dependency
from pydantic_model import TodoRequest

from .auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix='/todo',
    tags=['todo URLS']
)


@router.get('/user', status_code=status.HTTP_200_OK)
async def get_user_todos(db: db_dependency, user: user_dependency):
    """
    Get to_do of a specific user.
    :param db: database instance
    :param user: current user
    :return: to_do items
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')
    user_todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()
    return user_todos


@router.get('/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency,
                   todo_id: int = Path(gt=0)):
    """
    Get a specific to_do by the use of id for a specific user
    :param user: current user
    :param db: the database
    :param todo_id: the id of the to_do list
    :return: the specific to do if it exists else raise exception 404.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')

    todo = db.query(Todo).filter(Todo.owner_id == user.get('id')).filter(
        Todo.id == todo_id).first()

    if todo:
        return todo

    raise HTTPException(status_code=204,
                        detail=f"User {user.get('username')} has no to "
                               f"do with id {todo_id}.")


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      to_do: TodoRequest):
    """
    Create a to_do
    :param user: the owner
    :param db: the database
    :param to_do: to_do created
    :return: all to_dos
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed.')
    db.add(Todo(**to_do.dict(), owner_id=user.get('id')))
    db.commit()
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()[-1]


@router.put('/update/{todo_id}', status_code=status.HTTP_201_CREATED)
async def update_todo(db: db_dependency, to_do: TodoRequest,
                      user: user_dependency, todo_id: int = Path(gt=0)):
    """
    Update a selected to_do
    :param user: current user
    :param db: the database
    :param to_do: to_do instance to update
    :param todo_id: id of selected to_do
    :return: return the updated to_do
    """
    todo_to_update = db.query(Todo).filter(Todo.owner_id == user.get(
        'id')).filter(Todo.id == todo_id).first()

    if not todo_to_update:
        raise HTTPException(status_code=404,
                            detail=f'No to do with id: {todo_id}')

    todo_to_update.title = to_do.title
    todo_to_update.description = to_do.description
    todo_to_update.priority = to_do.priority
    todo_to_update.complete = to_do.complete
    todo_to_update.owner_id = user.get('id')

    db.add(todo_to_update)
    db.commit()

    updated_todo = db.query(Todo).filter(Todo.owner_id == user.get(
        'id')).filter(Todo.id == todo_id).first()
    return updated_todo


@router.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int):
    """
    Delete a specific to_do item using its id
    :param user: current user
    :param db: the database
    :param todo_id: the to_do item id to delete
    :return: None
    """
    todo_to_update = db.query(Todo).filter(Todo.owner_id == user.get(
        'id')).filter(Todo.id == todo_id).first()

    if not todo_to_update:
        raise HTTPException(status_code=404,
                            detail=f'No to do with id: {todo_id}')
    db.delete(todo_to_update)
    db.commit()
