from datetime import date
from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator

# points table from the prd
POINTS_TABLE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# admin + teams 
class OrganizerCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    def check_username(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("username must be at least 3 characters")
        return v

    @field_validator("password")
    def check_password(cls, v):
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class TeamCreate(BaseModel):
    name: str
    country: str
    manager_id: int
    max_drivers: int = 2

    @field_validator("name", "country")
    def not_empty(cls, v):
        v = v.strip()
        if v == "":
            raise ValueError("field cannot be empty")
        return v

    @field_validator("max_drivers")
    def check_max_drivers(cls, v):
        if v < 1:
            raise ValueError("max_drivers must be at least 1")
        return v


class TeamResponse(BaseModel):
    team_id: int
    name: str
    country: str
    manager_id: int
    max_drivers: int


# championships
class ChampionshipCreate(BaseModel):
    name: str
    season: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("name")
    def not_empty(cls, v):
        v = v.strip()
        if v == "":
            raise ValueError("name cannot be empty")
        return v

    @field_validator("season")
    def check_season(cls, v):
        if v < 1950 or v > 2100:
            raise ValueError("season must be a valid year")
        return v

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ChampionshipResponse(BaseModel):
    champ_id: int
    name: str
    season: int
    organizer_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str


class TeamRegisterRequest(BaseModel):
    team_id: int


# drivers
class DriverCreate(BaseModel):
    full_name: str
    car_number: int
    nationality: str
    date_of_birth: Optional[date] = None

    @field_validator("full_name", "nationality")
    def not_empty(cls, v):
        v = v.strip()
        if v == "":
            raise ValueError("field cannot be empty")
        return v

    @field_validator("car_number")
    def check_car_number(cls, v):
        if v < 1 or v > 99:
            raise ValueError("car_number must be between 1 and 99")
        return v


class TeamApplicationCreate(BaseModel):
    team_id: int
    message: Optional[str] = None


class ApplicationDecision(BaseModel):
    status: str

    @field_validator("status")
    def check_status(cls, v):
        v = v.lower().strip()
        if v not in ["accepted", "rejected"]:
            raise ValueError("status must be accepted or rejected")
        return v


# races
class RaceCreate(BaseModel):
    name: str
    circuit: str
    country: str
    round_number: int
    race_date: date

    @field_validator("name", "circuit", "country")
    def not_empty(cls, v):
        v = v.strip()
        if v == "":
            raise ValueError("field cannot be empty")
        return v

    @field_validator("round_number")
    def check_round(cls, v):
        if v < 1:
            raise ValueError("round_number must be at least 1")
        return v


class RaceResponse(BaseModel):
    race_id: int
    championship_id: int
    name: str
    circuit: str
    country: str
    round_number: int
    race_date: date
    status: str
    results_published: bool


# race results
class RaceResultItem(BaseModel):
    driver_id: int
    position: int
    fastest_lap: bool = False
    fastest_lap_time: Optional[str] = None  # e.g. "1:12.345"

    @field_validator("position")
    def check_position(cls, v):
        if v < 1:
            raise ValueError("position must be at least 1")
        return v

    @field_validator("fastest_lap_time")
    def check_lap_time(cls, v):
        if v is None:
            return v
        parts = v.split(":")
        if len(parts) != 2 or not parts[0].isdigit():
            raise ValueError("fastest_lap_time must look like 1:12.345")
        secs = parts[1].split(".")
        if len(secs) != 2 or len(secs[0]) != 2 or len(secs[1]) != 3:
            raise ValueError("fastest_lap_time must look like 1:12.345")
        if not secs[0].isdigit() or not secs[1].isdigit() or int(secs[0]) > 59:
            raise ValueError("fastest_lap_time must look like 1:12.345")
        return v


class RaceResultsSubmit(BaseModel):
    results: List[RaceResultItem]

    @field_validator("results")
    def check_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("results cannot be empty")
        return v

    @model_validator(mode="after")
    def check_results(self):
        positions = []
        drivers = []
        fastest_count = 0
        for item in self.results:
            if item.position in positions:
                raise ValueError("duplicate position " + str(item.position))
            if item.driver_id in drivers:
                raise ValueError("duplicate driver " + str(item.driver_id))
            positions.append(item.position)
            drivers.append(item.driver_id)
            if item.fastest_lap:
                fastest_count += 1
        if fastest_count > 1:
            raise ValueError("only one driver can have the fastest lap")
        return self


class RaceResultResponse(BaseModel):
    result_id: int
    race_id: int
    driver_id: int
    team_id: int
    position: int
    points: int
    fastest_lap: bool
    fastest_lap_time: Optional[str] = None
