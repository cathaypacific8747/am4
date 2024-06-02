use super::pax::PaxDemand;

#[derive(Debug, PartialEq)]
pub struct CargoDemand {
    pub l: u32,
    pub h: u32,
}

impl From<&PaxDemand> for CargoDemand {
    fn from(pax_demand: &PaxDemand) -> Self {
        Self {
            l: (pax_demand.y as f64 / 2.0).round() as u32 * 1000,
            h: pax_demand.j as u32 * 1000,
        }
    }
}

impl std::ops::Div<f64> for CargoDemand {
    type Output = Self;

    fn div(self, rhs: f64) -> Self::Output {
        Self {
            l: (self.l as f64 / rhs).floor() as u32,
            h: (self.h as f64 / rhs).floor() as u32,
        }
    }
}
