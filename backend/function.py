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


def create_organizer_account( user_id , username , password ):
    session = Session (engine)
    organizer_account = User (
        user_id = user_id,
        username = username,
        password  = password,
        role = "organizer" ,
        created_at = datetime.now(timezone.utc)
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

#1 - E5


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




# samhita functions (E11 - E15)
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
