import random

def generate_warehouses_json(n=3):
    warehouses = []
    for i in range(1, n + 1):
        cargos = []
        for j in range(random.randint(1, 3)):
            cargo = {
                'type': f'P{random.randint(1, 5)}',
                'quantity': str(random.randint(1, 20)),
                'weight': str(round(random.uniform(0.5, 5.0), 1))
            }
            cargos.append(cargo)
        warehouses.append({
            'name': f'stor{i}',
            'address': f'addr{i}',
            'cargos': cargos
        })
    return warehouses

def generate_receivers_json(n=3):
    receivers = []
    for i in range(1, n + 1):
        cargos = []
        for j in range(random.randint(1, 3)):
            cargo = {
                'type': f'P{random.randint(1, 5)}',
                'quantity': str(random.randint(1, 15)),
                'weight': str(round(random.uniform(0.5, 5.0), 1))
            }
            cargos.append(cargo)
        receivers.append({
            'name': f'rec{i}',
            'address': f'addr{i + 100}',  # чтобы не пересекались с адресами складов
            'cargos': cargos
        })
    return receivers

def generate_all_routes_json(warehouses_json, receivers_json):
    routes = []
    for wh in warehouses_json:
        for rc in receivers_json:
            route = {
                'from': wh['name'],
                'from_address': wh['address'],
                'to': rc['name'],
                'to_address': rc['address'],
                'distance_m': random.randint(1000, 5000),
                'duration_min': random.randint(5, 25),
                'path': [
                    [round(random.uniform(55.75, 55.76), 6), round(random.uniform(37.61, 37.63), 6)],
                    [round(random.uniform(55.75, 55.76), 6), round(random.uniform(37.61, 37.63), 6)]
                ]
            }
            routes.append(route)
    return routes
