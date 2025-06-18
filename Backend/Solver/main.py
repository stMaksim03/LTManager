import RouteClasses as rc
import BaseClasses as bc
from Calculation import solve
from ClassBuilder import *
import randomdata as rd
import Calculation as calc
import Formaters as forms
import json

def main():

    #Генерация тестовых json файлов
    warehouses_json = rd.generate_warehouses_json(10)
    receivers_json = rd.generate_receivers_json(10)
    routes_json = rd.generate_all_routes_json(warehouses_json, receivers_json)
    transport_json = rd.generate_transport_json(10)
    
    #Конвертация в классы (Сразу целым массивом)
    storages = build_ProductStorage_from_json(warehouses_json)
    receivers = build_ProductStorage_from_json(receivers_json)
    routes = build_Route_from_json(routes_json, storages + receivers)
    transports = build_Transport_from_json(transport_json)

    #Вывод всей информации в формате
    formatted_data = forms.array_simple_formatter(storages, routes, transports, 1.0)

    #Вывод статистики для каждого решения
    for pair in formatted_data:
        statistic = pair[0]
        print("------------------------------------")
        print(statistic["length"])
        print(statistic["cost"])
        print(statistic["warehouses_count"])
        print(statistic["destinations_count"])
        print(statistic["truck_count"])
    '''
    for calculation in calculations:
        formatted_transports = forms.transport_assigned_formatter(calculation, transports)
        statistic = forms.statistics_formatter(calculation)
        print("------------------------------------")
        print(statistic["length"])
        print(statistic["cost"])
        print(statistic["warehouses_count"])
        print(statistic["destinations_count"])
    '''
    '''
    for st in storages:
        print(st.address)
        print(st.name)
        for prod in st:
            print(prod)
    for st in receivers:
        print(st.address)
        print(st.name)
        for prod in st:
            print(prod)
    print(f"routes count: {len(routes)}")
    for route in routes:
        print(f"from: {route.storage_ptr.name} to {route.receiver_ptr.name}")
        print(f"length: {route.length}")
    print("------matrix info-----")
    print(f"count: {len(routeMatrices)}")
    for matrix in routeMatrices:
        print(f"{matrix}")
        print(f"{matrix.lines}, {matrix.columns}, {matrix.product}")
        for i in range(matrix.lines):
            for j in range(matrix.columns):
                r = matrix.get_by_indices(i, j)
                print(f"route_obj at {i}, {j}: from {matrix.get_storage_vector()[i].name} to {matrix.get_receiver_vector()[j].name}")
                print(f"from: {r.storage_ptr.name} to {r.receiver_ptr.name}")
    print("-----Calculation Info-----")
    for solution in calc.solve_array_RouteMatrix(routeMatrices, 1.0):
        print(solution.cost_overall)
        for route in solution:
            print(route[0].raw_data)
        tr = calc.assign_transport_from_calculation(solution, build_Transport_from_json(transport_json))
        for transport in tr:
            print(f"For {transport.name} id: {transport.id} routes:")
            for route in tr[transport]:
                print(f"from: {route.storage_ptr.name} to {route.receiver_ptr.name}")
                print(f"length: {route.length}")
    #print(transport_json)
    '''
        
    '''
    a = bc.ProductStorage("zavod", 0)
    a.insert(bc.Product(0, "apple", 2), 2)
    a.insert(bc.Product(1, "orange", 0.5), 6)
    a.insert(bc.Product(2, "lemon", 2.5), 10)
    a.insert(bc.Product(3, "bomb", 20), 100)
    for product, count in a:
        print(f"{product.id} {product.name} {product.weight} {count}")
    a = rc.Route()
    supply = [10, 20, 30]
    demand = [15, 20, 25]
    cost = [[5, 3, 1], [3, 2, 4], [4, 1, 2]]

    result = solve(supply, demand, cost)
    print(result)
    '''
    return 0
    
main()
