# am4
This crate provides core functions that will be used in the bot/wasm bundle (brewing).

## Implementation details
Some implementation details
- `Aircrafts`, `Airports` and `Routes` are stored in a private `Vec`
  - data is deserialised from bytes with zero-copy using `rkyv`
  - indexes on the data allow for searching and suggesting
    - `HashMap<K, usize>` is first built, where `K` is an owned enum derived from columns.
    - we do not use [self referential structs](https://stackoverflow.com/questions/32300132/why-cant-i-store-a-value-and-a-reference-to-that-value-in-the-same-struct/32300133#32300133) for simplicity
    - fuzzy finding: jaro winkler the query string against every single `K`: $O(n)$
  - they are immutable and do not allow addition/deletion.

### TODO
- [ ] consider storing {y, 2j, 3f} to avoid repeated * ops in config.
- [ ] store `airports` on the stack instead of `Vec` - it is and should be immutable?
- [ ] A->B->C: stopover search is to find optimal B that minimises total distance
  - the optimal solution lies on a great circle arc bounded between the circle generated by A and C.
  - right now: brute force all airports $O(n)$
  - when compounded with routes search against $n$ airports: gets very inefficient, possible solution:
    - ball tree with haversine distance to narrow down the search space, but seems overkill