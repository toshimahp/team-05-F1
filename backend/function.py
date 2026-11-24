from sqlalchemy import create_engine
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from model import Base, Feedback , User
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os

ph = PasswordHasher()

DB_URL = os.getenv("DB_URL", "sqlite:///feedback.db")
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)