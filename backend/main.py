from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import functions
from validation import DriverCreate, TeamApplicationCreate, ApplicationDecision, TeamRegisterRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ROLE = ["admin", "organizer", "driver"]

# checks the access token and returns what is inside it
def authorize(token, allowed_roles):
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    payload = functions.verify_token(token, "access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="You do not have the permission to do this")
    return payload


# if a function returned an error message, turn it into an HTTP error
def check_error(result, codes):
    if isinstance(result, str):
        raise HTTPException(status_code=codes.get(result, 400), detail=result)

#E1 - E5
#E1 : create organizer account
@app.post("/organizer_account")
def create_organizer_account (username, password):
    result = function.create_organizer_account(username=username, password=password)
    
    
#E6 - E10
# E6 gets all championships
@app.get("/championships")
def list_championships():
    return functions.get_championships()


# E7 registers a driver profile (driver only)
@app.post("/drivers", status_code=201)
def create_driver(creds: DriverCreate, token: str = Header(None)):
    user = authorize(token, ["driver"])
    result = functions.register_driver(
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
    result = functions.apply_to_team(user["user_id"], creds.team_id, creds.message)
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
    result = functions.decide_application(user["user_id"], application_id, creds.status)
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
    result = functions.register_team_for_championship(user["user_id"], championship_id, creds.team_id)
    check_error(result, {
        "championship not found": 404,
        "team not found": 404,
        "not your team": 403,
        "championship is completed": 400,
        "team already registered": 409,
    })
    return result




#E11 - E15