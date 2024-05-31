use am4::campaign::{Airline, Campaign, Eco};
// use am4::user::{GameMode, Role, User};

#[test]
fn test_campaign() {
    let c = Campaign::parse("c1, e");
    assert_eq!(c.pax_activated, Airline::C1_24HR);
    assert_eq!(c.cargo_activated, Airline::C1_24HR);
    assert_eq!(c.eco_activated, Eco::C24Hr);

    let c = Campaign::parse("e");
    assert_eq!(c.pax_activated, Airline::None);
    assert_eq!(c.cargo_activated, Airline::None);
    assert_eq!(c.eco_activated, Eco::C24Hr);
}

#[test]
fn test_campaign_reputation() {
    let c = Campaign::parse("c1, e");
    let rep = c.estimate_pax_reputation(45.0);
    assert_eq!(rep, 45.0 + 7.5 + 10.0);

    let c = Campaign::parse("c4, e");
    let rep = c.estimate_pax_reputation(45.0);
    assert_eq!(rep, 45.0 + 30.0 + 10.0);

    let c = Campaign::parse("e");
    let rep = c.estimate_pax_reputation(45.0);
    assert_eq!(rep, 45.0 + 10.0);
}

// #[test]
// fn test_default_user() {
//     let u = User::new(false);
//     let ur = User::new(true);

//     assert_eq!(u.game_mode, GameMode::Easy);
//     assert_eq!(ur.game_mode, GameMode::Realism);
//     assert_eq!(u.fuel_price, 700);
//     assert_eq!(u.co2_price, 120);
//     assert_eq!(u.load, 0.87);
//     assert_eq!(u.accumulated_count, 0);
//     assert_eq!(u.income_loss_tol, 0.02);
//     assert_eq!(u.fourx, false);
//     assert_eq!(u.role, Role::User);
// }
