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
pip3 install .[dev]
pip3 uninstall am4bot -y; pip3 install .
.venv/scripts/deactivate

mkdir build
cd build
cmake ..
cmake --build . --target am4utils

https://github.com/duckdb/duckdb/archive/refs/tags/v0.8.0.zip
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_GENERATOR_PLATFORM=x64 -DBUILD_ICU_EXTENSION=1 -DBUILD_PARQUET_EXTENSION=1 -DBUILD_TPCH_EXTENSION=1 -DBUILD_TPCDS_EXTENSION=1 -DBUILD_FTS_EXTENSION=1 -DBUILD_JSON_EXTENSION=1 -DBUILD_EXCEL_EXTENSION=0 -DBUILD_VISUALIZER_EXTENSION=1 -DBUILD_ODBC_DRIVER=1 -DDISABLE_UNITY=1 -DBUILD_AUTOCOMPLETE_EXTENSION=1 -DSTATIC_LIBCPP=1
cmake --build . --config Release
```