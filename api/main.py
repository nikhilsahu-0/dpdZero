from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.params import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# -------------------------------------- ERROR HANDLING ----------------------------
class GlobalException(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code


@app.exception_handler(GlobalException)
async def global_exception_handler(request: Request, exc: GlobalException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "code": exc.code, "message": exc.message},
    )


# ------------------------ VALIDATION & AUTHORIZATION FUNCTIONS -----------------------


def is_valid_password(password):
    [flag1, flag2, flag3, flag4] = [False, False, False, False]
    for c in password:
        flag1 = flag1 or c.islower()
        flag2 = flag2 or c.isupper()
        flag3 = flag3 or c.isdigit()
        flag4 = flag4 or c in "!@#$%^&*"

    return flag1 and flag2 and flag3 and flag4 and len(password) > 7


def check_token(authorization: str = Header(None)):
    if not authorization:
        return False
    fields = authorization.split(" ")
    return fields[1] == "fake_token_for_now_will_work"


# class User(BaseModel):
#     username: str
#     email: str
#     password: str
#     full_name: str
#     age: int
#     gender: str

# @app.get("/{id}")
# async def get_users(db: Session = Depends(get_db), id: int = 0):
#     users = db.query(models.User).filter(models.User.user_id == id).first()
#     return {"status": "Success", "data": users}

# -------------------------------- ROUNTER & ENDPOINTS----------------------------------


# ------------------------------- (1)USER REGISTRAION  ----------------------------------
@app.post("/api/register")
async def user_registration(new_user: dict = Body(None), db: Session = Depends(get_db)):
    if new_user == None or not {"username", "email", "password", "full_name"}.issubset(
        new_user.keys()
    ):
        raise GlobalException(
            "INVALID_REQUEST",
            "Invalid request. Please provide all required fields: username, email, password, full_name.",
            409,
        )
    username = (
        db.query(models.User)
        .filter(models.User.username == new_user["username"])
        .first()
    )
    if username != None:
        raise GlobalException(
            "USERNAME_EXISTS",
            "The provided username is already taken. Please choose a different username.",
            409,
        )
    email = db.query(models.User).filter(models.User.email == new_user["email"]).first()
    if email != None:
        raise GlobalException(
            "EMAIL_EXISTS",
            "The provided email is already registered. Please use a different email address.",
            409,
        )
    if not is_valid_password(new_user["password"]):
        raise GlobalException(
            "INVALID_PASSWORD",
            "The provided password does not meet the requirements. Password must be at least 8 characters long and contain a mix of uppercase and lowercase letters, numbers, and special characters.",
            409,
        )
    if "age" not in new_user or new_user["age"] < 0:
        raise GlobalException(
            "INVALID_AGE",
            "Invalid age value. Age must be a positive integer.",
            409,
        )
    if "gender" not in new_user:
        raise GlobalException(
            "GENDER_REQUIRED",
            "Gender field is required. Please specify the gender (e.g., male, female, non-binary).",
            409,
        )

    user = models.User(
        username=new_user["username"],
        email=new_user["email"],
        password=new_user["password"],
        full_name=new_user["full_name"],
        age=new_user["age"],
        gender=new_user["gender"],
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "status": "success",
            "message": "User successfully registered!",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "age": user.age,
                "gender": user.gender,
            },
        }
    except HTTPException as e:
        raise GlobalException(
            "INTERNAL_SERVER_ERROR",
            "An internal server error occurred. Please try again later.",
            500,
        )


