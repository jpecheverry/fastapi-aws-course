# fastapi-aws-course
Learn FastAPI by building a complete project. Extend my knowledge on advanced web development-AWS, Payments, Emails for Udemy course
## Commands to update database
alembic upgrade head
alembic revision --autogenerate -m "Initial"
## using the following command to start application 
uvicorn main:app --reload

## swagger 
http://127.0.0.1:8000/docs