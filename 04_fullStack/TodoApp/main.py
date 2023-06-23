from fastapi import FastAPI

from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

import models
from database import engine
from routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
async def root():
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
