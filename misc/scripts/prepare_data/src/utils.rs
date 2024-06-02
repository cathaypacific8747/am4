use polars::datatypes::AnyValue;

// dumb, but works
pub fn get_u8(v: AnyValue) -> u8 {
    match v {
        AnyValue::UInt8(v) => v,
        _ => panic!(),
    }
}

pub fn get_u16(v: AnyValue) -> u16 {
    match v {
        AnyValue::UInt16(v) => v,
        _ => panic!(),
    }
}

pub fn get_u32(v: AnyValue) -> u32 {
    match v {
        AnyValue::UInt32(v) => v,
        _ => panic!(),
    }
}

pub fn get_f32(v: AnyValue) -> f32 {
    match v {
        AnyValue::Float32(v) => v,
        _ => panic!(),
    }
}

pub fn get_f64(v: AnyValue) -> f64 {
    match v {
        AnyValue::Float64(v) => v,
        _ => panic!(),
    }
}

pub fn get_str(v: AnyValue) -> &str {
    match v {
        AnyValue::String(v) => v,
        _ => panic!(),
    }
}
