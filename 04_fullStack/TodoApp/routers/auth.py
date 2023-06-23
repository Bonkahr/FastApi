import sys

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from starlette.responses import RedirectResponse

from typing import Optional

from passlib.context import CryptContext

from jose import jwt, JWTError

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine


sys.path.append("..")

templates = Jinja2Templates(directory="templates")

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"


# class CreateUser(BaseModel):
#     username: str
#     email: Optional[str]
#     first_name: str
#     last_name: str
#     password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    prefix="/auth", tags=["auth"], responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.passowrd: Optional[str] = None

    async def create_outh_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")

        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        # raise get_user_exception()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )


# @router.post("/create/user")
# async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
#     create_user_model = models.Users()
#     create_user_model.email = create_user.email
#     create_user_model.username = create_user.username
#     create_user_model.first_name = create_user.first_name
#     create_user_model.last_name = create_user.last_name

#     hash_password = get_password_hash(create_user.password)

#     create_user_model.hashed_password = hash_password
#     create_user_model.is_active = True

#     db.add(create_user_model)
#     db.commit()


@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=False)
    return True


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Renders the login html page

    Args:
        request (Request): user request

    Returns:
        HTMLResponse: login html page
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.get('/profile', response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    """Get details of a logged in user and render the them to profile html

    Args:
        request (Request): User request
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        HTMLResponse: return the profile htm if the user is logged in else redirect to login page
    """
    user = await get_current_user(request)

    if user:
        profile = db.query(models.Users).filter(models.Users.id == user.get('id')).first()

        context = {
            'request': request,
            'user': user,
            'profile': profile
        }
        return templates.TemplateResponse('profile.html', context)
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)



@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """User login function. Checks whether the cookie is valid and logins in the user.
    After successful login, the user is redirected to his/her specific todos

    Args:
        request (Request): user request
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        returns the users todo or keeps the user in login till a successful login.
    """
    try:
        form = LoginForm(request)
        await form.create_outh_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"

            context = {"request": request, "msg": msg}
            return templates.TemplateResponse("login.html", context=context)
        return response
    except HTTPException:
        msg = "Unknown error occured."
        context = {"request": request, "msg": msg}
        return templates.TemplateResponse("login.html", context=context)


@router.get("/logout")
async def logout(request: Request):
    """LOgs out the user and deletes the access token

    Args:
        request (Request): user request

    Returns:
        HTMLResponse: login page with deleted cookie
    """
    msg = "Logout successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """Render the register html page

    Args:
        request (Request): the request

    Returns:
        HTMLResponse: the html page
    """
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def regiter(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    """Creates a new user and saves to the database.

    Args:
        request (Request): user request
        email (str, optional): user email. Defaults to Form(...).
        username (str, optional): user username. Defaults to Form(...).
        firstname (str, optional): user firstname. Defaults to Form(...).
        lastname (str, optional): user lastname. Defaults to Form(...).
        password (str, optional): user password. Defaults to Form(...).
        password2 (str, optional): user password confirmation. Defaults to Form.
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        HTMLResponse:return an error messade redirecting to the same register homepage or to login page
        if user successfully created.
    """
    validation1 = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    print(password == password2)
    print(password)
    print(password2)

    msg = ""
    if password != password2:
        msg = "Invalid password, passwords must match."
    elif len(password) < 6:
        msg = "Invalid password, password must have atleast 6 characters."
    elif validation1:
        msg = "Username already taken, choose another username."
    elif validation2:
        msg = f"User with email: {email} already exists."

    if msg:
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()
    msg = f"Welcome {firstname}. Your profile has been created."

    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/change_password", response_class=HTMLResponse)
async def password(request: Request):
    """renders the password change html

    Args:
        request (Request): user request

    Returns:
        _HTMLResponse:the html oage
    """
    user = await get_current_user(request)
    context = {"request": request, "user": user}
    return templates.TemplateResponse("change-password.html", context=context)


@router.post("/change_password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Gives a logged in user power to change his/her password

    Args:
        request (Request): user request
        current_password (str, optional): current password. Defaults to Form(...).
        new_password (str, optional): new password for the user. Defaults to Form(...).
        confirm_password (str, optional): new password confirmation. Defaults to Form(...).
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        HTMLResponse: redirects user to login after a successiful password change
    """
    user = await get_current_user(request)

    if user:
        user_model = (
            db.query(models.Users).filter(models.Users.id == user.get("id")).first()
        )

        if verify_password(current_password, user_model.hashed_password):
            msg = ""
            if new_password != confirm_password:
                msg = "Invalid password, passwords must match."
            elif len(new_password) < 6:
                msg = "Invalid password, password must have atleast 6 characters."

            if msg:
                context = {"request": request, "msg": msg, "user": user}
                return templates.TemplateResponse(
                    "change-password.html", context=context
                )

            user_password = get_password_hash(new_password)
            user_model.hashed_password = user_password
            msg = "Password changed successfully, login with your new password"
            db.add(user_model)
            db.commit()
            context = {"request": request, "msg": msg, "user": user}

            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )

        context = {
            "request": request,
            "msg": "You have entred incorrect current password!",
            "user": user,
        }
        return templates.TemplateResponse("change-password.html", context=context)

    context = {
        "request": request,
        "msg": "We have no idea how you landed here. You must be a hacker!",
        "user": user,
    }
    return templates.TemplateResponse("change-password.html", context=context)
