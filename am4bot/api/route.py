import math

from .airport import Airport

class Route:
    def __init__(self, a1: Airport, a2: Airport):
        self.a1 = a1
        self.a2 = a2
    
    # def set_demands(self, yd: int, jd: int, fd: int):
    #     self.yd = yd
    #     self.jd = jd
    #     self.fd = fd
    
    # def set_distance(self, distance):
    #     self.distance = distance

    def get_distance(self):
        lat1, lat2, lng1, lng2 = self.a1.lat, self.a2.lat, self.a1.lng, self.a2.lng
        return 12742 * math.asin(math.sqrt(math.pow(math.sin((lat2-lat1) / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lng2-lng1) / 2), 2)))