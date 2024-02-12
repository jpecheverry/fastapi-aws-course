from datetime import datetime, timedelta
from typing import Optional

import enum
import jwt
from passlib.context import CryptContext
from click import DateTime
import databases
import sqlalchemy

from pydantic import BaseModel, validator
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from decouple import config
from email_validator import EmailNotValidError, validate_email as validate_e

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:{config('DB_PORT')}/{config('DB_NAME')}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CustomHTTPBearer(HTTPBearer):
   async def __call__(
         self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
    res = await super().__call__(request)
    try:
      payload = jwt.decode(res.credentials, config("JWT_SECRET"), algorithms=["HS256"])
      user = await database.fetch_one(users.select().where(users.c.id == payload["sub"]))
      request.state.user = user
      return payload
    except jwt.ExpiredSignatureError:
      raise HTTPException(401, "Token is expired")     
    except jwt.InvalidTokenError:
       raise HTTPException(401, "Invalid token")     


oauth2_scheme = CustomHTTPBearer()

def is_admin(request: Request):
   user = request.state.user
   if not user or user["role"] not in (UserRole.admin, UserRole.super_admin):
      raise HTTPException(403, "You do not have permissions for this resource")
 
def create_access_token(user): 
   try:
     payload = {"sub": user["id"], "exp": datetime.now() + timedelta(minutes=2400)}
     return jwt.encode(payload, config("JWT_SECRET"), algorithm="HS256")
   except Exception as ex:
     raise ex   

def hash_password(password):
    # Hash a password using bcrypt
    hashed_password = pwd_context.hash(password) 
    return hashed_password


class UserRole(enum.Enum):
   super_admin = "super_admin"
   admin = "admin"
   user= "user"

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("Title", sqlalchemy.String),
    sqlalchemy.Column("Author", sqlalchemy.String),
    sqlalchemy.Column("Pages", sqlalchemy.Integer)
)

readers = sqlalchemy.Table(
    'readers',
    metadata,
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("FirstName", sqlalchemy.String),
    sqlalchemy.Column("LastName", sqlalchemy.String)
 )

readers_books = sqlalchemy.Table(
    'read_books',
    metadata,
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("Book_Id", sqlalchemy.ForeignKey('books.Id'), nullable=False),
    sqlalchemy.Column("Read_Id", sqlalchemy.ForeignKey('readers.Id'), nullable=False)
 )

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("full_name", sqlalchemy.String(120)),
    sqlalchemy.Column("email", sqlalchemy.String(255)),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("last_modified_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(),
                      onupdate=sqlalchemy.func.now()),
    sqlalchemy.Column("role", sqlalchemy.Enum(UserRole), nullable=False, server_default=UserRole.user.name)
 )

class ColorEnum(enum.Enum):
    Pink = "Pink"
    Black = "Black"
    White = "White"
    Yellow = "Yellow"

class SizeEnum(enum.Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    Xl = "Xl"
    XXL = "XXL"

clothes = sqlalchemy.Table(
    'clothes',
    metadata,
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("Name", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("Color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("Size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("Photo_Url", sqlalchemy.String(255)),
    sqlalchemy.Column("CreatedDate_At", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("LastModified_At", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(),
                      onupdate=sqlalchemy.func.now())
 )  


class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> str:
        try:
            validate_e(v)
            return v
        except EmailNotValidError:
            raise ValueError("Email is not valid")


class BaseUser(BaseModel):
    email: str
    full_name: Optional[str]

    @validator("full_name")
    def validate_full_name(cls, v):
        try:
            first_name, last_name = v.split()
            return v
        except Exception:
            raise ValueError("You should provide at least 2 names")
    
    @validator("email")
    def validate_email(cls, v) -> str:
       try:
         validate_e(v)
         return v
       except EmailNotValidError:
           raise ValueError("Email is not valid")


class UserSignIn(BaseUser):
    password: str


class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime

class ClothesBase(BaseModel):
   Name: str
   Color: str
   Size: SizeEnum
   Color: ColorEnum

class ClothesIn(ClothesBase):
   pass

class ClothesOut(ClothesBase):
   Id: int
   CreatedDate_At: datetime
   LastModified_At: datetime

app = FastAPI()


@app.on_event("startup")
async def startup():
 await database.connect()

@app.on_event("shutdown")
async def shutdown():
 await database.disconnect()

@app.get("/books/")
async def read_books():
 return await database.fetch_all(books.select())

@app.post("/books/")
async def create_book(request: Request):
 data = await request.json()
 query = books.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id": last_record_id}


@app.post("/readers/")
async def create_reader(request: Request):
 data = await request.json()
 query = readers.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id": last_record_id}


@app.post("/read/")
async def readers_book(request: Request):
 data = await request.json()
 query = readers_books.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id", last_record_id}

@app.get("/clothes", dependencies=[Depends(oauth2_scheme)])
async def get_all_clothes():    
    return await database.fetch_all(clothes.select())

@app.post("/clothes/",  response_model=ClothesOut, 
                        dependencies=[Depends(oauth2_scheme), 
                        Depends(is_admin)], 
                        status_code=201)
async def create_clothes(clothes_data:ClothesIn):
   id = await database.execute(clothes.insert().values(**clothes_data.dict())) 
   return await database.fetch_one(clothes.select().where(clothes.c.Id == id))
 
 
@app.post("/register", status_code=201)
async def create_user(user: UserSignIn):
 user.password = hash_password(user.password) 
 q = users.insert().values(**user.dict())
 id_ = await database.execute(q)
 created_user = await database.fetch_one(users.select().where(users.c.id == id_))
 token = create_access_token(created_user)
 return {"token": token}


 