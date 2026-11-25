from sqlalchemy import create_engine
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from model import Base, User
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os
from model import Championship, ChampionshipTeam, Driver, Race, RaceResult, Team, TeamApplication
from validation import POINTS_TABLE


ph = PasswordHasher()

DB_URL = os.getenv("DB_URL", "sqlite:///F1.db")
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)


#E1 :function for creation of organizer acount
def create_organizer_account( username , password ):
    session = Session (engine)
    organizer_account = User (
        username = username,
        password  = password,
        role = "organizer" ,
        created_at = datetime.now()
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

    
