from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status

from data import Book, BookRequest

app = FastAPI()

BOOKS = [
    Book(1, 'Computer Science', 'Tim Bulkhead', 'Programming algorithms',
         4.6, 2012),
    Book(2, 'Advanced Maths', 'James Dolphin', 'Pure mathematics', 2.6, 2023),
    Book(3, 'Paper loose', 'Harun Micheal', 'When everyone looses papers',
         1.5, 1994),
    Book(4, 'When Time Runs', 'James Bond', 'Time is not on your side', 3.7,
         2004),
    Book(5, 'Python', 'Finland Sidney', 'Learn Python programming', 5, 2001),
    Book(6, 'Learn Physics', 'Peter Czech', 'The daily physics rule', 4.6,
         1643),
    Book(7, 'Home Away', 'Paper Mines', 'Never run away from home', 3.8, 2017)
]


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


# Get all books
@app.get('/books', status_code=status.HTTP_200_OK)
async def all_books():
    return BOOKS


# Get a book using an id.
@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found.')


# Get books depending on published year ranges
@app.get('/books/year_published/', status_code=status.HTTP_200_OK)
async def publish_year(min_year: int = Query(gt=1600),
                       max_year: int = Query(lt=2027)):
    books = []
    for book in BOOKS:
        if max_year >= book.publish_year >= min_year:
            books.append(book)
    return books


# Get books according to the rating.
@app.get('/books/', status_code=status.HTTP_200_OK)
async def book_rating(rating: float = Query(ge=0, le=5)):
    books = []
    for book in BOOKS:
        if rating + 0.5 >= book.rating >= rating - 0.5:
            books.append(book)
    return books


# create an instance of Book
@app.post('/create_book', status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    # creating a book of type BookRequest and converting it to Book object.
    new_book = Book(**book.dict())
    BOOKS.append(find_book_id(new_book))
    return BOOKS


# Update a given book
@app.put('/books/update/{book_id}', status_code=status.HTTP_200_OK)
async def update_book(book_update: BookRequest, book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            updated_book = Book(**book_update.dict())
            updated_book.id = book_id
            BOOKS[i] = updated_book
            return BOOKS
    else:
        raise HTTPException(status_code=404, detail=f'No book with id:'
                                                    f' {book_id}.')


# Delete  a given book
@app.delete('/books/delete/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            return BOOKS
    else:
        raise HTTPException(status_code=404, detail=f'No book with id:'
                                                    f' {book_id}.')
