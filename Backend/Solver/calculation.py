import ctypes
import numpy as np

lib = ctypes.CDLL("./libsolver.so")

lib.solveTransport.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int
]
lib.solveTransport.restype = ctypes.POINTER(ctypes.c_int)

def solve(supply, demand, cost):
    sl = len(supply)
    dl = len(demand)

    supply_c = (ctypes.c_int * sl)(*supply)
    demand_c = (ctypes.c_int * dl)(*demand)

    flat_cost = [cost[i][j] for i in range(sl) for j in range(dl)]
    cost_c = (ctypes.c_int * (sl * dl))(*flat_cost)

    result_ptr = lib.solveTransport(
        supply_c, sl, demand_c, dl,
        cost_c, sl, dl
    )

    result = np.ctypeslib.as_array(result_ptr, shape=(sl * dl,))
    return result.reshape((sl, dl))