# ------------------------------- (2)GENERATE TOKEN  ----------------------------------
@app.post("/api/token")
def generate_token(db: Session = Depends(get_db), payload: dict = Body(None)):
    print(payload)
    if not payload or "username" not in payload or "password" not in payload:
        raise GlobalException(
            "MISSING_FIELDS",
            "Missing fields. Please provide both username and password.",
            409,
        )

    user = (
        db.query(models.User)
        .filter(models.User.username == payload["username"])
        .first()
    )

    if not user or user.password != payload["password"]:
        raise GlobalException(
            "INVALID_CREDENTIALS",
            "Invalid credentials. The provided username or password is incorrect.",
            409,
        )
    try:
        token = jwt.encode(
            {
                "username": payload["username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            },
            "using_dummy_secret_key_for_now",
            algorithm="HS256",
        )
        return {
            "status": "success",
            "message": "Access token generated successfully.",
            "data": {"access_token": token, "expires_in": 3600},
        }
    except HTTPException as e:
        raise GlobalException(
            "INTERNAL_ERROR",
            "Internal server error occurred. Please try again later.",
            409,
        )


# ------------------------------- (3)STORE DATA  ----------------------------------
@app.post("/api/data")
def store_data(
    db: Session = Depends(get_db),
    payload: dict = Body(None),
    token_status: bool = Depends(check_token),
):
    if not token_status:
        raise GlobalException(
            "INVALID_TOKEN",
            "Invalid access token provided",
            409,
        )
    if not payload or "key" not in payload:
        raise GlobalException(
            "INVALID_KEY",
            "The provided key is not valid or missing",
            409,
        )
    elif "value" not in payload:
        raise GlobalException(
            "INVALID_VALUE",
            "The provided value is not valid or missing",
            409,
        )
    key_already_exist = (
        db.query(models.Data).filter(models.Data.key == payload["key"]).first()
    )
    if key_already_exist:
        raise GlobalException(
            "KEY_EXISTS",
            "The provided key already exists in the database. To update an existing key, use the update API",
            409,
        )
    new_post = models.Data(key=payload["key"], value=payload["value"])
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"status": "success", "message": "Data stored successfully."}


# ------------------------------- (4)RETRIEVE DATA  ----------------------------------
@app.get("/api/data/{key}")
def retrieve_data(
    key: str = None,
    token_status: bool = Depends(check_token),
    db: Session = Depends(get_db),
):
    if not token_status:
        raise GlobalException(
            "INVALID_TOKEN",
            "Invalid access token provided",
            409,
        )
    if key:
        data = db.query(models.Data).filter(models.Data.key == key).first()
        if data:
            return {"status": "success", "data": {"key": data.key, "value": data.value}}
    raise GlobalException(
        "KEY_NOT_FOUND",
        "The provided key does not exist in the database",
        404,
    )


# ------------------------------- (5)UPDATE DATA  ----------------------------------
@app.put("/api/data/{key}")
def update_data(
    key: str = None,
    token_status: bool = Depends(check_token),
    db: Session = Depends(get_db),
    payload: dict = Body(None),
):
    if not token_status:
        raise GlobalException(
            "INVALID_TOKEN",
            "Invalid access token provided",
            409,
        )
    if key:
        data_query = db.query(models.Data).filter(models.Data.key == key)
        if data_query.first():
            data_query.update({"value": payload["value"]}, synchronize_session=False)
            db.commit()
            return {"status": "success", "message": "Data updated successfully."}
    raise GlobalException(
        "KEY_NOT_FOUND",
        "The provided key does not exist in the database",
        404,
    )


# ------------------------------- (6)DELETE DATA  ----------------------------------
@app.delete("/api/data/{key}")
def delete_data(
    key: str = None,
    token_status: bool = Depends(check_token),
    db: Session = Depends(get_db),
):
    if not token_status:
        raise GlobalException(
            "INVALID_TOKEN",
            "Invalid access token provided",
            409,
        )
    if key:
        data_query = db.query(models.Data).filter(models.Data.key == key)
        if data_query.first():
            data_query.delete(synchronize_session=False)
            db.commit()
            return {"status": "success", "message": "Data deleted successfully."}
    raise GlobalException(
        "KEY_NOT_FOUND",
        "The provided key does not exist in the database",
        404,
    )
