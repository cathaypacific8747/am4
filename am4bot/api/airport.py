class Airport:
    def __init__(self, id, city, country, iata, icao, runway, market, lat, lng) -> None:
        self.id = int(id)
        self.city = str(city)
        self.country = str(country)
        self.iata = str(iata)
        self.icao = str(icao)
        self.runway = int(runway)
        self.market = int(market)
        self.lat = float(lat)
        self.lng = float(lng)