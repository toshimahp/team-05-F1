from fastapi import FastAPI, HTTPException, Header
import function
from fastapi.middleware.cors import CORSMiddleware
import OrganizerCreate, TeamCreate,TeamResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ROLE= ["admin", "organizer" , "driver"]

#E1 - E5

#E1 : create organizer account
@app.post("/organizer_account")
def create_organizer_account (account:OrganizerCreate):
    return function.create_organizer_account(username=account.username, password=account.password)
    
    
#E2 : create racing team
@app.post("/racing_team")
def create_racing_team (race: TeamCreate):
    return function.create_racing_team( name=race.name , country = race.country , manager_id = race.manager_id , max_drivers = race.max_drivers)

#E3 :get racing_team
@app.get("/racing_team")
def get_racing_team():
    return function.get_racing_team()

#E4 : get racing team through id
@app.get("racing_team/{team_id}")
def get_racing_team_by_id (race : TeamResponse):
    return function.get_racing_team_by_id(team_id=race["team_id"])

#E5 : creating  a Championship
    
#E6 - E10



#E11 - E15