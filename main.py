# remember to run 
import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', milliseconds=True)

# standard modules
import ctypes
import time

if True: # initialise and setup C functions
    f = ctypes.CDLL('./am4functions.so')

    if True: # initialise ticket prices functions.
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
        logger.debug("Loaded all ticket functions.")

    f.initAirports.argtypes = None
    f.initAirports.restype = ctypes.c_bool
    if f.initAirports():
        logger.debug("Loaded all airports.")
    else:
        logger.critical("Loading airports failed.")

    brutePaxConf = f.brutePaxConf
    brutePaxConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    brutePaxConf.restype = ctypes.POINTER(ctypes.c_int)

    bruteCargoConf = f.bruteCargoConf
    bruteCargoConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    bruteCargoConf.restype = ctypes.POINTER(ctypes.c_int)
    logger.debug("Loaded all remaining C functions.")

