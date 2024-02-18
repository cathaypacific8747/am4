import io
import pickle
from dataclasses import dataclass
from pathlib import Path

import cmocean
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from pyproj import CRS, Transformer


@dataclass
class DestinationData:
    lngs: list[float]
    lats: list[float]
    profits: list[float]
    ac_needs: list[int]
    origin_lng: float
    origin_lat: float


class MPLMap:
    def __init__(self):
        self.transformer = Transformer.from_crs(4326, CRS.from_string("+proj=peirce_q +lon_0=25 +shape=square"))
        self.init_template()
        self.cmap = cmocean.tools.crop_by_percent(cmocean.cm.ice, 30, which="min", N=None)

    def init_template(self):
        plt.style.use("dark_background")
        ext = 2**24

        font_path = Path(__file__).parent / "assets" / "font" / "B612-Regular.ttf"
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams.update({"font.family": prop.get_name()})

        fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), layout="tight")
        ax: plt.Axes
        ax.set_axis_off()
        ax.set_xlim(-ext, ext)
        ax.set_ylim(-ext, ext)
        d = Path(__file__).parent / "assets" / "img" / "map.jpg"  # peirce_quincuncial
        ax.imshow(plt.imread(d), extent=[-ext, ext, -ext, ext])
        self.template = pickle.dumps((fig, ax, ax2))
        plt.close(fig)

    def plot_destinations(self, data: DestinationData) -> io.BytesIO:
        fig, ax, ax2 = pickle.loads(self.template)
        fig: Figure
        ax: plt.Axes
        ax2: plt.Axes
        ax.scatter(*self.transformer.transform(data.lats, data.lngs), c=data.profits, s=0.5, cmap=self.cmap)
        ax.plot(*self.transformer.transform([data.origin_lat], [data.origin_lng]), "ro", markersize=3)

        c = 0
        y1 = []
        for acn, pro in zip(data.ac_needs, data.profits):
            for _ in range(acn):
                y1.append(pro)
                c += 1

        binwidth = 7500
        bins = np.arange(min(y1), max(y1) + binwidth, binwidth)
        ax2.hist(y1, bins=bins, alpha=0.7)
        ax2.set_xlabel("profit/t/ac")
        ax2.set_ylabel("#aircraft")
        ax2.set_title("Income distribution")

        buf = io.BytesIO()
        fig.savefig(buf, format="jpg")
        buf.seek(0)
        plt.close(fig)
        return buf


mpl_map = MPLMap()
