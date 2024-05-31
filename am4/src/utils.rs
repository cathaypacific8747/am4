use std::cmp::Ordering;

#[derive(Debug, Clone, PartialEq)]
pub struct Suggestion<T> {
    pub item: T,
    pub similarity: f64,
}

impl<T: PartialEq> Eq for Suggestion<T> {}

impl<T: PartialEq> Ord for Suggestion<T> {
    fn cmp(&self, other: &Self) -> Ordering {
        other.similarity.partial_cmp(&self.similarity).unwrap() // min heap
    }
}

impl<T: PartialEq> PartialOrd for Suggestion<T> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// converts raw database value into a key
/// note: this is not hashing but a preprocessing step
pub trait Preprocess {
    fn preprocess(&self) -> Self;
}
