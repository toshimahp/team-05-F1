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
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 

def register_user(username, password, role):
    session = Session(engine)
    user_exist = session.query(User).filter_by(username =username).first()
    if user_exist is not None:
        session.close()
        return False
    
    try:
        hashed_password = ph.hash(password)
    except Exception:
        session.close()
        return False
    
    session.add(User(username= username, password= hashed_password, role= role))
    session.commit()
    session.close()
    return True

#E1 :function for creation of organizer acount (admin only)
def create_organizer_account( username , password ):
    session = Session (engine)
    existing = session.query(User).filter(User.username == username).first()
    if existing is not None:
        session.close()
        return False

    organizer_account = User (
        username = username,
        password  = ph.hash(password),
        role = "organizer" ,
        created_at = datetime.now()
    )
    
    session.add (organizer_account)
    session.commit()
    
    data = {
        "user_id" : organizer_account.user_id,
        "username" : organizer_account.username,
        "role" : organizer_account.role ,
        "created_at" : organizer_account.created_at
    }
    session.close()
    return data

#E2 : function for creation of racing team (admin only)
def create_racing_team( name , country,manager_id, max_drivers ):
    session = Session (engine)
    racing_team = Team (
        name = name,
        country = country,
        manager_id = manager_id ,
        max_drivers = max_drivers,
        created_at = datetime.now()
    )
    
    session.add (racing_team)
    session.commit()
    
    data = {
        "team_id" : racing_team.team_id,
        "name" : name,
        "country" : country,
        "manager_id" : manager_id ,
        "max_drivers" : max_drivers,
        "created_at" : racing_team.created_at
    }
    session.close()
    return data

   
#E3 : geting all racing team (all)
def get_racing_team ():
    session = Session(engine)
    racing_team = session.query(Team).all()
    
    data = []
    for race_team in racing_team:
        data.append ({
            "team_id" : race_team.team_id,
            "name" : race_team.name,
            "country" : race_team.country,
            "manager_id" : race_team.manager_id ,
            "max_drivers" : race_team.max_drivers,
            "created_at" : race_team.created_at
        })
        
    session.close()
    return data


#E4 : geting details of particular team through team_id
def get_racing_team_by_id (team_id):
    session = Session(engine)
    racing_team = session.query(Team).filter(Team.team_id == team_id).all()
    
    data = []
    for race_team in racing_team:
        data.append ({
            "team_id" : race_team.team_id,
            "name" : race_team.name,
            "country" : race_team.country,
            "manager_id" : race_team.manager_id ,
            "max_drivers" : race_team.max_drivers,
            "created_at" : race_team.created_at
        })
        
    session.close()
    return data
    
    
#E5 : create a championship
def create_championship( name, season, organizer_id, start_date, end_date, status = "upcoming"):
    session = Session(engine)
    championship =  Championship(
            name = name,
            season = season,
            organizer_id = organizer_id, 
            start_date = start_date,
            end_date = end_date,
            status = status , # upcoming / ongoing / completed
            created_at = datetime.now()
        )
        
    session.add (championship)
    session.commit()
    
    data = {
        "champ_id" : championship.champ_id , 
        "name" : championship.name,
        "season" :  championship.season,
        "organizer_id" : championship.organizer_id, 
        "start_date" : championship.start_date,
        "end_date" : championship.end_date, 
        "status" : championship.status , # upcoming / ongoing / completed
        "created_at" : championship.created_at
    }
    session.close()
    return data



# E6 - E10
# helper turns a championship row into a dictionary
def championship_to_dict(championship):
    return {
        "champ_id": championship.champ_id,
        "name": championship.name,
        "season": championship.season,
        "organizer_id": championship.organizer_id,
        "start_date": championship.start_date,
        "end_date": championship.end_date,
        "status": championship.status,
    }


# helper turns a driver row into a dictionary
def driver_to_dict(driver):
    return {
        "driver_id": driver.driver_id,
        "user_id": driver.user_id,
        "full_name": driver.full_name,
        "car_number": driver.car_number,
        "nationality": driver.nationality,
        "date_of_birth": driver.date_of_birth,
        "team_id": driver.team_id,
    }


# helper turns an application row into a dictionary
def application_to_dict(application):
    return {
        "application_id": application.application_id,
        "driver_id": application.driver_id,
        "team_id": application.team_id,
        "status": application.status,
        "message": application.message,
        "applied_at": application.applied_at,
        "reviewed_at": application.reviewed_at,
    }
    
