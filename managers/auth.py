from datetime import datetime, timedelta
from typing import Optional

import databases
import jwt
from decouple import config
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models import user


class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
          paylod = {
             "sub": user["id"],
             "exp": datetime.now() + timedelta(minutes=120)
          }
          return jwt.encode(paylod, config("SECRET_KEY"), algorithm="HS256")
        except Exception as ex:
          #Log the exeption
          raise ex


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
       res = await super().__call__(request)

       try:
         payload = jwt.decode(res.credentials, config("SECRET_KEY"),  algorithms=["HS256"])
         user_data = await databases.fetch_one(user.select().where(user.c.id == payload["sub"]))
         request.state.user = user_data
         return user_data
       except jwt.ExpiredSignatureError:
         raise HTTPException(401, "Token expired")
       except jwt.InvalidTokenError:
          raise HTTPException(401, "Invalid token")


   