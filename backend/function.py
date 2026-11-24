from sqlalchemy import create_engine
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from model import Base, Feedback , User
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os

ph = PasswordHasher()

DB_URL = os.getenv("DB_URL", "sqlite:///F1.db")
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)


def create_organizer_account( user_id , username , password ):
    session = Session (engine)
    organizer_account = User (
        user_id = user_id,
        username = username,
        password  = password,
        role = "organizer" ,
        created_at = datetime.date
    )
    
    session.add (organizer_account)
    session.commit()
    
    data = {
        "user_id" : organizer_account.user_id,
        "username" : organizer_account.username,
        "password"  : organizer_account.password,
        "role" : organizer_account.role ,
        "created_at" : organizer_account.created_at
    }
    session.close()
    return data


    