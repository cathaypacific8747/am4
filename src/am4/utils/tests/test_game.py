from am4.utils.game import Campaign, User


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
    assert u.load == 0.99
    assert u.accumulated_count == 0
    assert u.income_loss_tol == 0.02
    assert u.fourx is False
    assert u.role == User.Role.USER
    # assert u.get_password() == ""
