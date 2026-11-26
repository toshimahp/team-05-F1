# F1 – Formula Racing Championship Manager

## 1. Project and team

A backend for managing a Formula 1-style championship. Admins create organizers and teams, organizers create championships, schedule races and publish results, and users register as drivers, apply to teams and race. Championship standings are calculated from the published results. Built with FastAPI, SQLite, Pydantic, JWT access and refresh tokens and role-based access control, and deployed with Docker, GitHub Actions and AWS EC2. This is a backend-only project, so there is no frontend.

**Roles:** `admin`, `organizer`, `driver`  and `team_manager`. New registrations are drivers by default, and only admins can create organizer accounts.

| Member | Endpoints built |
|:-------|:----------------|
| **Toshimah** | A1 register, E1 create organizer, E2 create team, E3 get all teams, E4 get one team, E5 create championship |
| **Samhita** | A2 login, E11 schedule a race, E12 get races, E13 submit race results, E14 championship standings, E15 driver performance history |
| **Darsh** | A3 refresh token, E6 get all championships, E7 register driver profile, E8 apply to join a team, E9 accept or reject an application, E10 register a team for a championship |


| Done/Not(✅) | A1/A2/A3 | E1/E11/E6 | E2/E12/E7 | E3/E13/E8 | E4/E14/E9 | E5/E15/E10 |
|:--------------|:---------|:----------|:----------|:----------|:----------|:-----------|
| **Toshimah** | A1✅ | E1✅ | E2✅ | E3✅ | E4✅ | E5✅ |
| **Samhita** | A2 ✅ | E11 ✅ | E12 ✅ | E13 ✅ | E14 ✅ | E15 ✅ |
| **Darsh** | A3 ✅ | E6 ✅ | E7 ✅ | E8 ✅ | E9 ✅ | E10 ✅ |

## 2. Live app

**Public API link:** http://54.221.66.61:8001/docs
**API docs:** http://127.0.0.1:8001/docs

## 3. How to run it

