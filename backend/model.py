from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")  # admin / organizer / driver
    created_at = Column(DateTime, default=datetime.now)


class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    max_drivers = Column(Integer, nullable=False, default=2)
    created_at = Column(DateTime, default=datetime.now)


class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    car_number = Column(Integer, unique=True, nullable=False)
    nationality = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=True)  # current team
    created_at = Column(DateTime, default=datetime.now)


class TeamApplication(Base):
    __tablename__ = "team_applications"
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending / accepted / rejected
    message = Column(String, nullable=True)
    applied_at = Column(DateTime, default=datetime.now)
    reviewed_at = Column(DateTime, nullable=True)


class Championship(Base):
    __tablename__ = "championships"
    champ_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="upcoming")  # upcoming / ongoing / completed
    created_at = Column(DateTime, default=datetime.now)


class ChampionshipTeam(Base):
    __tablename__ = "championship_teams"
    champ_team_id = Column(Integer, primary_key=True, autoincrement=True)
    championship_id = Column(Integer, ForeignKey("championships.champ_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.now)


class Race(Base):
    __tablename__ = "races"
    race_id = Column(Integer, primary_key=True, autoincrement=True)
    championship_id = Column(Integer, ForeignKey("championships.champ_id"), nullable=False)
    name = Column(String, nullable=False)
    circuit = Column(String, nullable=False)
    country = Column(String, nullable=False)
    round_number = Column(Integer, nullable=False)
    race_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="scheduled")  # scheduled / completed
    results_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class RaceResult(Base):
    __tablename__ = "race_results"
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    position = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=0)
    fastest_lap = Column(Boolean, default=False)
    fastest_lap_time = Column(String, nullable=True)  # e.g. "1:12.345"
    created_at = Column(DateTime, default=datetime.now)