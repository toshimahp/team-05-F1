from fastapi import FastAPI, HTTPException, Header, Body
import function
from validation import (
    DriverCreate, TeamApplicationCreate, 
    ApplicationDecision, TeamRegisterRequest, 
    OrganizerCreate, ChampionshipCreate, TeamCreate, 
    LoginRequest, RegisterRequest)

app = FastAPI()
ROLE = ["admin", "organizer", "driver"]


# checks the access token and returns what is inside it
def authorize(token, allowed_roles):
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    payload = function.verify_token(token, "access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="You do not have the permission to do this")
    return payload


# if a function returned an error message, turn it into an HTTP error
def check_error(result, codes):
    if isinstance(result, str):
        raise HTTPException(status_code=codes.get(result, 400), detail=result)


# A1 register endpoint
@app.post("/register")
def register_user(creds: RegisterRequest):
    if function.register_user(username=creds.username, password=creds.password, role="driver"):
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=409, detail="user already exists")


# A2 logs in and gives access and refresh tokens
@app.post("/auth/login")
def login(creds: LoginRequest):
    result = function.login_user(creds.username, creds.password)
    check_error(result, {"invalid username or password": 401})
    return result


# A3 gives a new access token from a refresh token
@app.post("/auth/refresh")
def refresh(refresh_token: str = Header(None)):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    access_token = function.refresh_access_token(refresh_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": access_token}

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
@app.get("/racing_team/{team_id}")
def get_racing_team_by_id (team_id : int):
    return function.get_racing_team_by_id(team_id=team_id)

@app.post("/Championship")
def Championship (account:ChampionshipCreate, organizer_id: int = Header()):
    return function.create_championship( name= account.name, season= account.season, organizer_id = organizer_id, start_date = account.start_date, end_date = account.end_date)

#E6 - E10
# E6 gets all championships
@app.get("/championships")
def list_championships():
    return function.get_championships()


# E7 registers a driver profile (driver only)
@app.post("/drivers", status_code=201)
def create_driver(creds: DriverCreate, token: str = Header(None)):
    user = authorize(token, ["driver"])
    result = function.register_driver(
        user["user_id"], creds.full_name, creds.car_number, creds.nationality, creds.date_of_birth
    )
    check_error(result, {
        "driver profile already exists": 409,
        "car number already taken": 409,
    })
    return result


# E8 a driver applies to join a team
@app.post("/applications", status_code=201)
def apply_for_team(creds: TeamApplicationCreate, token: str = Header(None)):
    user = authorize(token, ["driver"])
    result = function.apply_to_team(user["user_id"], creds.team_id, creds.message)
    check_error(result, {
        "driver profile not found": 404,
        "team not found": 404,
        "driver is already in a team": 409,
        "already applied to this team": 409,
    })
    return result


# E9 the team manager accepts or rejects an application
@app.patch("/applications/{application_id}")
def decide_on_application(application_id: int, creds: ApplicationDecision, token: str = Header(None)):
    user = authorize(token, ROLE)
    result = function.decide_application(user["user_id"], application_id, creds.status)
    check_error(result, {
        "application not found": 404,
        "not your team": 403,
        "application already decided": 400,
        "team is full": 400,
        "driver is already in a team": 409,
    })
    return result


# E10 the team manager registers a team for a championship
@app.post("/championships/{championship_id}/teams", status_code=201)
def register_team_in_championship(championship_id: int, creds: TeamRegisterRequest, token: str = Header(None)):
    user = authorize(token, ROLE)
    result = function.register_team_for_championship(user["user_id"], championship_id, creds.team_id)
    check_error(result, {
        "championship not found": 404,
        "team not found": 404,
        "not your team": 403,
        "championship is completed": 400,
        "team already registered": 409,
    })
    return result


# E11 - E15 (Sam)
