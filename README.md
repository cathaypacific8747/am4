# AM4 bot

## Installation
Requirements: python3.11

```
pip3 install -r requirements.txt
```

## dev
cmake
```
virtualenv .venv
.venv/scripts/activate
pip install .

cd build
cmake ..
cmake --build . --config Release --target check
```