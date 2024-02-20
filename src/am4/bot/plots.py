import io
import pickle
from pathlib import Path

import cmocean
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from am4.utils.route import AircraftRoute, Destination
from matplotlib.figure import Figure
from pyproj import CRS, Transformer


class MPLMap:
    def __init__(self):
        self.transformer = Transformer.from_crs(4326, CRS.from_string("+proj=peirce_q +lon_0=25 +shape=square"))
        self.init_template()
        self.cmap = cmocean.tools.crop_by_percent(cmocean.cm.ice, 30, which="min")
        self.cmap2 = cmocean.tools.crop_by_percent(cmocean.cm.curl, 50)

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

    def plot_destinations(
        self,
        destinations: list[Destination],
        origin_lng: float,
        origin_lat: float,
        sort_by: AircraftRoute.Options.SortBy,
    ) -> io.BytesIO:
        fig, ax, ax2 = pickle.loads(self.template)
        fig: Figure
        ax: plt.Axes
        ax2: plt.Axes

        # per_trip = sort_by == AircraftRoute.Options.SortBy.PER_TRIP
        dists, tpdpacs = [], []
        lats, lngs, profits, ac_needs = [], [], [], []
        for d in destinations:
            dists.append(d.ac_route.route.direct_distance)
            tpdpacs.append(d.ac_route.trips_per_day / d.ac_route.ac_needed)
            lats.append(d.airport.lat)
            lngs.append(d.airport.lng)
            profits.append(
                # d.ac_route.profit if per_trip else d.ac_route.profit * d.ac_route.trips_per_day / d.ac_route.ac_needed
                d.ac_route.profit * d.ac_route.trips_per_day / d.ac_route.ac_needed
            )
            ac_needs.append(d.ac_route.ac_needed)
        ax.scatter(*self.transformer.transform(lats, lngs), c=profits, s=0.5, cmap=self.cmap)
        ax.plot(*self.transformer.transform([origin_lat], [origin_lng]), "ro", markersize=3)

        c = 0
        y1 = []
        for acn, pro in zip(ac_needs, profits):
            for _ in range(acn):
                y1.append(pro)
                c += 1

        ax3 = ax2.twiny()
        binwidth = 7500
        bins = np.arange(min(y1), max(y1) + binwidth, binwidth)
        ax3.hist(y1, bins=bins, alpha=0.5, orientation="horizontal")
        ax3.set_xlabel("#aircraft")
        ax3.invert_xaxis()

        # tpdpacs = np.array(tpdpacs)
        ax2.scatter(dists, profits, s=1.5, c=tpdpacs - np.median(tpdpacs), cmap=self.cmap2)
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position("right")
        ax2.set_xlabel("distance, km")
        ax2.set_ylabel("profit, $/d/ac")

        # for tpd in

        buf = io.BytesIO()
        fig.savefig(buf, format="jpg")
        buf.seek(0)
        plt.close(fig)
        return buf


mpl_map = MPLMap()