### Backend
```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
On Mac or Linux, use `python3.12 -m venv venv` and `source venv/bin/activate`. Open the API docs at http://127.0.0.1:8001/docs.

### Frontend
There is no frontend. Use `/docs` to try every endpoint.

### Docker container
```bash
cd backend
docker build -t f1-backend .
docker run -d --name f1-app -p 8001:8001 -v "$(pwd)/data:/app/data" f1-backend
```
The `-v` flag mounts a folder from your machine for the SQLite file, so the data survives when the container is replaced. Open http://127.0.0.1:8001/docs. To stop and remove it:
```bash
docker stop f1-app
docker rm f1-app
```

## 4. API contract

Paths and bodies below are the team's design. Authenticated endpoints take the access token in the request header.

| # | What it does | Access | Method | Path | Request body | Success code |
|:-:|:-------------|:------:|:------:|:-----|:-------------|:------------:|
| A1 | Register a new account | All | POST | /auth/register | username<br>email<br>password | 201 |
| A2 | Log in and get access and refresh tokens | All | POST | /auth/login | email<br>password | 200 |
| A3 | Get a new access token | All | POST | /auth/refresh | none (refresh token in the header) | 200 |
| E1 | Create an organizer account | Admin | POST | /organizers | username<br>email<br>password | 201 |
| E2 | Create a racing team | Admin | POST | /teams | name<br>country<br>manager<br>driver_limit | 201 |
| E3 | Get all racing teams | All | GET | /teams | none | 200 |
| E4 | Get one team | All | GET | /teams/{team_id} | none | 200 |
| E5 | Create a championship | Organizer | POST | /championships | name<br>season | 201 |
| E6 | Get all championships | All | GET | /championships | none | 200 |
| E7 | Register a driver profile | Driver | POST | /drivers | name<br>country | 201 |
| E8 | Apply to join a team | Driver | POST | /teams/{team_id}/applications | none | 201 |
| E9 | Accept or reject a driver application | Team manager | PATCH | /applications/{application_id} | action (`accept` or `reject`) | 200 |
| E10 | Register a team for a championship | Team manager | POST | /championships/{championship_id}/teams | team_id | 201 |
| E11 | Schedule a race in a championship | Organizer | POST | /championships/{championship_id}/races | name<br>date | 201 |
| E12 | Get races for a championship | All | GET | /championships/{championship_id}/races | none | 200 |
| E13 | Submit race results | Organizer | POST | /races/{race_id}/results | results: driver_id, position, fastest_lap (optional) for each driver | 201 |
| E14 | Get championship standings | All | GET | /championships/{championship_id}/standings | none | 200 |
| E15 | Get a driver's performance history | All | GET | /drivers/{driver_id}/history | none | 200 |

### Scoring

| Position | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th | 10th |
|:---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:----:|
| **Points** | 25 | 18 | 15 | 12 | 10 | 8 | 6 | 4 | 2 | 1 |

### Error rules

Every error returns `{"detail": "..."}`.

| Rule | Status |
|:-----|:------:|
| Missing, invalid or expired access token | 401 |
| Invalid or expired refresh token | 401 |
| Wrong email or password at login | 401 |
| The role is not allowed to use the endpoint (for example a driver creating a team) | 403 |
| A team manager acting on a team they don't manage | 403 |
| A team, championship, race, driver or application id that doesn't exist | 404 |
| Registering with an email that already exists | 409 |
| Applying to a team when the driver is already in a team, or has already applied | 409 |
| Accepting a driver when the team's driver limit is reached | 400 |
| Deciding an application that is not pending | 400 |
| Registering a team that is already in the championship | 409 |
| Submitting results for a driver or team that is not registered in the championship | 400 |
| Missing or empty required field, or an invalid position or points value | 422 |

## 5. Database

One SQLite file with these tables. The columns below are the plan, so update them to match `model.py` when it is final.

| Table | Columns |
|:------|:--------|
| **users** | id, username, email (unique), password (hashed), role, created_at |
| **teams** | id, name, country, manager_id (user), driver_limit |
| **drivers** | id, user_id, name, country, team_id (empty until accepted) |
| **applications** | id, driver_id, team_id, status (`pending`, `accepted` or `rejected`), created_at |
| **championships** | id, name, season, created_by (user) |
| **championship_teams** | id, championship_id, team_id |
| **races** | id, championship_id, name, date |
| **results** | id, race_id, driver_id, team_id, position, points, fastest_lap |

## 6. Screenshots

### Authentication

**A1: Register a new account**<br>
[View screenshot](screenshots/a1-register.png)

**A2: Log in and get access and refresh tokens**<br>
[View screenshot](screenshots/a2-login.png)

**A3: Get a new access token using the refresh token**<br>
[View screenshot](screenshots/a3-refresh.png)

### Organizers, teams and championships

**E1: Admin creates an organizer account**<br>
[View screenshot](screenshots/e1-create_organizer_account.png)

**E2: Admin creates a racing team**<br>
[View screenshot](screenshots/e2-create_racing_team.png)

**E3: Get all racing teams**<br>
[View screenshot](screenshots/e3-get_racing_team.png)

**E4: Get one team by its ID**<br>
[View screenshot](screenshots/e4-get-raging_team_id.png)

**E5: Organizer creates a championship**<br>
[View screenshot](screenshots/e5-reate_championship.png)

**E6: Get all championships**<br>
[View screenshot](screenshots/e6-get_all_championships.png)

### Drivers and applications

**E7: Driver registers a driver profile**<br>
[View screenshot](screenshots/e7-create_driver.png)

**E8: Driver applies to join a team**<br>
[View screenshot](screenshots/e8-driver%20applies_to_join_a_team.png)

**E9: Team manager accepts or rejects an application**<br>
[View screenshot](screenshots/e9-team_manager_accepts_or_rejects_an_application.png)

**E10: Team manager registers a team for a championship**<br>
[View screenshot](screenshots/e10-team_manager_registers_a_team_for_a_championship.png)

### Races, results and standings

**E11: Organizer schedules a race in a championship**<br>
[View screenshot](screenshots/e11-schedule-race.png)

**E12: Get the races for a championship**<br>
[View screenshot](screenshots/e12-get-championship.png)

**E13: Organizer submits race results**<br>
[View screenshot](screenshots/e13-publish-race-results.png)

**E14: Get championship standings**<br>
[View screenshot](screenshots/e14-get-championship-standings.png)

**E15: Get a driver's performance history**<br>
[View screenshot](screenshots/e15-get-driver-history.png)


## 7. Known issues

| # | Known issue | Proposed fix |
|:--:|:-------------|:-------------|
| 1 | Anyone can register as an admin or organizer. | Remove admin and organizer from public registration. Seed the initial admin account securely. |
| 2 | A fallback `SECRET_KEY` is hardcoded, and deployment does not override it. | Require `SECRET_KEY` as an environment variable and pass the GitHub secret to `docker run`. |
| 3 | Creating a team with a duplicate name returns HTTP `500`. | Check for an existing team name and return HTTP `409 Conflict`. |
| 4 | E4 returns HTTP `200` with an empty list (`[]`) for a non-existent team. | Return HTTP `404 Not Found` if the team does not exist. |
| 5 | E9 allows admins through the route, but the ownership check returns `403 Forbidden` (`"not your team"`). | Remove admin from the allowed roles or let admins bypass the ownership check. |
| 6 | E7 (`create_driver`) does not expose `team_id` in the request body, so it always remains `null`. | Change the `team_id` column in the drivers table of`model.py` to `nullable=False`. |
