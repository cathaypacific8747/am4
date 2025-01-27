import asyncio
import io
import pickle
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cmocean
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from pyproj import CRS, Transformer

from .utils import format_num

_executor = ProcessPoolExecutor(max_workers=1)


class MPLMap:
    def __init__(self):
        self.transformer = Transformer.from_crs(4326, CRS.from_string("+proj=peirce_q +lon_0=25 +shape=square"))
        self.init_template()
        self.cmap = cmocean.tools.crop_by_percent(cmocean.cm.dense_r, 30, which="min")
        self.cmap2 = cmocean.tools.crop_by_percent(cmocean.cm.curl, 50)

    def init_template(self):
        plt.style.use("dark_background")
        ext = 2**24

        font_path = Path(__file__).parent / "assets" / "font" / "B612-Regular.ttf"
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams.update(
            {
                "font.family": prop.get_name(),
                "axes.facecolor": "#16171a",
                "savefig.facecolor": "#1f2024",
                "legend.fontsize": 10 * 0.9,
                "legend.handlelength": 2 * 0.9,
            }
        )

        fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), layout="tight")
        ax3 = ax2.twiny()

        ax: plt.Axes
        ax.set_axis_off()
        ax.set_xlim(-ext, ext)
        ax.set_ylim(-ext, ext)

        ax2: plt.Axes
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position("right")
        ax2.set_xlabel("distance, km")
        ax2.set_ylabel("profit, $/d/ac")

        ax3: plt.Axes
        ax3.set_xlabel("#aircraft")
        ax3.invert_xaxis()
        d = Path(__file__).parent / "assets" / "img" / "map.jpg"  # peirce_quincuncial
        im = np.array(PIL.Image.open(d))
        self.template = pickle.dumps((fig, ax, ax2, ax3, im))
        plt.close(fig)

    def _plot_destinations(
        self,
        cols: dict[str, list],
        origin_lng: float,
        origin_lat: float,
    ) -> io.BytesIO:
        fig, ax, ax2, ax3, im = pickle.loads(self.template)
        fig: Figure
        ax: plt.Axes
        ax2: plt.Axes
        ax3: plt.Axes
        im: np.ndarray

        # FIXME: see https://github.com/matplotlib/matplotlib/issues/28448
        ext = 2**24
        ax.imshow(im.astype(np.uint16), extent=[-ext, ext, -ext, ext])

        lats = cols["98|dest.lat"]
        lngs = cols["99|dest.lng"]
        tpdpas = np.array(cols["32|trips_pd_pa"])
        profits = np.array(cols["39|profit_pt"]) * tpdpas
        sc_d = ax.scatter(*self.transformer.transform(lats, lngs), c=profits, s=0.5, cmap=self.cmap)
        ax.plot(*self.transformer.transform([origin_lat], [origin_lng]), "ro", markersize=3)
        legend = ax.legend(*sc_d.legend_elements(fmt=FuncFormatter(format_num)), title="$/d/ac")

        ac_needs = cols["33|num_ac"]
        c = 0
        y1 = []
        for acn, pro in zip(ac_needs, profits):
            for _ in range(acn):
                y1.append(pro)
                c += 1

        binwidth = 10000
        bins = np.arange(min(y1), max(y1) + binwidth, binwidth)
        ax3.hist(y1, bins=bins, alpha=0.4, orientation="horizontal")

        dists = cols["30|direct_dist"]
        sc_tpdpa = ax2.scatter(dists, profits, s=1.5, c=tpdpas, cmap=self.cmap2)
        legend = ax2.legend(*sc_tpdpa.legend_elements(), title="t/d/ac", loc="upper left")
        ax2.add_artist(legend)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpg", dpi=200)
        buf.seek(0)
        plt.close(fig)
        return buf

    async def plot_destinations(
        self,
        cols: dict[str, list],
        origin_lng: float,
        origin_lat: float,
    ) -> io.BytesIO:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._plot_destinations, cols, origin_lng, origin_lat)


mpl_map = MPLMap()
