use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct PaxDemand {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

impl std::ops::Div<f64> for PaxDemand {
    type Output = Self;

    fn div(self, rhs: f64) -> Self::Output {
        Self {
            y: (self.y as f64 / rhs).floor() as u16,
            j: (self.j as f64 / rhs).floor() as u16,
            f: (self.f as f64 / rhs).floor() as u16,
        }
    }
}

// #[cfg(test)]
// mod tests {
//     use super::*;
//     use bincode::{self, Options};

//     #[test]
//     fn test_from_bytes() {
//         let options = bincode::DefaultOptions::new().with_fixint_encoding();

//         // let xs: &[u8] = &[0x21, 0xe2, 0x00, 0xb6, 0x00, 0x2d];
//         // let ys: PaxDemand = options.deserialize(&xs).unwrap();
//         // dbg!(ys);
//         // let expected = PaxDemand {
//         //     y: 542,
//         //     j: 182,
//         //     f: 45,
//         // };
//         // let xhat: Vec<u8> = options.serialize(&expected).unwrap();
//         // dbg!(xhat);
//         // assert_eq!(expected, ys);
//     }
// }
