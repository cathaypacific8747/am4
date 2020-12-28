import ctypes

f = ctypes.CDLL('./helper_c.so')

# initialise ticket prices functions.
yTicket_easy = f.yTicket_easy
yTicket_easy.argtypes = [ctypes.c_double]
yTicket_easy.restype = ctypes.c_int

jTicket_easy = f.yTicket_easy
jTicket_easy.argtypes = [ctypes.c_double]
jTicket_easy.restype = ctypes.c_int

fTicket_easy = f.yTicket_easy
fTicket_easy.argtypes = [ctypes.c_double]
fTicket_easy.restype = ctypes.c_int

yTicket_realism = f.yTicket_easy
yTicket_realism.argtypes = [ctypes.c_double]
yTicket_realism.restype = ctypes.c_int

jTicket_realism = f.yTicket_easy
jTicket_realism.argtypes = [ctypes.c_double]
jTicket_realism.restype = ctypes.c_int

fTicket_realism = f.yTicket_easy
fTicket_realism.argtypes = [ctypes.c_double]
fTicket_realism.restype = ctypes.c_int

lTicket_easy = f.lTicket_easy
lTicket_easy.argtypes = [ctypes.c_double]
lTicket_easy.restype = ctypes.c_double

hTicket_easy = f.lTicket_easy
hTicket_easy.argtypes = [ctypes.c_double]
hTicket_easy.restype = ctypes.c_double

lTicket_realism = f.lTicket_easy
lTicket_realism.argtypes = [ctypes.c_double]
lTicket_realism.restype = ctypes.c_double

hTicket_realism = f.lTicket_easy
hTicket_realism.argtypes = [ctypes.c_double]
hTicket_realism.restype = ctypes.c_double
# loaded all ticket functions

f.initAirports.argtypes = None
f.initAirports.restype = ctypes.c_bool
f.initAirports()

class paxConf(ctypes.Structure):
    _fields_ = [("yConf", ctypes.c_int), ("jConf", ctypes.c_int), ("fConf", ctypes.c_int), ("maxIncome", ctypes.c_double), ("planesPerRoute", ctypes.c_int)]

class cargoConf(ctypes.Structure):
    _fields_ = [("lPct", ctypes.c_double), ("hPct", ctypes.c_double), ("maxIncome", ctypes.c_double), ("planesPerRoute", ctypes.c_int)]

brutePaxConf = f.brutePaxConf
brutePaxConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
brutePaxConf.restype = paxConf

bruteCargoConf = f.bruteCargoConf
bruteCargoConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
bruteCargoConf.restype = cargoConf

distance = f.distance
distance.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
distance.restype = ctypes.c_double

class stopoverEntry(ctypes.Structure):
    _fields_ = [("apId", ctypes.c_int), ("toO", ctypes.c_double), ("toD", ctypes.c_double)]

stopover = f.stopover
stopover.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
stopover.restype = stopoverEntry