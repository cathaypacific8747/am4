import io
import pickle
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


class MPLMap:
    def __init__(self):
        # setup the style and font
        font_path = Path(__file__).parent / "assets" / "font" / "B612-Regular.ttf"
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        self.rc_params = {
            "font.family": prop.get_name(),  # "B612"
            "axes.facecolor": "#16171a",
            "savefig.facecolor": "#1f2024",
            "legend.fontsize": 10 * 0.9,
            "legend.handlelength": 2 * 0.9,
            "text.color": "white",
            "axes.labelcolor": "white",
            "axes.edgecolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
        }

        self.template_routes = self.create_routes_template()
        self.cmap = cmocean.tools.crop_by_percent(cmocean.cm.dense_r, 30, which="min")
        self.cmap2 = cmocean.tools.crop_by_percent(cmocean.cm.curl, 50)
        self.wgs84_to_pierceq = Transformer.from_crs(4326, CRS.from_string("+proj=peirce_q +lon_0=25 +shape=square"))

    def create_routes_template(self):
        """Create a blank template for the routes plot, which will be unpickled later to draw the plot."""
        plt.style.use("dark_background")
        ext = 2**24

        plt.rcParams.update(self.rc_params)

        fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), layout="tight")
        ax3 = ax2.twiny()

        ax: plt.Axes
        ax.set_axis_off()
        ax.set_xlim(-ext, ext)
        ax.set_ylim(-ext, ext)

        ax2: plt.Axes
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position("right")
        ax2.set_xlabel("direct distance, km")
        ax2.set_ylabel("profit, $/d/ac")

        ax3: plt.Axes
        ax3.set_xlabel("#aircraft")
        ax3.invert_xaxis()
        d = Path(__file__).parent / "assets" / "img" / "map.jpg"  # peirce_quincuncial
        im = np.array(PIL.Image.open(d))

        # old bug eliminated: see https://github.com/matplotlib/matplotlib/issues/28448
        ext = 2**24
        ax.imshow(im.astype(np.uint16), extent=[-ext, ext, -ext, ext])

        template = pickle.dumps((fig, ax, ax2, ax3))
        plt.close(fig)
        return template

    def _plot_destinations(
        self,
        cols: dict[str, list],
        origin_lngs: list[float],
        origin_lats: list[float],
    ) -> io.BytesIO:
        fig, ax, ax2, ax3 = pickle.loads(self.template_routes)
        fig: Figure
        ax: plt.Axes
        ax2: plt.Axes
        ax3: plt.Axes

        lats = cols["98|dest.lat"]
        lngs = cols["99|dest.lng"]
        tpdpas = np.array(cols["32|trips_pd_pa"])
        profits = np.array(cols["39|profit_pt"]) * tpdpas
        sc_d = ax.scatter(*self.wgs84_to_pierceq.transform(lats, lngs), c=profits, s=0.5, cmap=self.cmap)
        ax.plot(*self.wgs84_to_pierceq.transform(origin_lats, origin_lngs), "ro", markersize=3)
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
