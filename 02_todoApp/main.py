from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos

app = FastAPI()

# include all the routers in auth module
app.include_router(auth.router)

# include all the routers in todos module
app.include_router(todos.router)

# Create the database with all the data/tables in the models module.
models.Base.metadata.create_all(bind=engine)
