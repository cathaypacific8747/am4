import ctypes
import time

f = ctypes.CDLL('./am4functions.so')

if True:
    if True:
        yTicket_easy = f.yTicket_easy
        yTicket_easy.argtypes = [ctypes.c_double]
        yTicket_easy.restype = ctypes.c_int

    brutePaxConf = f.brutePaxConf
    brutePaxConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    brutePaxConf.restype = ctypes.POINTER(ctypes.c_int)

    bruteCargoConf = f.bruteCargoConf
    bruteCargoConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    bruteCargoConf.restype = ctypes.POINTER(ctypes.c_int)

# result = brutePaxConf(1600, 200, 100, 440, 3, 4777, 69, True)
# result = bruteCargoConf(60000, 99999, 100000, 1, 1, 1, 10000, 100, False)
# print([result[i] for i in range(3)])

res = f.yTicket_easy(10010)
print(res, type(res))