import requests

URL = "http://127.0.0.1:8001"

tokens = {}
refresh_tokens = {}


# helper builds the token header for a user
def auth(name):
    return {"token": tokens[name]}


# ======================================================================
# SETUP: register and log in the users we need
# users get ids 1 to 6 in this order: admin1, org1, mgr1, ana, ben, cal
# ======================================================================

def test_setup_register_users():
    users = [
        {"username": "admin1", "password": "pass123", "role": "admin"},
        {"username": "org1", "password": "pass123", "role": "organizer"},
        {"username": "mgr1", "password": "pass123", "role": "team_manager"},
        {"username": "ana", "password": "pass123", "role": "driver"},
        {"username": "ben", "password": "pass123", "role": "driver"},
        {"username": "cal", "password": "pass123", "role": "driver"},
    ]
    for user in users:
        response = requests.post(url=URL + "/register", json=user)
        assert response.status_code in [200, 201]


def test_setup_login_users():
    for name in ["admin1", "org1", "mgr1", "ana", "ben", "cal"]:
        response = requests.post(url=URL + "/auth/login", json={"username": name, "password": "pass123"})
        assert response.status_code == 200
        tokens[name] = response.json()["access_token"]
        refresh_tokens[name] = response.json()["refresh_token"]


# ======================================================================
# A1 register (Toshima)
# ======================================================================

def test_a1_register_duplicate_username():
    user = {"username": "ana", "password": "pass123", "role": "driver"}
    response = requests.post(url=URL + "/register", json=user)
    assert response.status_code == 409


def test_a1_register_short_username():
    user = {"username": "ab", "password": "pass123", "role": "driver"}
    response = requests.post(url=URL + "/register", json=user)
    assert response.status_code == 422


def test_a1_register_short_password():
    user = {"username": "newuser", "password": "123", "role": "driver"}
    response = requests.post(url=URL + "/register", json=user)
    assert response.status_code == 422


def test_a1_register_missing_field():
    response = requests.post(url=URL + "/register", json={"username": "newuser"})
    assert response.status_code == 422


# ======================================================================
# A2 login (Sam)
# ======================================================================

