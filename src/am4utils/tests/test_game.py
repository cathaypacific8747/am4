from am4utils.game import Campaign, User

def test_campaign():
    c = Campaign.parse("c1, e")
    assert c.pax_activated == Campaign.Airline.C1_24HR
    assert c.cargo_activated == Campaign.Airline.C1_24HR
    assert c.eco_activated == Campaign.Eco.C_24HR

    c = Campaign.parse("e")
    assert c.pax_activated == Campaign.Airline.NONE
    assert c.cargo_activated == Campaign.Airline.NONE
    assert c.eco_activated == Campaign.Eco.C_24HR

    c = Campaign.Default()
    assert c.pax_activated == Campaign.Airline.C4_24HR
    assert c.cargo_activated == Campaign.Airline.C4_24HR
    assert c.eco_activated == Campaign.Eco.C_24HR

def test_campaign_reputation():
    c = Campaign.parse("c1, e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 7.5 + 10

    c = Campaign.parse("c4, e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 30 + 10

    c = Campaign.parse("e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 10

def test_default_user():
    u = User.Default()
    ur = User.Default(True)
    assert u.id == "00000000-0000-0000-0000-000000000000"
    assert u.game_mode == User.GameMode.EASY
    assert ur.id == "00000000-0000-0000-0000-000000000001"
    assert ur.game_mode == User.GameMode.REALISM
    assert u.fuel_price == 700
    assert u.co2_price == 120
    assert u.load == 0.87
    assert u.accumulated_count == 0
    assert u.income_loss_tol == 0.
    assert u.fourx == False
    assert u.role == User.Role.USER
    assert u.get_password() == ''

def test_create_user():
    u = User.create("cathayexpress", "<TODO:hashed_password>", 54557, "Cathay Express")
    assert u.username == "cathayexpress"
    assert u.game_id == 54557
    assert u.game_name == "Cathay Express"
    assert u.game_mode == User.GameMode.EASY
    assert u.discord_id == 0
    assert u.get_password() == "<TODO:hashed_password>"

    u_duplicate = User.create("cathayexpress", "<TODO:hashed_password13>", 13, "Cathay Express13")
    assert u_duplicate.valid == False

    u0 = User.from_id(u.id)
    assert u0.id == u.id

    u1 = User.from_username("cathayexpress")
    assert u1.id == u.id

    u2 = User.from_game_id(54557)
    assert u2.id == u.id

    u3 = User.from_game_name("Cathay Express")
    assert u3.id == u.id

    u4 = User.from_discord_id(0)
    assert u4.id == u.id

def test_user_settings():
    u = User.from_username("cathayexpress")
    
    success = u.set_username("cathayexpress13")
    assert success and u.username == "cathayexpress13"

    success = u.set_game_id(13)
    assert success and u.game_id == 13

    success = u.set_game_name("Cathay Express 13")
    assert success and u.game_name == "Cathay Express 13"

    success = u.set_game_mode(User.GameMode.REALISM)
    assert success and u.game_mode == User.GameMode.REALISM

    success = u.set_discord_id(13)
    assert success and u.discord_id == 13

    success = u.set_wear_training(1)
    assert success and u.wear_training == 1

    success = u.set_repair_training(1)
    assert success and u.repair_training == 1

    success = u.set_l_training(1)
    assert success and u.l_training == 1

    success = u.set_h_training(1)
    assert success and u.h_training == 1

    success = u.set_fuel_training(1)
    assert success and u.fuel_training == 1

    success = u.set_co2_training(1)
    assert success and u.co2_training == 1

    success = u.set_fuel_price(512)
    assert success and u.fuel_price == 512

    success = u.set_co2_price(128)
    assert success and u.co2_price == 128

    success = u.set_accumulated_count(13)
    assert success and u.accumulated_count == 13

    success = u.set_load(0.13)
    assert success and u.load == 0.13

    success = u.set_income_tolerance(0.13)
    assert success and u.income_loss_tol == 0.13

    success = u.set_fourx(True)
    assert success and u.fourx == True

    success = u.set_role(User.Role.TRUSTED_USER)
    assert success and u.role == User.Role.TRUSTED_USER

def test_user_invalid_settings():
    u = User.from_username("cathayexpress13")

    success = u.set_username("cathayexpress13")
    assert not success

    success = u.set_wear_training(6)
    assert not success

    success = u.set_repair_training(6)
    assert not success

    success = u.set_l_training(7)
    assert not success

    success = u.set_h_training(7)
    assert not success

    success = u.set_fuel_training(4)
    assert not success

    success = u.set_co2_training(6)
    assert not success

    success = u.set_fuel_price(3001)
    assert not success

    success = u.set_co2_price(201)
    assert not success

    success = u.set_load(101)
    assert not success

    success = u.set_load(0)
    assert not success

    success = u.set_income_tolerance(1.1)
    assert not success