# from enum import IntEnum

# def assert_equal_int_enums(pybind_enum: type, python_enum: IntEnum):
#     pb_kvs = {k: int(v) for k, v in pybind_enum.__members__.items()}
#     py_kvs = {k: int(v) for k, v in python_enum.__members__.items()}
#     assert pb_kvs.keys() == py_kvs.keys(), f"Keys not equal: {pb_kvs.keys()} vs {py_kvs.keys()}"
#     assert set(pb_kvs.values()) == set(py_kvs.values()), f"Values not equal: {pb_kvs.values()} vs {py_kvs.values()}"
#     print(pb_kvs)


def assert_equal_property_names(pybind_class: type, pydantic_class: type):
    pb_keys = []
    for k, v in vars(pybind_class).items():
        if k == "valid":
            continue
        if isinstance(v, property):
            pb_keys.append(k)

    pd_keys = []
    for k, v in pydantic_class.__annotations__.items():
        if k == "valid" or k.startswith("_"):
            continue
        pd_keys.append(k)

    assert set(pb_keys) == set(pd_keys), f"Keys not equal: {set(pb_keys) ^ set(pd_keys)}"
