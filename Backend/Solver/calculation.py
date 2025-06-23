import ctypes
import os
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from . import RouteClasses as rt
from . import BaseClasses as bc

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, "libsolver.dll")

try:
    lib = ctypes.CDLL(lib_path)
except Exception as e:
    raise RuntimeError(f"Failed to load library: {lib_path}. Error: {str(e)}")

lib.solveTransport.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int
]
lib.solveTransport.restype = ctypes.POINTER(ctypes.c_int)

lib.FreeResult.argtypes = [ctypes.POINTER(ctypes.c_int)]
lib.FreeResult.restype = None

@dataclass
class Calculation:
    id: int = -1
    routeMatrix: rt.RouteMatrix = None
    solvedMatrix: List[List[int]] = field(default_factory=list)
    route_values: Dict[rt.Route, Tuple[float, float]] = field(default_factory=dict)
    distance_overall: int = 0
    cost_per_distance: float = 1.0
    cost_overall: float = 0.0
    aux_costs: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_data(cls, routeMatrix, solvedMatrix, cost_per_distance: float):
        obj = cls(routeMatrix=routeMatrix, solvedMatrix=solvedMatrix, cost_per_distance=cost_per_distance)
        obj.calculateRoutes()
        return obj

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)

    def __iter__(self):
        return iter(self.route_values.items())
    
    def calculateRoutes(self):
        for storage_ind in range(len(self.solvedMatrix)):
            for receiver_ind in range(len(self.solvedMatrix[0])):
                if (self.solvedMatrix[storage_ind][receiver_ind] > 0):
                    route = self.routeMatrix.get_by_indices(storage_ind, receiver_ind)
                    self.distance_overall += route.length
                    self.route_values[route] = self.solvedMatrix[storage_ind][receiver_ind] * self.routeMatrix.product.weight

def solve_array_RouteMatrix(routeMatrices: List[rt.RouteMatrix], cost_per_distance):
    calculations = []
    for matrix in routeMatrices:
        solution = Calculation.from_data(matrix, solve_from_RouteMatrix(matrix), cost_per_distance)
        calculations.append(solution)
    return calculations

def solve_from_RouteMatrix(routeMatrix: rt.RouteMatrix):
    lines = routeMatrix.lines
    columns = routeMatrix.columns
    supply = [0] * lines
    demand = [0] * columns
    product = routeMatrix.product
    cost = []
    for line in range(lines):
        cost.append([0]*columns)
        for column in range(columns):
            route = routeMatrix.get_by_indices(line, column)
            storage = routeMatrix.storages[line].stored_products
            receiver = routeMatrix.receivers[column].stored_products
            supply[line] = storage[product] if supply[line] == 0 else supply[line]
            demand[column] = receiver[product] if demand[column] == 0 else demand[column]
            cost[line][column] = route.length
    #print("----- Before the solve ------")
    #print(f"supply length: {len(supply)}")
    #print(f"supply: {supply}")
    #print(f"demand length: {len(demand)}")
    #print(f"demand: {demand}")
    #print(f"cost: {cost}")
    return solve(supply, demand, cost)


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

    result = np.ctypeslib.as_array(result_ptr, shape=(sl * dl,)).copy()

    lib.FreeResult(result_ptr)

    return result.reshape((sl, dl))

def assign_transport_to_routes(route_weight, transports: List[bc.Transport]):
    min_cost = -1
    chosen_transport = None 
    for transport in transports:
        wl = transport.weight_lift
        trips = 1
        if wl < route_weight[1]:
            trips = (route_weight[1] // wl) + 1
        cost = route_weight[0].length * transport.fuel_cost * trips
        if cost <= min_cost or min_cost == -1:
            min_cost = cost
            chosen_transport = transport
    return (chosen_transport, route_weight[0], cost)

def assign_transport_from_calculation(calculation: Calculation, transports: List[bc.Transport]):
    result = {}
    for rw in calculation:
        tr, rt, cost = assign_transport_to_routes(rw, transports)
        entry = result.get(tr)
        if entry == None:
            result[tr] = []
            calculation.cost_overall += cost * calculation.cost_per_distance
        result[tr].append(rt)
    return result