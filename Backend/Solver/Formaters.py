from Backend.Solver.ClassBuilder import build_RouteMatrix
from Backend.Solver.calculation import Calculation, assign_transport_from_calculation, List, solve_array_RouteMatrix

def transport_assigned_formatter(solution : Calculation, transports):
    formatted_output = {}
    transport_routes = assign_transport_from_calculation(solution, transports)
    for transport in transport_routes:
        for route in transport_routes[transport]:
            route_data = route.raw_data
            entry = formatted_output.get(transport.name)
            if entry == None:
                formatted_output[transport.name] = {}
                entry = formatted_output[transport.name]
            if entry.get("routes") == None:
                entry["routes"] = {}
            entry["routes"][(route_data["from"], route_data["to"])] = route_data
            if entry.get("warehouses") == None:
                entry["warehouses"] = {}
            entry["warehouses"][route_data["from"]] = {route_data["from_address"]}
            if entry.get("destinations") == None:
                entry["destinations"] = {}
            entry["destinations"][route_data["to"]] = {route_data["to_address"]}
    return formatted_output

def statistics_formatter(solution : Calculation, additional_costs = 0):
    formatted_output = {"length" : solution.distance_overall, "cost" : solution.cost_overall + additional_costs}
    warehouses = set()
    destinations = set()
    for rcw in solution:
        pair = rcw[0].get_ptrs()
        warehouses.add(pair[0])
        destinations.add(pair[1])
    formatted_output["warehouses_count"] = len(warehouses)
    formatted_output["destinations_count"] = len(destinations)
    return formatted_output

def double_formatter(solution : Calculation, transports, additional_costs = 0):
    statistics = statistics_formatter(solution, additional_costs)
    transports_formatted = transport_assigned_formatter(solution, transports)
    statistics["truck_count"] = len(transports_formatted)
    return (statistics, transports_formatted)

def array_double_formatter(solutions : List[Calculation], transports, additional_costs = 0):
    result = []
    for solution in solutions:
        result.append(double_formatter(solution, transports, additional_costs))
    return result

def array_simple_formatter(storages, routes, transports, additional_costs = 0, cost_per_distance = 0.0):
    routeMatrices = build_RouteMatrix(storages, routes)
    calculations = solve_array_RouteMatrix(routeMatrices, cost_per_distance)
    return array_double_formatter(calculations, transports, additional_costs)