# E6 gets all championships
def get_championships():
    session = Session(engine)
    result = []
    for championship in session.query(Championship):
        result.append(championship_to_dict(championship))
    session.close()
    return result

# E7 registers a driver profile for the logged in user (driver only)
def register_driver(user_id, full_name, car_number, nationality, date_of_birth=None):
    session = Session(engine)
    for row in session.query(Driver):
        if row.user_id == user_id:
            session.close()
            return "driver profile already exists"
        if row.car_number == car_number:
            session.close()
            return "car number already taken"

    driver = Driver(
        user_id=user_id,
        full_name=full_name,
        car_number=car_number,
        nationality=nationality,
        date_of_birth=date_of_birth,
    )
    session.add(driver)
    session.commit()
    data = driver_to_dict(driver)
    session.close()
    return data


# E8 the logged in driver applies to join a team (driver only)
def apply_to_team(user_id, team_id, message=None):
    session = Session(engine)

    # finds the driver profile of this user
    driver = None
    for row in session.query(Driver):
        if row.user_id == user_id:
            driver = row
    if driver is None:
        session.close()
        return "driver profile not found"

    team = session.get(Team, team_id)
    if team is None:
        session.close()
        return "team not found"

    if driver.team_id is not None:
        session.close()
        return "driver is already in a team"

    for row in session.query(TeamApplication):
        if row.driver_id == driver.driver_id and row.team_id == team_id and row.status == "pending":
            session.close()
            return "already applied to this team"

    application = TeamApplication(
        driver_id=driver.driver_id,
        team_id=team_id,
        message=message,
        status="pending",
    )
    session.add(application)
    session.commit()
    data = application_to_dict(application)
    session.close()
    return data


# E9 the team manager accepts or rejects an application (status is "accepted" or "rejected") (manager only)
def decide_application(user_id, application_id, status):
    session = Session(engine)

    application = session.get(TeamApplication, application_id)
    if application is None:
        session.close()
        return "application not found"

    team = session.get(Team, application.team_id)
    if team.manager_id != user_id:
        session.close()
        return "not your team"

    if application.status != "pending":
        session.close()
        return "application already decided"

    if status == "accepted":
        driver = session.get(Driver, application.driver_id)
        if driver.team_id is not None:
            session.close()
            return "driver is already in a team"

        # counts the drivers already in this team
        count = 0
        for row in session.query(Driver):
            if row.team_id == team.team_id:
                count = count + 1
        if count >= team.max_drivers:
            session.close()
            return "team is full"

        driver.team_id = team.team_id

    application.status = status
    application.reviewed_at = datetime.now()
    session.commit()
    data = application_to_dict(application)
    session.close()
    return data


# E10 the team manager registers a team for a championship  (manager only)
def register_team_for_championship(user_id, championship_id, team_id):
    session = Session(engine)

    championship = session.get(Championship, championship_id)
    if championship is None:
        session.close()
        return "championship not found"

    team = session.get(Team, team_id)
    if team is None:
        session.close()
        return "team not found"

    if team.manager_id != user_id:
        session.close()
        return "not your team"

    if championship.status == "completed":
        session.close()
        return "championship is completed"

    for row in session.query(ChampionshipTeam):
        if row.championship_id == championship_id and row.team_id == team_id:
            session.close()
            return "team already registered"

    entry = ChampionshipTeam(championship_id=championship_id, team_id=team_id)
    session.add(entry)
    session.commit()
    data = {
        "champ_team_id": entry.champ_team_id,
        "championship_id": entry.championship_id,
        "team_id": entry.team_id,
        "registered_at": entry.registered_at,
    }
    session.close()
    return data



# samhita function (E11 - E15)
# helper func turns a race row into a dictionary
def race_to_dict(race):
    return {
        "race_id": race.race_id,
        "championship_id": race.championship_id,
        "name": race.name,
        "circuit": race.circuit,
        "country": race.country,
        "round_number": race.round_number,
        "race_date": race.race_date,
        "status": race.status,
        "results_published": race.results_published,
    }