def test_a2_login_gives_both_tokens():
    response = requests.post(url=URL + "/auth/login", json={"username": "ana", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_a2_login_wrong_password():
    response = requests.post(url=URL + "/auth/login", json={"username": "ana", "password": "wrongpass"})
    assert response.status_code == 401


def test_a2_login_unknown_user():
    response = requests.post(url=URL + "/auth/login", json={"username": "nobody", "password": "pass123"})
    assert response.status_code == 401


def test_a2_login_missing_field():
    response = requests.post(url=URL + "/auth/login", json={"username": "ana"})
    assert response.status_code == 422


# ======================================================================
# A3 refresh (Darsh)
# the refresh token goes in the header called refresh-token
# ======================================================================

def test_a3_refresh_gives_new_access_token():
    header = {"refresh-token": refresh_tokens["ana"]}
    response = requests.post(url=URL + "/auth/refresh", headers=header)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_a3_refresh_with_new_token_works():
    header = {"refresh-token": refresh_tokens["ana"]}
    new_token = requests.post(url=URL + "/auth/refresh", headers=header).json()["access_token"]
    response = requests.get(url=URL + "/racing_team", headers={"token": new_token})
    assert response.status_code == 200


def test_a3_refresh_missing_token():
    response = requests.post(url=URL + "/auth/refresh")
    assert response.status_code == 401


def test_a3_refresh_with_access_token_fails():
    header = {"refresh-token": tokens["ana"]}
    response = requests.post(url=URL + "/auth/refresh", headers=header)
    assert response.status_code == 401


def test_a3_refresh_with_garbage_fails():
    header = {"refresh-token": "not-a-real-token"}
    response = requests.post(url=URL + "/auth/refresh", headers=header)
    assert response.status_code == 401


# ======================================================================
# E1 create an organizer account (Toshima, admin only)
# ======================================================================

def test_e1_admin_creates_organizer():
    body = {"username": "org2", "password": "pass123"}
    response = requests.post(url=URL + "/organizer_account", json=body, headers=auth("admin1"))
    assert response.status_code == 201
    assert response.json()["role"] == "organizer"
    assert "password" not in response.json()

    login = requests.post(url=URL + "/auth/login", json=body)
    assert login.status_code == 200
    tokens["org2"] = login.json()["access_token"]


def test_e1_duplicate_organizer():
    body = {"username": "org2", "password": "pass123"}
    response = requests.post(url=URL + "/organizer_account", json=body, headers=auth("admin1"))
    assert response.status_code == 409


def test_e1_non_admin_is_forbidden():
    body = {"username": "org3", "password": "pass123"}
    response = requests.post(url=URL + "/organizer_account", json=body, headers=auth("org1"))
    assert response.status_code == 403


def test_e1_no_token():
    body = {"username": "org3", "password": "pass123"}
    response = requests.post(url=URL + "/organizer_account", json=body)
    assert response.status_code == 401


# ======================================================================
# E2 create a racing team (Toshima, admin only)
# mgr1 is user 3, so manager_id is 3
# ======================================================================

def test_e2_admin_creates_team():
    body = {"name": "Red Rocket", "country": "Austria", "manager_id": 3, "max_drivers": 2}
    response = requests.post(url=URL + "/racing_team", json=body, headers=auth("admin1"))
    assert response.status_code in [200, 201]
    assert response.json()["name"] == "Red Rocket"
    assert response.json()["team_id"] == 1


def test_e2_non_admin_is_forbidden():
    body = {"name": "Blue Bolt", "country": "Italy", "manager_id": 3, "max_drivers": 2}
    response = requests.post(url=URL + "/racing_team", json=body, headers=auth("org1"))
    assert response.status_code == 403


def test_e2_no_token():
    body = {"name": "Blue Bolt", "country": "Italy", "manager_id": 3, "max_drivers": 2}
    response = requests.post(url=URL + "/racing_team", json=body)
    assert response.status_code == 401


def test_e2_invalid_max_drivers():
    body = {"name": "Blue Bolt", "country": "Italy", "manager_id": 3, "max_drivers": 0}
    response = requests.post(url=URL + "/racing_team", json=body, headers=auth("admin1"))
    assert response.status_code == 422


# ======================================================================
# E3 get all teams, E4 get one team (Toshima, any logged in user)
# ======================================================================

def test_e3_get_all_teams():
    response = requests.get(url=URL + "/racing_team", headers=auth("ana"))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Red Rocket"


def test_e3_no_token():
    response = requests.get(url=URL + "/racing_team")
    assert response.status_code == 401


def test_e4_get_one_team():
    response = requests.get(url=URL + "/racing_team/1", headers=auth("ana"))
    assert response.status_code == 200
    assert response.json()[0]["country"] == "Austria"


def test_e4_no_token():
    response = requests.get(url=URL + "/racing_team/1")
    assert response.status_code == 401


# ======================================================================
# E5 create a championship (Toshima, organizer only)
# ======================================================================

def test_e5_organizer_creates_championship():
    body = {"name": "Season 2026", "season": 2026}
    response = requests.post(url=URL + "/Championship", json=body, headers=auth("org1"))
    assert response.status_code in [200, 201]
    assert response.json()["champ_id"] == 1
    assert response.json()["status"] == "upcoming"


def test_e5_driver_is_forbidden():
    body = {"name": "Season 2027", "season": 2027}
    response = requests.post(url=URL + "/Championship", json=body, headers=auth("ana"))
    assert response.status_code == 403


def test_e5_invalid_season():
    body = {"name": "Old Season", "season": 1800}
    response = requests.post(url=URL + "/Championship", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e5_end_date_before_start_date():
    body = {"name": "Bad Dates", "season": 2026, "start_date": "2026-12-01", "end_date": "2026-01-01"}
    response = requests.post(url=URL + "/Championship", json=body, headers=auth("org1"))
    assert response.status_code == 422


# ======================================================================
# E6 get all championships (Darsh, everyone)
# ======================================================================

def test_e6_get_all_championships():
    response = requests.get(url=URL + "/championships")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Season 2026"


# ======================================================================
# E7 register a driver profile (Darsh, driver only)
# ana is driver 1, ben is driver 2, cal is driver 3
# ======================================================================

def test_e7_drivers_create_profiles():
    profiles = [
        ("ana", {"full_name": "Ana", "car_number": 11, "nationality": "Indian"}),
        ("ben", {"full_name": "Ben", "car_number": 22, "nationality": "British"}),
        ("cal", {"full_name": "Cal", "car_number": 33, "nationality": "Spanish"}),
    ]
    for name, body in profiles:
        response = requests.post(url=URL + "/drivers", json=body, headers=auth(name))
        assert response.status_code == 201
        assert response.json()["full_name"] == body["full_name"]


def test_e7_duplicate_profile():
    body = {"full_name": "Ana Again", "car_number": 44, "nationality": "Indian"}
    response = requests.post(url=URL + "/drivers", json=body, headers=auth("ana"))
    assert response.status_code == 409


def test_e7_organizer_is_forbidden():
    body = {"full_name": "Org", "car_number": 55, "nationality": "Indian"}
    response = requests.post(url=URL + "/drivers", json=body, headers=auth("org1"))
    assert response.status_code == 403


def test_e7_invalid_car_number():
    body = {"full_name": "Dev", "car_number": 0, "nationality": "Indian"}
    response = requests.post(url=URL + "/drivers", json=body, headers=auth("mgr1"))
    assert response.status_code == 422


# ======================================================================
# E8 apply to join a team (Darsh, driver only)
# ======================================================================

def test_e8_drivers_apply_to_team():
    for name in ["ana", "ben"]:
        response = requests.post(url=URL + "/applications", json={"team_id": 1}, headers=auth(name))
        assert response.status_code == 201
        assert response.json()["status"] == "pending"


def test_e8_apply_twice():
    response = requests.post(url=URL + "/applications", json={"team_id": 1}, headers=auth("ana"))
    assert response.status_code == 409


def test_e8_unknown_team():
    response = requests.post(url=URL + "/applications", json={"team_id": 99}, headers=auth("cal"))
    assert response.status_code == 404


def test_e8_without_driver_profile():
    response = requests.post(url=URL + "/applications", json={"team_id": 1}, headers=auth("mgr1"))
    assert response.status_code == 404


# ======================================================================
# E9 accept or reject an application (Darsh, team manager)
# applications 1 (ana) and 2 (ben) are pending
# ======================================================================

def test_e9_not_the_manager():
    response = requests.patch(url=URL + "/applications/1", json={"status": "accepted"}, headers=auth("ana"))
    assert response.status_code == 403


def test_e9_invalid_status():
    response = requests.patch(url=URL + "/applications/1", json={"status": "maybe"}, headers=auth("mgr1"))
    assert response.status_code == 422


def test_e9_unknown_application():
    response = requests.patch(url=URL + "/applications/99", json={"status": "accepted"}, headers=auth("mgr1"))
    assert response.status_code == 404


def test_e9_manager_accepts_both():
    for application_id in [1, 2]:
        response = requests.patch(url=URL + "/applications/" + str(application_id), json={"status": "accepted"}, headers=auth("mgr1"))
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"


def test_e9_already_decided():
    response = requests.patch(url=URL + "/applications/1", json={"status": "rejected"}, headers=auth("mgr1"))
    assert response.status_code == 400


# ======================================================================
# E10 register a team for a championship (Darsh, team manager)
# ======================================================================

def test_e10_not_the_manager():
    response = requests.post(url=URL + "/championships/1/teams", json={"team_id": 1}, headers=auth("ana"))
    assert response.status_code == 403


def test_e10_unknown_championship():
    response = requests.post(url=URL + "/championships/99/teams", json={"team_id": 1}, headers=auth("mgr1"))
    assert response.status_code == 404


def test_e10_manager_registers_team():
    response = requests.post(url=URL + "/championships/1/teams", json={"team_id": 1}, headers=auth("mgr1"))
    assert response.status_code == 201
    assert response.json()["team_id"] == 1


def test_e10_register_twice():
    response = requests.post(url=URL + "/championships/1/teams", json={"team_id": 1}, headers=auth("mgr1"))
    assert response.status_code == 409


# ======================================================================
# E11 schedule a race (Sam, organizer only)
# ======================================================================

def test_e11_organizer_schedules_races():
    first = requests.post(url=URL + "/championships/1/races", json={"name": "Season Opener", "race_date": "2026-12-05"}, headers=auth("org1"))
    assert first.status_code == 201
    assert first.json()["round_number"] == 1
    assert first.json()["status"] == "scheduled"

    second = requests.post(url=URL + "/championships/1/races", json={"name": "Second Round", "race_date": "2026-12-19"}, headers=auth("org1"))
    assert second.status_code == 201
    assert second.json()["round_number"] == 2


def test_e11_other_organizer_is_forbidden():
    body = {"name": "Sneaky Race", "race_date": "2026-12-26"}
    response = requests.post(url=URL + "/championships/1/races", json=body, headers=auth("org2"))
    assert response.status_code == 403


def test_e11_driver_is_forbidden():
    body = {"name": "Driver Race", "race_date": "2026-12-26"}
    response = requests.post(url=URL + "/championships/1/races", json=body, headers=auth("ana"))
    assert response.status_code == 403


def test_e11_no_token():
    body = {"name": "No Token Race", "race_date": "2026-12-26"}
    response = requests.post(url=URL + "/championships/1/races", json=body)
    assert response.status_code == 401


def test_e11_unknown_championship():
    body = {"name": "Lost Race", "race_date": "2026-12-26"}
    response = requests.post(url=URL + "/championships/99/races", json=body, headers=auth("org1"))
    assert response.status_code == 404


def test_e11_empty_name():
    body = {"name": "  ", "race_date": "2026-12-26"}
    response = requests.post(url=URL + "/championships/1/races", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e11_bad_date():
    body = {"name": "Bad Date Race", "race_date": "not-a-date"}
    response = requests.post(url=URL + "/championships/1/races", json=body, headers=auth("org1"))
    assert response.status_code == 422


# ======================================================================
# E12 get the races of a championship (Sam, everyone)
# ======================================================================

def test_e12_get_races_in_round_order():
    response = requests.get(url=URL + "/championships/1/races")
    assert response.status_code == 200
    races = response.json()
    assert len(races) == 2
    assert races[0]["name"] == "Season Opener"
    assert races[0]["round_number"] == 1
    assert races[1]["name"] == "Second Round"
    assert races[1]["round_number"] == 2


def test_e12_unknown_championship():
    response = requests.get(url=URL + "/championships/99/races")
    assert response.status_code == 404


# ======================================================================
# E13 submit race results (Sam, organizer only)
# race 1 and race 2 belong to championship 1 (org1)
# ana is driver 1, ben is driver 2, cal is driver 3 (no team)
# ======================================================================

def test_e13_publish_race_1():
    body = {"results": [
        {"driver_id": 1, "position": 1, "fastest_lap": True, "fastest_lap_time": "1:12.345"},
        {"driver_id": 2, "position": 2},
    ]}
    response = requests.post(url=URL + "/races/1/results", json=body, headers=auth("org1"))
    assert response.status_code == 201
    results = response.json()
    assert len(results) == 2
    assert results[0]["points"] == 25
    assert results[0]["fastest_lap"] == True
    assert results[1]["points"] == 18


def test_e13_publish_twice():
    body = {"results": [{"driver_id": 1, "position": 1}]}
    response = requests.post(url=URL + "/races/1/results", json=body, headers=auth("org1"))
    assert response.status_code == 400


def test_e13_unknown_race():
    body = {"results": [{"driver_id": 1, "position": 1}]}
    response = requests.post(url=URL + "/races/99/results", json=body, headers=auth("org1"))
    assert response.status_code == 404


def test_e13_other_organizer_is_forbidden():
    body = {"results": [{"driver_id": 1, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org2"))
    assert response.status_code == 403


def test_e13_driver_is_forbidden():
    body = {"results": [{"driver_id": 1, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("ana"))
    assert response.status_code == 403


def test_e13_no_token():
    body = {"results": [{"driver_id": 1, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body)
    assert response.status_code == 401


def test_e13_duplicate_position():
    body = {"results": [{"driver_id": 1, "position": 1}, {"driver_id": 2, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e13_duplicate_driver():
    body = {"results": [{"driver_id": 1, "position": 1}, {"driver_id": 1, "position": 2}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e13_two_fastest_laps():
    body = {"results": [
        {"driver_id": 1, "position": 1, "fastest_lap": True},
        {"driver_id": 2, "position": 2, "fastest_lap": True},
    ]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e13_bad_lap_time():
    body = {"results": [{"driver_id": 1, "position": 1, "fastest_lap_time": "1:2.3"}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 422


def test_e13_empty_results():
    response = requests.post(url=URL + "/races/2/results", json={"results": []}, headers=auth("org1"))
    assert response.status_code == 422


def test_e13_unknown_driver():
    body = {"results": [{"driver_id": 99, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 404


def test_e13_driver_without_team():
    body = {"results": [{"driver_id": 3, "position": 1}]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 400


def test_e13_publish_race_2():
    body = {"results": [
        {"driver_id": 2, "position": 1},
        {"driver_id": 1, "position": 3},
    ]}
    response = requests.post(url=URL + "/races/2/results", json=body, headers=auth("org1"))
    assert response.status_code == 201
    results = response.json()
    assert results[0]["points"] == 25
    assert results[1]["points"] == 15


def test_e13_race_is_marked_completed():
    response = requests.get(url=URL + "/championships/1/races")
    races = response.json()
    assert races[0]["results_published"] == True
    assert races[0]["status"] == "completed"
    assert races[1]["results_published"] == True


# ======================================================================
# E14 championship standings (Sam, everyone)
# ana: 25 + 15 = 40, ben: 18 + 25 = 43, so ben leads
# ======================================================================

def test_e14_driver_standings():
    response = requests.get(url=URL + "/championships/1/standings")
    assert response.status_code == 200
    drivers = response.json()["driver_standings"]
    assert len(drivers) == 2
    assert drivers[0]["position"] == 1
    assert drivers[0]["full_name"] == "Ben"
    assert drivers[0]["points"] == 43
    assert drivers[1]["position"] == 2
    assert drivers[1]["full_name"] == "Ana"
    assert drivers[1]["points"] == 40


def test_e14_team_standings():
    response = requests.get(url=URL + "/championships/1/standings")
    teams = response.json()["team_standings"]
    assert len(teams) == 1
    assert teams[0]["team_name"] == "Red Rocket"
    assert teams[0]["points"] == 83


def test_e14_unknown_championship():
    response = requests.get(url=URL + "/championships/99/standings")
    assert response.status_code == 404


# ======================================================================
# E15 driver performance history (Sam, everyone)
# ======================================================================

def test_e15_driver_history():
    response = requests.get(url=URL + "/drivers/1/history")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Ana"
    assert data["total_points"] == 40
    assert len(data["history"]) == 2
    assert data["history"][0]["race_name"] == "Season Opener"
    assert data["history"][0]["position"] == 1
    assert data["history"][1]["race_name"] == "Second Round"
    assert data["history"][1]["position"] == 3


def test_e15_driver_with_no_races():
    response = requests.get(url=URL + "/drivers/3/history")
    assert response.status_code == 200
    assert response.json()["total_points"] == 0
    assert response.json()["history"] == []


def test_e15_unknown_driver():
    response = requests.get(url=URL + "/drivers/99/history")
    assert response.status_code == 404
