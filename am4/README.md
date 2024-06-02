# am4

This crate provides core functions that will be used in the bot/wasm bundle (brewing).

Some implementation details
- `aircraft` and `airports` are stored in a `Vec`
  - `HashMap<K, usize>` provides quick lookups into the `Vec`, where `K` is an owned enum.
  - fuzzy finding: jaro winkler the query string against every single `K`: $O(n)$
  - not using [self referential structs](https://stackoverflow.com/questions/32300132/why-cant-i-store-a-value-and-a-reference-to-that-value-in-the-same-struct/32300133#32300133) for simplicity
- `routes` similarly stored in a `Vec`

TODO:
- [ ] move away from csv and use bincode.
- [ ] consider storing {y, 2j, 3f} to avoid repeated * ops in config.
- [ ] store `airports` on the stack instead of `Vec` - it is and should be immutable.