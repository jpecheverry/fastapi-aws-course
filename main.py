import databases
import sqlalchemy

from fastapi import FastAPI, Request

DATABASE_URL = "postgresql://postgres:Anto2021@localhost:5438/store_aws"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("Id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("Title", sqlalchemy.String),
    sqlalchemy.Column("Author", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

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