# E11 schedules a race in a championship
def schedule_race(championship_id, organizer_id, name, race_date, circuit="TBD", country="TBD"):
    session = Session(engine)
    championship = session.query(Championship).filter(Championship.champ_id == championship_id).first()
    if championship is None:
        session.close()
        return "championship not found"
    if championship.organizer_id != organizer_id:
        session.close()
        return "not your championship"
    if championship.status == "completed":
        session.close()
        return "this championship season is completed, cannot schedule new races"

    existing_races = session.query(Race).filter(Race.championship_id == championship_id).all()
    round_number = len(existing_races) + 1

    race = Race(
        championship_id=championship_id,
        name=name,
        circuit=circuit,
        country=country,
        round_number=round_number,
        race_date=race_date,
    )
    session.add(race)
    session.commit()
    session.refresh(race)
    result = race_to_dict(race)
    session.close()
    return result


# E12 gets all races of a championship
def get_races(championship_id):
    session = Session(engine)
    championship = session.query(Championship).filter(Championship.champ_id == championship_id).first()
    if championship is None:
        session.close()
        return "championship not found"

    races = session.query(Race).filter(Race.championship_id == championship_id).order_by(Race.round_number).all()
    result = []
    for race in races:
        result.append(race_to_dict(race))
    session.close()
    return result


# E13 submits the results of a race
def submit_results(race_id, organizer_id, results):
    session = Session(engine)
    race = session.query(Race).filter(Race.race_id == race_id).first()
    if race is None:
        session.close()
        return "race not found"

    championship = session.query(Championship).filter(Championship.champ_id == race.championship_id).first()
    if championship.organizer_id != organizer_id:
        session.close()
        return "not your championship"
    if race.results_published:
        session.close()
        return "results already published"

    # shows the team ids registered for this championship
    registered = session.query(ChampionshipTeam).filter(ChampionshipTeam.championship_id == race.championship_id).all()
    registered_team_ids = []
    for entry in registered:
        registered_team_ids.append(entry.team_id)

    # checks every driver first so nothing is saved if one of them is invalid
    rows = []
    for item in results:
        driver = session.query(Driver).filter(Driver.driver_id == item.driver_id).first()
        if driver is None:
            session.close()
            return "driver not found"
        if driver.team_id is None:
            session.close()
            return "driver has no team"
        if driver.team_id not in registered_team_ids:
            session.close()
            return "team not registered in championship"

        points = POINTS_TABLE.get(item.position, 0)
        rows.append(RaceResult(
            race_id=race_id,
            driver_id=driver.driver_id,
            team_id=driver.team_id,
            position=item.position,
            points=points,
            fastest_lap=item.fastest_lap,
            fastest_lap_time=item.fastest_lap_time,
        ))

    for row in rows:
        session.add(row)
    race.results_published = True
    race.status = "completed"
    session.commit()

    race_results = []
    for row in rows:
        race_results.append({
            "result_id": row.result_id,
            "race_id": row.race_id,
            "driver_id": row.driver_id,
            "team_id": row.team_id,
            "position": row.position,
            "points": row.points,
            "fastest_lap": row.fastest_lap,
            "fastest_lap_time": row.fastest_lap_time,
        })
    session.close()
    return race_results

# helper for sorting standings, more points first then more wins
def standing_key(entry):
    return (-entry["points"], -entry["wins"])

