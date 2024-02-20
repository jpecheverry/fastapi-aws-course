# fastapi-aws-course
Learn FastAPI by building a complete project. Extend my knowledge on advanced web development-AWS, Payments, Emails for Udemy course

## Commands to update database
pip install databases
pip install alembic
pip install databases asyncpg psycopg2-binary
pip install asyncpg psycopg2 psycopg2-binary sqlalchemy
alembic init migration -> This Command create the Migration folder

alembic revision --autogenerate -m "Initial"
alembic upgrade head

## using the following command to start application 
Use pip intall uvicorn
uvicorn main:app --reload

## swagger 
http://127.0.0.1:8000/docs

## JWT_SECRET
It is a best practice to use UUID.uuid4 to generate the key and paste into the .env configuration file


## Setp-up

python -m venv venv
CTRL + ALT + O -> This command order the imports