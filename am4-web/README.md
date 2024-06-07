```sh
rustup target add wasm32-unknown-unknown
cargo install trunk
trunk serve --open
trunk build -M --release
```

dev
```sh
cargo install leptosfmt
```