# E14 gets the standings of a championship from published results
def get_standings(championship_id):
    session = Session(engine)
    championship = session.query(Championship).filter(Championship.champ_id == championship_id).first()
    if championship is None:
        session.close()
        return "championship not found"

    races = session.query(Race).filter(Race.championship_id == championship_id, Race.results_published == True).all()

    driver_points = {}
    driver_wins = {}
    driver_team = {}
    team_points = {}
    team_wins = {}

    # every registered team shows up even with 0 points
    registered = session.query(ChampionshipTeam).filter(ChampionshipTeam.championship_id == championship_id).all()
    for entry in registered:
        team_points[entry.team_id] = 0
        team_wins[entry.team_id] = 0

    # adds up the points race by race
    for race in races:
        race_results = session.query(RaceResult).filter(RaceResult.race_id == race.race_id).all()
        for result in race_results:
            if result.driver_id not in driver_points:
                driver_points[result.driver_id] = 0
                driver_wins[result.driver_id] = 0
            if result.team_id not in team_points:
                team_points[result.team_id] = 0
                team_wins[result.team_id] = 0

            driver_points[result.driver_id] += result.points
            team_points[result.team_id] += result.points
            driver_team[result.driver_id] = result.team_id
            if result.position == 1:
                driver_wins[result.driver_id] += 1
                team_wins[result.team_id] += 1

    # driver standings
    driver_entries = []
    for driver_id in driver_points:
        driver = session.query(Driver).filter(Driver.driver_id == driver_id).first()
        driver_entries.append({
            "driver_id": driver_id,
            "full_name": driver.full_name,
            "team_id": driver_team[driver_id],
            "points": driver_points[driver_id],
            "wins": driver_wins[driver_id],
        })
    driver_entries.sort(key=standing_key)

    driver_standings = []
    place = 1
    for entry in driver_entries:
        driver_standings.append({
            "position": place,
            "driver_id": entry["driver_id"],
            "full_name": entry["full_name"],
            "team_id": entry["team_id"],
            "points": entry["points"],
        })
        place += 1

    # team standings
    team_entries = []
    for team_id in team_points:
        team = session.query(Team).filter(Team.team_id == team_id).first()
        team_entries.append({
            "team_id": team_id,
            "team_name": team.name,
            "points": team_points[team_id],
            "wins": team_wins[team_id],
        })
    team_entries.sort(key=standing_key)

    team_standings = []
    place = 1
    for entry in team_entries:
        team_standings.append({
            "position": place,
            "team_id": entry["team_id"],
            "team_name": entry["team_name"],
            "points": entry["points"],
        })
        place += 1

    session.close()
    return {
        "championship_id": championship_id,
        "driver_standings": driver_standings,
        "team_standings": team_standings,
    }


# helper for sorting history by race date
def history_key(entry):
    return entry["race_date"]

# E15 gets the performance history of a driver
def get_driver_history(driver_id):
    session = Session(engine)
    driver = session.query(Driver).filter(Driver.driver_id == driver_id).first()
    if driver is None:
        session.close()
        return "driver not found"

    results = session.query(RaceResult).filter(RaceResult.driver_id == driver_id).all()
    history = []
    total_points = 0
    for result in results:
        race = session.query(Race).filter(Race.race_id == result.race_id).first()
        history.append({
            "race_id": race.race_id,
            "race_name": race.name,
            "round_number": race.round_number,
            "championship_id": race.championship_id,
            "race_date": race.race_date,
            "team_id": result.team_id,
            "position": result.position,
            "points": result.points,
            "fastest_lap": result.fastest_lap,
        })
        total_points += result.points
    history.sort(key=history_key)

    session.close()
    return {
        "driver_id": driver_id,
        "full_name": driver.full_name,
        "total_points": total_points,
        "history": history,
    }


# A1 registering a new user
def register_user(username, password, role):
    session = Session(engine)
    user_exist = session.query(User).filter_by(username =username).first()
    if user_exist is not None:
        session.close()
        return False
    
    try:
        hashed_password = ph.hash(password)
    except Exception:
        session.close()
        return False
    
    session.add(User(username= username, password= hashed_password, role= role))
    session.commit()
    session.close()
    return True

# A2 login
# create token function
def create_token(user_id, role, username, token_type):
    time = ACCESS_TOKEN_EXPIRY 
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "user_id": user_id,
        "role": role,
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time),
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

# A2 checks the username and password and gives access and refresh tokens
def login_user(username, password):
    session = Session(engine)
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        session.close()
        return "invalid username or password"

    try:
        ph.verify(user.password, password)
    except Exception:
        session.close()
        return "invalid username or password"

    user_id = user.user_id
    role = user.role
    session.close()

    return {
        "access_token": create_token(user_id, role, username, "access"),
        "refresh_token": create_token(user_id, role, username, "refresh"),
    }
    
    
    
# A3 checks a token and returns what is inside it, or None if it is bad
def verify_token(token, token_type):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None

    if payload["token_type"] != token_type:
        return None
    return payload


# A3 takes a refresh token and gives back a new access token string
def refresh_access_token(refresh_token):
    payload = verify_token(refresh_token, "refresh")
    if payload is None:
        return None

    # checks that the user still exists in the database
    session = Session(engine)
    user = session.query(User).filter(User.user_id == payload["user_id"]).first()
    if user is None:
        session.close()
        return None

    user_id = user.user_id
    role = user.role
    username = user.username
    session.close()

    return create_token(user_id, role, username, "access")
