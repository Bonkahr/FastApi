import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import auth, todos, admin, user

app = FastAPI()


# Consume the API from react middlewares settings
origins = [
    "http://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)