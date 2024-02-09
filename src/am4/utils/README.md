# am4utils

A C++ library containing the core calculations.
Core code under [cpp](./cpp) builds a Python library using pybind11.
By default, `am4.utils.utils` is a `.so` module in the root dir of `site-packages`, so files under [py](./py) allow you to do:
```py
import am4
am4.utils.db.init() # instead of `am4.utils.utils.db.init()`
```
[stubs](./stubs) are auto-genereated with `generate-stubs.py`.

> [!CAUTION]
> Beware of cringe, this was developed when I was still learning C++.

## Usage
See [README in root dir](../../README.md#am4utils-development)

Supports Python 3.9 - 3.11 on the following platforms:
- manylinux2_28 x86_64 (ubuntu 18.04+, debian 10+, fedora 30+)
- ~~macos x86_64 / amd64~~
- ~~windows amd64~~