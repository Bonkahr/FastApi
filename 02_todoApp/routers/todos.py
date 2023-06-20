from fastapi import APIRouter, HTTPException, Path


from starlette import status

from models import Todo
from database import db_dependency
from pydantic_model import TodoRequest

router = APIRouter(
    prefix='/todo',
    tags=['todo URLS']
)


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    """
    Get all todos in the database
    :param db:  instance
    :return: all the todos in the database.
    """
    return db.query(Todo).all()


@router.get('/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    """
    Get a specific to_do by the use of id
    :param db: the database
    :param todo_id: the id of the to_do list
    :return: the specific to do if it exists else raise the 404 exception.
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail=f'No item with id :{todo_id}')


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, to_do: TodoRequest):
    """
    Create a to_do
    :param db: te database
    :param to_do: the to_do created
    :return: all to_dos
    """
    db.add(Todo(**to_do.dict()))
    db.commit()
    return db.query(Todo).all()


@router.put('/update/{todo_id}', status_code=status.HTTP_201_CREATED)
async def update_todo(db: db_dependency, to_do: TodoRequest,
                      todo_id: int = Path(gt=0)):
    """
    Update a selected to_do
    :param db: the database
    :param to_do: the to_do instance to update
    :param todo_id: the id of selected to_do
    :return: return the updated to_do
    """
    todo_to_update = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo_to_update:
        raise HTTPException(status_code=404,
                            detail=f'No to do with id: {todo_id}')

    todo_to_update.title = to_do.title
    todo_to_update.description = to_do.description
    todo_to_update.priority = to_do.priority
    todo_to_update.complete = to_do.complete

    db.add(todo_to_update)
    db.commit()

    updated_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    return updated_todo


@router.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int):
    """
    Delete a specific to_do item using its id
    :param db: the database
    :param todo_id: the to_do item id to delete
    :return: None
    """
    todo_to_update = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo_to_update:
        raise HTTPException(status_code=404,
                            detail=f'No to do with id: {todo_id}')
    db.delete(todo_to_update)
    db.commit()
