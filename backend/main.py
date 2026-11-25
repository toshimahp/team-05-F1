from fastapi import FastAPI, HTTPException, Header
import function
from fastapi.middleware.cors import CORSMiddleware
from validation import OrganizerCreate, TeamCreate, ChampionshipCreate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ROLE= ["admin", "organizer" , "driver"]

# register endpoint
@app.post("/register")
def register_user(username, password, role):
    if function.register_user(username=username, password=password, role=role):
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=409, detail="user already exists")


#E1 - E5

#E1 : create organizer account
@app.post("/organizer_account")
def create_organizer_account (account:OrganizerCreate):
    return function.create_organizer_account(username=account.username, password=account.password)
