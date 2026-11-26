import os
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from model import Base, User, Team, Driver, TeamApplication, Championship, ChampionshipTeam, Race, RaceResult

# fills an EMPTY database with sample data for testing
# run it from the backend folder:  python seed_data.py
# it uses the same DB_URL setting as the app, so it follows whatever database the app would use

DB_URL = os.getenv("DB_URL", "sqlite:///F1.db")
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
ph = PasswordHasher()

PASSWORD = "pass123"  # every seeded account uses this password

# points table from the prd
POINTS_TABLE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


def seed_database():
    session = Session(engine)

    # safety check, never seed on top of existing data
    if session.query(User).first() is not None:
        print("The database already has users, so nothing was changed.")
        print("Rename or delete the database file first, then run this again.")
        session.close()
        return

    # ---------- users (ids 1 to 8) ----------
    users = [
        (1, "admin1", "admin"),
        (2, "organizer1", "organizer"),
        (3, "manager_redbull", "team_manager"),
        (4, "manager_ferrari", "team_manager"),
        (5, "driver_max", "driver"),
        (6, "driver_sergio", "driver"),
        (7, "driver_charles", "driver"),
        (8, "driver_carlos", "driver"),
    ]
    for user_id, username, role in users:
        session.add(User(
            user_id=user_id,
            username=username,
            password=ph.hash(PASSWORD),
            role=role,
            created_at=datetime(2026, 11, 1, 9, 0, 0),
        ))

    # ---------- teams (each manager is a team_manager account) ----------
    session.add(Team(team_id=1, name="Redbull", country="Austria", manager_id=3, max_drivers=2, created_at=datetime(2026, 11, 1, 10, 0, 0)))
    session.add(Team(team_id=2, name="Ferrari", country="Italy", manager_id=4, max_drivers=2, created_at=datetime(2026, 11, 1, 10, 5, 0)))

    # ---------- drivers, every driver has a team_id ----------
    session.add(Driver(driver_id=1, user_id=5, full_name="Max Ryder", car_number=1, nationality="Dutch", date_of_birth=date(1997, 9, 30), team_id=1, created_at=datetime(2026, 11, 2, 9, 0, 0)))
    session.add(Driver(driver_id=2, user_id=6, full_name="Sergio Pena", car_number=11, nationality="Mexican", date_of_birth=date(1990, 1, 26), team_id=1, created_at=datetime(2026, 11, 2, 9, 5, 0)))
    session.add(Driver(driver_id=3, user_id=7, full_name="Charles Laurent", car_number=16, nationality="Monegasque", date_of_birth=date(1997, 10, 16), team_id=2, created_at=datetime(2026, 11, 2, 9, 10, 0)))
    session.add(Driver(driver_id=4, user_id=8, full_name="Carlos Vega", car_number=55, nationality="Spanish", date_of_birth=date(1994, 9, 1), team_id=2, created_at=datetime(2026, 11, 2, 9, 15, 0)))

    # ---------- applications: 4 accepted (the drivers are on those teams) and 2 rejected ----------
    # sergio and carlos were rejected first, then accepted by their other team
    applications = [
        (1, 3, 1, "rejected", "Hoping to join Redbull.", datetime(2026, 11, 2, 10, 0, 0), datetime(2026, 11, 2, 15, 0, 0)),
        (2, 4, 2, "rejected", "Hoping to join Ferrari.", datetime(2026, 11, 2, 10, 30, 0), datetime(2026, 11, 2, 15, 10, 0)),
        (3, 1, 1, "accepted", "Race winner looking for a seat.", datetime(2026, 11, 2, 11, 0, 0), datetime(2026, 11, 3, 9, 0, 0)),
        (4, 3, 2, "accepted", "Happy to drive for Ferrari.", datetime(2026, 11, 2, 12, 0, 0), datetime(2026, 11, 3, 9, 30, 0)),
        (5, 2, 1, "accepted", "Experienced driver, 10 years racing.", datetime(2026, 11, 3, 10, 0, 0), datetime(2026, 11, 3, 12, 0, 0)),
        (6, 4, 2, "accepted", "Applying again after a good season.", datetime(2026, 11, 3, 10, 30, 0), datetime(2026, 11, 3, 12, 30, 0)),
    ]
    for application_id, driver_id, team_id, status, message, applied_at, reviewed_at in applications:
        session.add(TeamApplication(
            application_id=application_id,
            driver_id=driver_id,
            team_id=team_id,
            status=status,
            message=message,
            applied_at=applied_at,
            reviewed_at=reviewed_at,
        ))

    # ---------- one active championship with both teams registered ----------
    session.add(Championship(
        champ_id=1,
        name="Formula Racing Championship 2026",
        season=2026,
        organizer_id=2,
        start_date=date(2026, 11, 1),
        end_date=date(2026, 12, 31),
        status="ongoing",
        created_at=datetime(2026, 11, 1, 11, 0, 0),
    ))
    session.add(ChampionshipTeam(champ_team_id=1, championship_id=1, team_id=1, registered_at=datetime(2026, 11, 3, 14, 0, 0)))
    session.add(ChampionshipTeam(champ_team_id=2, championship_id=1, team_id=2, registered_at=datetime(2026, 11, 3, 14, 5, 0)))

    # ---------- two races, one completed and one scheduled ----------
    session.add(Race(
        race_id=1, championship_id=1, name="Japan Grand Prix", circuit="Suzuka Circuit", country="Japan",
        round_number=1, race_date=date(2026, 11, 15), status="completed", results_published=True,
        created_at=datetime(2026, 11, 4, 9, 0, 0),
    ))
    session.add(Race(
        race_id=2, championship_id=1, name="Abu Dhabi Grand Prix", circuit="Yas Marina Circuit", country="UAE",
        round_number=2, race_date=date(2026, 12, 6), status="scheduled", results_published=False,
        created_at=datetime(2026, 11, 4, 9, 5, 0),
    ))

    # ---------- results of the completed race (driver id, team id, position) ----------
    results = [
        (1, 1, 1, 1),
        (2, 3, 2, 2),
        (3, 2, 1, 3),
        (4, 4, 2, 4),
    ]
    for result_id, driver_id, team_id, position in results:
        fastest = False
        lap_time = None
        if driver_id == 3:  # charles set the fastest lap
            fastest = True
            lap_time = "1:31.845"
        session.add(RaceResult(
            result_id=result_id,
            race_id=1,
            driver_id=driver_id,
            team_id=team_id,
            position=position,
            points=POINTS_TABLE.get(position, 0),
            fastest_lap=fastest,
            fastest_lap_time=lap_time,
            created_at=datetime(2026, 11, 15, 18, 0, 0),
        ))

    session.commit()
    session.close()

    print("Seed data added. Every account uses the password: " + PASSWORD)
    print("")
    print("admin           admin1")
    print("organizer       organizer1       (owns championship 1)")
    print("team managers   manager_redbull  (Redbull, team 1)")
    print("                manager_ferrari  (Ferrari, team 2)")
    print("drivers         driver_max, driver_sergio    (Redbull)")
    print("                driver_charles, driver_carlos (Ferrari)")


seed_database()