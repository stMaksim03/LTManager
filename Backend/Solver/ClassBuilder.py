from typing import List, Dict
from itertools import count
from . import BaseClasses as bc
from . import RouteClasses as rc


product_id_counter = count(start=1)
product_registry: Dict[str, bc.Product] = {}

def build_RouteMatrix(storages, routes):
    #print("-----building matrix------")
    result = set()
    products = set()
    for storage in storages:
        for prod in storage:
            if prod[0] not in products:
                products.add(prod[0])
    #print(products)
    for prod in products:
        routeMatrix = rc.RouteMatrix(prod)
        for route in routes:
            #print(prod)
            #print(route.storage_ptr.stored_products.keys())
            #print(route.receiver_ptr.stored_products.keys())
            if prod in route.storage_ptr.stored_products.keys() and prod in route.receiver_ptr.stored_products.keys():
                routeMatrix.set_at(route.storage_ptr, route.receiver_ptr, route)
        result.add(routeMatrix)
    return result

def get_or_create_product(name: str, weight: str, weight_coef = 1.0) -> bc.Product:
    if name not in product_registry:
        product_registry[name] = bc.Product(
            id=next(product_id_counter),
            name=name,
            weight=float(weight) * weight_coef
        )
    return product_registry[name]

def build_ProductStorage_from_json(warehouses_json: List[Dict], weight_coef = 1.0) -> List[bc.ProductStorage]:
    result = []
    for entry in warehouses_json:
        storage = bc.ProductStorage(name=entry["name"], address=entry["address"])
        for cargo in entry.get("cargos", []):
            #print(cargo)
            product = get_or_create_product(cargo["type"], cargo["weight"], weight_coef)
            quantity = int(cargo["quantity"])
            storage.insert(product, quantity)
        result.append(storage)
    return result

def build_Route_from_json(
    routes_json: List[Dict],
    all_storages: List[bc.ProductStorage],
    distance_coef: int = 1
) -> List[rc.Route]:
    

    route_id_counter = count(start=1)
    storage_lookup = {(s.name, s.address): s for s in all_storages}
    route_objects = []

    for route in routes_json:
        from_key = (route["from"], route["from_address"])
        to_key = (route["to"], route["to_address"])

        storage = storage_lookup.get(from_key)
        receiver = storage_lookup.get(to_key)

        if not storage or not receiver:
            continue

        route_obj = rc.Route()
        route_obj.id = next(route_id_counter)
        route_obj.length = int(route.get("distance_m", -1)) * distance_coef
        route_obj.storage_ptr = storage
        route_obj.receiver_ptr = receiver
        route_obj.raw_data = route

        route_objects.append(route_obj)

    return route_objects

def build_Transport_from_json(transport_json: List[Dict], weight_lift_coef = 1.0, fuel_cost_coef = 1.0) -> List[bc.Transport]:
    transport_objects = []
    id_counter = count(start=1)
    for transport in transport_json:
        wl = 0
        fc = 1.0
        try:
            wl = float(transport.get("capacity", "-1")) * weight_lift_coef
            fc = float(transport.get("fuel", "1")) * fuel_cost_coef
        except:
            pass
        transport_objects.append(bc.Transport(
            id = next(id_counter),
            name = transport.get("name", "unnamed"),
            fuel_cost = fc,
            weight_lift = wl
            
        ))
    return transport_objects