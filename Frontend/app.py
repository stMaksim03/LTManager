from datetime import timedelta
import re
from flask import Flask, json, request, jsonify, render_template, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import sys
from pathlib import Path

import os
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from Data.Data import DatabaseManager

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000"]
    }
})
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'static_files'

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with DatabaseManager(**DB_CONFIG) as db:
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(user_data.user_id, user_data.username)
    return None

load_dotenv(dotenv_path='C:\MAI\GitHub\LTManager\DB.env')  # Загружает переменные из DB.env

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return render_template(f'/{filename}')

data_storage = {}

@app.route('/validate', methods=['POST'])
def validate_form():
    try:
        global data_storage
        data_storage = {
            'trucks': [],
            'warehouses': [],
            'destinations': [],
            'extraCosts': []
        }

        data = request.get_json()
        
        # Проверка заполненности всех полей
        if not all_fields_filled(data):
            return jsonify({'success': False, 'message': 'Все поля должны быть заполнены'}), 400
        
        # Проверка наличия грузов на складах
        if not validate_warehouse_quantities(data['warehouses'], data['destinations']):
            return jsonify({'success': False, 'message': 'Недостаточное количество груза на складах'}), 400
        
        # Проверка уникальности названий
        if not validate_unique_names(data):
            return jsonify({'success': False, 'message': 'Названия должны быть уникальными в пределах каждой формы'}), 400
        
        data_storage = {
            'trucks': data.get('trucks', []),
            'warehouses': data.get('warehouses', []),
            'destinations': data.get('destinations', []),
            'extraCosts': data.get('extraCosts', [])
        }
        
        return jsonify({'success': True, 'redirect': '/itinerary.html'}), 200   
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка сервера: {str(e)}'}), 500


