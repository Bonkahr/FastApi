from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos, admin, user

app = FastAPI()

# include admin routers
app.include_router(admin.router)

# include user routers
app.include_router(user.router)

# include all the routers in auth module
app.include_router(auth.router)

# include all the routers in todos module
app.include_router(todos.router)

# Create the database with all the data/tables in the model module.
models.Base.metadata.create_all(bind=engine)
