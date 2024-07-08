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
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

df = pl.read_csv("check_cost.csv").with_columns(
    check_cost=pl.col("check_cost").str.replace_all("[$,]", "").cast(pl.Float64)
)
x, y = df["check_cost"].to_numpy(), df["check_time"].to_numpy() * 3600

SLOPE = 0.01

intercept = np.mean(y - SLOPE * x)

y_pred = SLOPE * x + intercept
residuals = y - y_pred

n = len(x)
sigma_squared = np.sum(residuals**2) / (n - 1)
sum_x_squared = np.sum(x**2)
se_intercept = np.sqrt(sigma_squared * sum_x_squared / (n * sum_x_squared - np.sum(x) ** 2))

xs = np.linspace(x.min(), x.max(), 100)
ys = SLOPE * xs + intercept
label = f"{SLOPE}x + {intercept:.6g}, SE = {se_intercept:.6g}"

plt.style.use("dark_background")
plt.plot(xs, ys, "--", label=label)
plt.scatter(x, y)
plt.xlabel("Check Cost ($)")
plt.ylabel("Check Time (s)")
plt.legend()
plt.show()

# %%
