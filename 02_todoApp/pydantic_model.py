from pydantic import BaseModel, Field


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=5, max_length=100)
    priority: int = Field(ge=0, le=5)
    complete: bool

    class Config:
        schema_extra = {
            'example': {
                'title': 'Todo title',
                'description': 'Describe your todo',
                'priority': 4,
                'complete': False,
            }
        }


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    email: str = Field(min_length=5, max_length=50)
    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    password: str = Field()
    role: str = Field(min_length=3, max_length=15)

    class Config:
        schema_extra = {
            'example': {
                'username': 'username',
                'email': 'email@someone.com',
                'first_name': 'firstname',
                'last_name': 'lastname',
                'password': '1234',
                'role': 'admin'
            }
        }
