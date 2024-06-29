# %%
# from collections import namedtuple

# Ac = namedtuple("Aircraft", ["name", "check_cost", "expected_hours"])
from dataclasses import dataclass


@dataclass
class Ac:
    name: str
    check_cost: int
    expected_hours: str = None


data = [
    Ac("Concorde", 87678720, "245"),
    Ac("SJM90", 20748122, "59"),
    Ac("A388", 12937770, "37"),
    Ac("B744D", 11217520, "37"),
    Ac("B773", 9898588, "29.5"),
    Ac("B748", 8476840, "25"),
    Ac("B747SP", 3878280, "12"),
    Ac("B779X", 3646040, None),
    Ac("A359", 2820122, None),
    Ac("MC214", 494428, "2.5"),
    # below are off by 30mins
    Ac("point0", 3646040, None),
    Ac("point1", 2820122, None),
    Ac("cathayexpress-mc214-bulk", 247214, 4273 * 60 * 60),
]


def downtime(wear_pct: float, check_cost: int) -> float:
    return 480000 * wear_pct + 3600 + 0.01 * check_cost + 1860


def ftime(seconds: float) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


for ac in data:
    dt = ftime(downtime(0, ac.check_cost))
    print(f"{ac.name:8} {ac.check_cost:>9} {dt:>9}")

# %%
ftime(4273)

# %%
