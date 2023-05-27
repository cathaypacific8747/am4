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
pip3 uninstall am4bot -y; pip3 install .
pip3 install .[dev]

cmake -S . -B build
```