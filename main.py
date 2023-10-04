import enum
import databases
import sqlalchemy

from pydantic import BaseModel, validator
from fastapi import FastAPI, Request
from decouple import config
from email_validator import EmailNotValidError, validate_email

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:{config('DB_PORT')}/{config('DB_NAME')}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

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
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("FullName", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("Email", sqlalchemy.String(255)),
    sqlalchemy.Column("Password", sqlalchemy.String(255)),
    sqlalchemy.Column("Phone", sqlalchemy.String(13)),
    sqlalchemy.Column("CreatedDate_At", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("LastModified_At", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(),
                      onupdate=sqlalchemy.func.now())
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

class BaseUser(BaseModel):
  Email: str
  FullName: str

  @validator("Email")
  def isValidEmail(cls, email):
    try:
      validate_email(email)
      return email
    except EmailNotValidError:
      raise ValueError("Eamil is not valid")
   
  @validator("FullName")
  def Validate_Full_Name(cls, fullName):
    try:
      first_name, last_name = fullName.split()
    except Exception:
      raise ValueError("You should provide at least 2 names")
   

  
  
class UserSignIn(BaseUser):
  Password: str

app = FastAPI()

@app.on_event("startup")
async def startup():
 await database.connect()

@app.on_event("shutdown")
async def shutdown():
 await database.disconnect()

@app.get("/books/")
async def read_books():
 query = books.select()
 return await database.fetch_all(query)

@app.post("/books/")
async def create_book(request: Request):
 data = await request.json()
 query = books.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id": last_record_id}


@app.post("/readers/")
async def create_book(request: Request):
 data = await request.json()
 query = readers.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id": last_record_id}


@app.post("/read/")
async def read_book(request: Request):
 data = await request.json()
 query = readers_books.insert().values(**data)
 last_record_id = await database.execute(query)
 return {"id", last_record_id}

@app.post("/register")
async def create_user(user: UserSignIn):
 q = users.insert().values(**user.dict())
 id_ = await database.execute(q)
 return

 