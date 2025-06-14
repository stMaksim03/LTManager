import ctypes
import numpy as np
import RouteClasses as rc
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

lib = ctypes.CDLL("./libsolver.so")

lib.solveTransport.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int
]
lib.solveTransport.restype = ctypes.POINTER(ctypes.c_int)

lib.FreeResult.argtypes = [ctypes.POINTER(ctypes.c_int)]
lib.FreeResult.restype = None

def solve_array_RouteMatrix(routeMatrices: List[rc.RouteMatrix], cost_per_distance):
    calculations = []
    for matrix in routeMatrices:
        solution = Calculation.from_data(matrix, solve_from_RouteMatrix(matrix), cost_per_distance)
        calculations.append(solution)
    return calculations

def solve_from_RouteMatrix(routeMatrix: rc.RouteMatrix):
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
    print("----- Before the solve ------")
    print(f"supply length: {len(supply)}")
    print(f"supply: {supply}")
    print(f"demand length: {len(demand)}")
    print(f"demand: {demand}")
    print(f"cost: {cost}")
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

@dataclass
class Calculation:
    id: int = -1
    routeMatrix: rc.RouteMatrix = None
    solvedMatrix: List[List[int]] = field(default_factory=list)
    route_values: Dict[rc.Route, Tuple[float, float]] = field(default_factory=dict)
    cost_per_distance: float = 0.0
    cost_overall: float = 0.0
    aux_costs: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_data(cls, routeMatrix, solvedMatrix, cost_per_distance: float):
        obj = cls(routeMatrix=routeMatrix, solvedMatrix=solvedMatrix, cost_per_distance=cost_per_distance)
        obj.calculateRoutes()
        obj.calculateCost()
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
                    cost_weight = (route.length * self.cost_per_distance, self.solvedMatrix[storage_ind][receiver_ind] * self.routeMatrix.product.weight)
                    self.route_values[route] = cost_weight

    def calculateCost(self):
        result = 0
        try:
            if len(self.route_values) > 0 and self.cost_per_distance != 0.0:
                for cw in self:
                    result += cw[1][0]
        except:
            print("A problem occured during calculation")
        self.cost_overall = result
        return result
    
            