@app.route('/data')
def get_data():
    global data_storage

    return jsonify({
        'trucks': data_storage['trucks'],
        'warehouses': data_storage['warehouses'],
        'destinations': data_storage['destinations'],
        'extraCosts': data_storage['extraCosts']
    })


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    email_re = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    password_re = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[-!@#$%^&*()_+№;:?=]).{8,}$'

    if not re.match(email_re, email):
        return jsonify({
            'success': False,
            'message': 'Некорректный формат email'
        }), 400
        
    if not re.match(password_re, password):
        return jsonify({
            'success': False,
            'message': 'Пароль должен содержать: 8+ символов, цифры, буквы в разных регистрах и спецсимволы'
        }), 400
    
    with DatabaseManager(**DB_CONFIG) as db:
        user = db.authenticate_user(email, password)
        
        if user:
            user_obj = User(user.user_id, user.username)
            login_user(user_obj)
            return jsonify({'success': True, 'redirect': '/'})
        else:
            return jsonify({'success': False, 'message': 'Ошибка авторизации: неверный email или пароль'})
    
    return render_template('entrance.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')

    email_re = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    password_re = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[-!@#$%^&*()_+№;:?=]).{8,}$'
    
    if not re.match(email_re, email):
        return jsonify({
            'success': False,
            'message': 'Некорректный формат email'
        }), 400
        
    if not re.match(password_re, password):
        return jsonify({
            'success': False,
            'message': 'Пароль должен содержать: 8+ символов, цифры, буквы в разных регистрах и спецсимволы'
        }), 400
    
    with DatabaseManager(**DB_CONFIG) as db:
        try:
            user = db.create_user(email, email, password)
            session['user_id'] = user.user_id
            return jsonify({'success': True, 'redirect': '/entrance.html'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})


@app.route('/check_auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'username': current_user.username})
    return jsonify({'authenticated': False})


@app.route('/creating-task.html')
@login_required
def protected_creating_task():
    return render_template('creating-task.html')


@app.route('/get_db_data')
@login_required
def get_db_data():
    try:
        with DatabaseManager(**DB_CONFIG) as db:
            # Получаем данные текущего пользователя
            user_id = current_user.id
            
            # Получаем продукты пользователя
            products = db._execute_and_fetchall("""
                SELECT product_id, name, weight 
                FROM products 
                WHERE user_id = %s;
            """, (user_id,))
            
            # Получаем склады пользователя
            warehouses = db._execute_and_fetchall("""
                SELECT warehouse_id, name, address, 
                       ST_Y(coordinates::geometry) as lat, 
                       ST_X(coordinates::geometry) as lon
                FROM warehouses 
                WHERE user_id = %s;
            """, (user_id,))
            
            # Получаем инвентарь для каждого склада
            warehouses_data = []
            for warehouse in warehouses:
                inventory = db._execute_and_fetchall("""
                    SELECT p.name as product_name, si.quantity
                    FROM storage_inventory si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.warehouse_id = %s;
                """, (warehouse['warehouse_id'],))
                
                warehouses_data.append({
                    'name': warehouse['name'],
                    'address': warehouse['address'],
                    'cargos': [{
                        'type': item['product_name'],
                        'quantity': item['quantity'],
                        'available': item['quantity']
                    } for item in inventory]
                })

            # Получаем транспорт пользователя (если нужен)
            transports = db._execute_and_fetchall("""
                SELECT name, weight_lift as capacity, fuel_consumption as fuel
                FROM transport 
                WHERE user_id = %s;
            """, (user_id,))

            # Получаем пункты приема пользователя
            collection_points = db._execute_and_fetchall("""
                SELECT point_id, name, address, 
                       ST_Y(coordinates::geometry) as lat, 
                       ST_X(coordinates::geometry) as lon
                FROM collection_points 
                WHERE user_id = %s;
            """, (user_id,))
            
            return jsonify({
                'cargoTypes': [{'name': p['name'], 'weight': p['weight']} for p in products],
                'truckTypes': [{'name': t['name'], 'capacity': t['capacity'], 'fuel': t['fuel']} for t in transports],
                'warehouses': warehouses_data,
                'destinations': [{'name': cp['name'], 'address': cp['address']} for cp in collection_points]
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/logistics')
@login_required
def get_logistics_data():
    global data_storage
    # Если данные есть в памяти — вернуть их
    if data_storage.get('warehouses') and data_storage.get('destinations'):
        return jsonify({
            'warehouses': data_storage.get('warehouses', []),
            'destinations': data_storage.get('destinations', [])
        })

    try:
        with DatabaseManager(**DB_CONFIG) as db:
            user_id = current_user.id

            # Получение складов
            warehouses = db._execute_and_fetchall("""
                SELECT warehouse_id, name, address,
                       ST_Y(coordinates::geometry) AS lat,
                       ST_X(coordinates::geometry) AS lon
                FROM warehouses
                WHERE user_id = %s;
            """, (user_id,))

            # Получение содержимого складов
            warehouses_data = []
            for warehouse in warehouses:
                inventory = db._execute_and_fetchall("""
                    SELECT p.name AS product_name, si.quantity
                    FROM storage_inventory si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.warehouse_id = %s;
                """, (warehouse['warehouse_id'],))

                warehouses_data.append({
                    'name': warehouse['name'],
                    'address': warehouse['address'],
                    'cargos': [{
                        'type': item['product_name'],
                        'quantity': item['quantity'],
                        'available': item['quantity']
                    } for item in inventory]
                })

            # Получение пунктов приёма
            destinations = db._execute_and_fetchall("""
                SELECT name, address,
                       ST_Y(coordinates::geometry) AS lat,
                       ST_X(coordinates::geometry) AS lon
                FROM collection_points
                WHERE user_id = %s;
            """, (user_id,))

            destinations_data = [{
                'name': dest['name'],
                'address': dest['address'],
                'cargos': []
            } for dest in destinations]

            return jsonify({
                'warehouses': warehouses_data,
                'destinations': destinations_data
            })
    # в случае ошибки при получении данных из базы
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


import logging
logging.basicConfig(filename='app.log', level=logging.INFO, filemode='w')
@app.route('/api/compute-routes', methods=['POST'])
def compute_routes():
    try:
        routes_data = request.get_json()
        if not routes_data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # print("Received routes data:", routes_data)  # Для отладки
        # logging.info("Received routes data: %s", routes_data)
        
        # # Получаем данные из хранилища
        global data_storage
        warehouses_data = data_storage.get('warehouses', [])
        destinations_data = data_storage.get('destinations', [])
        trucks_data = data_storage.get('trucks', [])
        extra_costs = data_storage.get('extraCosts', [])
        logging.info("warehouses_data %s", warehouses_data)
        logging.info("destinations_data %s", destinations_data)
        logging.info("trucks_data %s", trucks_data)
        logging.info("extra_costs %s", extra_costs)

        sum_extra_costs = sum(float(cost['value']) for cost in extra_costs if cost.get('value'))
        
        # Строим объекты складов и пунктов приема
        from Backend.Solver.ClassBuilder import build_ProductStorage_from_json, build_Transport_from_json, build_Route_from_json
        from Backend.Solver.Formaters import array_simple_formatter
        
        # Создаем объекты складов
        warehouses = build_ProductStorage_from_json(warehouses_data)
        logging.info("warehouses %s", warehouses)
        
        # Создаем объекты пунктов приема (используем ту же функцию, так как структура похожа)
        destinations = build_ProductStorage_from_json(destinations_data)
        logging.info("destinations %s", destinations)
        
        # Создаем объекты маршрутов
        routes = build_Route_from_json(routes_data, warehouses + destinations)
        # logging.info("routes %s", routes)
        
        # Создаем объекты транспорта
        transports = build_Transport_from_json(trucks_data)
        logging.info("transports %s", transports)
        
        # Вычисляем оптимальные маршруты и распределяем транспорт
        result = array_simple_formatter(
            storages=warehouses,
            routes=routes,
            transports=transports,
            additional_costs=0,
            cost_per_distance=1.0  # Можно изменить на нужное значение
        )

        logging.info("result %s", result)
        
        # Подготавливаем данные для фронтенда
        response_data = {
            'success': True,
            'message': 'Routes computed successfully',
            'statistics': {
                'path_length': 0,
                'total_cost': 0,
                'warehouses_count': 0,
                'destinations_count': 0,
                'truck_count': 0,
                'extra_costs': float(sum_extra_costs)
            },
            'trucks': []
        }

        # Собираем уникальные склады, пункты назначения и машины
        unique_warehouses = set()
        unique_destinations = set()
        unique_trucks = set()

        # Цвета для разных машин
        truck_colors = [
            'islands#blueIcon', 
            'islands#redIcon',
            'islands#greenIcon',
            'islands#yellowIcon',
            'islands#violetIcon'
        ]

        if result:
            for idx, (stats, transport_routes) in enumerate(result):
                # Суммируем длины путей и затраты
                response_data['statistics']['path_length'] += float(stats.get('length', 0))
                response_data['statistics']['total_cost'] += float(stats.get('cost', 0))
                logging.info("stats %s", stats)


                # Собираем уникальные объекты
                for truck_name, truck_data in transport_routes.items():
                    unique_trucks.add(truck_name)
                    
                    # Склады
                    for wh_name in truck_data.get('warehouses', {}).keys():
                        unique_warehouses.add(wh_name)
                    
                    # Пункты назначения
                    for dest_name in truck_data.get('destinations', {}).keys():
                        unique_destinations.add(dest_name)

                # Создаем данные для машин
                for truck_idx, (truck_name, truck_data) in enumerate(transport_routes.items()):
                    truck_info = {
                        'name': str(truck_name),
                        'color': truck_colors[truck_idx % len(truck_colors)],
                        'routes': [],
                        'warehouses': [],
                        'destinations': []
                    }

                    # Обрабатываем маршруты
                    for route_key, route in truck_data.get('routes', {}).items():
                        if isinstance(route_key, tuple):
                            route_key = str(route_key)
                        
                        truck_info['routes'].append({
                            'from': str(route.get('from', '')),
                            'to': str(route.get('to', '')),
                            'from_address': str(route.get('from_address', '')),
                            'to_address': str(route.get('to_address', '')),
                            'distance_m': float(route.get('distance_m', 0)),
                            'path': [[float(coord[0]), float(coord[1])] for coord in route.get('path', [])]
                        })

                    # Обрабатываем склады
                    for wh_name, wh_address in truck_data.get('warehouses', {}).items():
                        truck_info['warehouses'].append({
                            'name': str(wh_name),
                            'address': str(wh_address)
                        })

                    # Обрабатываем пункты назначения
                    for dest_name, dest_address in truck_data.get('destinations', {}).items():
                        truck_info['destinations'].append({
                            'name': str(dest_name),
                            'address': str(dest_address)
                        })

                    response_data['trucks'].append(truck_info)

            # Устанавливаем количество уникальных объектов
            response_data['statistics']['warehouses_count'] = len(unique_warehouses)
            response_data['statistics']['destinations_count'] = len(unique_destinations)
            response_data['statistics']['truck_count'] = len(unique_trucks)
                
            # logging.info("response_data['trucks'] %s", response_data['trucks'])

        # Обновляем глобальное хранилище
        data_storage['computed_routes'] = [response_data]
        # logging.info("response_data['statistics'] %s", response_data['statistics'])

        logging.info("response_data %s", response_data)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/save-routes', methods=['POST'])
def save_routes():  
    return jsonify({'success': True, 'message': 'Routes saved successfully'}), 200


def all_fields_filled(data):
    """Проверка заполненности всех полей"""
    # Получаем настройки маршрута из localStorage (с фронтенда)
    route_settings = request.args.get('route_settings')
    if route_settings:
        route_settings = json.loads(route_settings)
    else:
        # Значения по умолчанию, если настройки не переданы
        route_settings = {
            'routeType': 'simple',
            'considerCapacity': False,
            'considerFuel': False
        }
    # типы грузов
    for cargo in data['cargo_types']:
        if not cargo['name'] or not cargo['weight']:
            return False
        
    # типы машин
    if route_settings.get('considerCapacity', False):
        for truck in data['trucks']:
            if not truck['name'] or not truck['capacity']:
                return False
    
    # склады
    for warehouse in data['warehouses']:
        if not warehouse['name'] or not warehouse['address']:
            return False
        for cargo in warehouse['cargos']:
            if not cargo['type'] or not cargo['quantity']:
                return False
    
    # пункты приема
    for destination in data['destinations']:
        if not destination['name'] or not destination['address']:
            return False
        for cargo in destination['cargos']:
            if not cargo['type'] or not cargo['quantity']:
                return False
    
    return True


def validate_warehouse_quantities(warehouses, destinations):
    """Проверка наличия достаточного количества грузов на складах"""
    warehouse_cargos = {}
    destination_cargos = {}
    
    # Сначала собираем все грузы на складах
    for warehouse in warehouses:
        warehouse_name = warehouse['name']
        for cargo in warehouse['cargos']:
            key = (warehouse_name, cargo['type'])
            if key in warehouse_cargos:
                warehouse_cargos[key] += float(cargo['quantity'])
            else:
                warehouse_cargos[key] = float(cargo['quantity'])
    
    # Затем собираем все грузы в пунктах назначения
    for destination in destinations:
        for cargo in destination['cargos']:
            if cargo['type'] in destination_cargos:
                destination_cargos[cargo['type']] += float(cargo['quantity'])
            else:
                destination_cargos[cargo['type']] = float(cargo['quantity'])
    
    # Проверяем, что для каждого груза в пункте назначения есть достаточное количество на складах
    for dest_cargo, dest_cargo_quantity in destination_cargos.items():
        total_available = 0
        
        # Суммируем количество этого груза на всех складах
        for (wh_name, cargo_type), quantity in warehouse_cargos.items():
            if cargo_type == dest_cargo:
                total_available += quantity
        
        if float(dest_cargo_quantity) > total_available:
            return False
    
    return True


def validate_unique_names(data):
    """Проверка уникальности названий в пределах каждой формы"""
    # типы грузов
    cargo_names = [cargo['name'] for cargo in data['cargo_types']]
    if len(cargo_names) != len(set(cargo_names)):
        return False
    
    # склады
    warehouse_names = [warehouse['name'] for warehouse in data['warehouses']]
    if len(warehouse_names) != len(set(warehouse_names)):
        return False

    for warehouse in data['warehouses']:
        cargo_names_wh = [cargo['type'] for cargo in warehouse['cargos']]
        if len(cargo_names_wh) != len(set(cargo_names_wh)):
            return False
    
    # пункты приема
    destination_names = [destination['name'] for destination in data['destinations']]
    if len(destination_names) != len(set(destination_names)):
        return False

    for destination in data['destinations']:
        cargo_names_ds = [cargo['type'] for cargo in destination['cargos']]
        if len(cargo_names_ds) != len(set(cargo_names_ds)):
            return False
    
    return True


if __name__ == '__main__':
    app.run(debug=True, port=5000)