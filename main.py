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



