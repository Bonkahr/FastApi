from pydantic import BaseModel, Field

from typing import Optional


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: float
    publish_year: int

    def __init__(self, id, title, author, description, rating, publish_year):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publish_year = publish_year


class BookRequest(BaseModel):
    id: Optional[int] = Field(title='generated automatically')
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=5, max_length=100)
    rating: float = Field(ge=0.0, le=5.0)
    publish_year: int = Field(gt=1600, le=2027)

    class Config:
        schema_extra = {
            'example': {
                'title': 'The new book title',
                'author': 'author name',
                'description': 'what is the book about?',
                'rating': 2.3,
                'publish_year': 1678
            }
        }


if __name__ == '__main__':
    pass
