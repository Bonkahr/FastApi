from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {"id": 1, "title": "Title one", "author": "author one", "category":
        "science"},
    {"id": 2, "title": "Title Two", "author": "author two", "category":
        "science"},
    {"id": 3, "title": "Title Three", "author": "author three", "category":
        "math"},
    {"id": 4, "title": "Title Four", "author": "author one", "category":
        "history"},
    {"id": 5, "title": "Title Five", "author": "author two", "category":
        "math"},
]


# Home page
@app.get("/")
async def home():
    return {
        "Message": "Hello, you are in the homepage -> go to /books to get all "
                   "books."
    }


# Get all books
@app.get("/books")
async def books():
    # maths = []
    # science = []
    #
    # for book in BOOKS:
    #     match book["category"]:
    #         case "math":
    #             maths.append(book)
    #         case "science":
    #             science.append(book)
    #
    # return {"maths": maths, "science": science}
    return BOOKS


# get books filtered by passed category
@app.get('/books/')
async def filtered_books(category: str):
    fill_books = []
    for book in BOOKS:
        if category.casefold() == book['category'].casefold():
            fill_books.append(book)
    return fill_books if fill_books else {'Error': 'Category not in list.'}


# Path parameters. -> get books by passing the title.
@app.get('/books/{dynamic_param}')
async def read_all_books(dynamic_param: str):
    for book in BOOKS:
        if book['title'].casefold() == dynamic_param.casefold():
            return book
    return {'Error': 'Book not found.'}


# Get books from a specific author.
@app.get('/books/author/{author_name}')
async def get_books_by_author(author_name: str):
    books = []

    for book in BOOKS:
        if book.get('author').casefold() == author_name.casefold():
            books.append(book)

    return books if books else {"Error": f'No author by name {author_name}.'}


# Post requests -> Add a book in the BOOKS list.
@app.post('/books/add')
async def add_book(new_book: dict = Body()):
    for book in BOOKS:
        if new_book.get('id') == book.get('id'):
            return {'Error': f'Book with ID: {book.get("id")} exists.'}
    BOOKS.append(new_book)
    return BOOKS


# Put request -> update a specific book.
@app.put('/books/update_book')
async def update_book(updated_book: dict = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('id') == updated_book.get('id'):
            BOOKS[i] = updated_book
    return BOOKS


# Delete/ Destroy requests -> Delete a specific book.
@app.delete('/books/delete/{id}')
async def delete_book(id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('id') == id:
            BOOKS.pop(i)

    return BOOKS
