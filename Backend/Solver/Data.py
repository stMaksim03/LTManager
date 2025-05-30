import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass

# Классы данных (соответствуют новым таблицам в БД)
@dataclass
class User:
    user_id: str
    username: str
    email: str
    is_active: bool

@dataclass
class Product:
    product_id: int
    user_id: str
    name: str
    weight: float
    aux_info: Dict

@dataclass
class Warehouse:
    warehouse_id: int
    user_id: str
    name: str
    address: str
    coordinates: Tuple[float, float]
    aux_info: Dict

@dataclass
class CollectionPoint:
    point_id: int
    user_id: str
    name: str
    address: str
    coordinates: Tuple[float, float]
    aux_info: Dict

@dataclass
class Inventory:
    inventory_id: int
    warehouse_id: int
    product_id: int
    quantity: int

@dataclass
class Route:
    route_id: int
    user_id: str
    warehouse_id: int
    point_id: int
    distance: float  # в м
    duration: float  # в с
    path_coordinates: List[Tuple[float, float]]  # список координат маршрута
    waypoints: List[Dict]

class DatabaseManager:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()
    
    # Методы для работы с пользователями (без изменений)
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING user_id, username, email, is_active;
        """
        self.cursor.execute(query, (username, email, password_hash))
        result = self.cursor.fetchone()
        return User(**result)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        query = "SELECT user_id, username, email, is_active FROM users WHERE username = %s;"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return User(**result) if result else None
    
    # Методы для работы с продуктами (без изменений)
    def add_product(self, user_id: str, name: str, weight: float, aux_info: Dict = None) -> Product:
        query = """
        INSERT INTO products (user_id, name, weight, aux_info)
        VALUES (%s, %s, %s, %s)
        RETURNING product_id, user_id, name, weight, aux_info;
        """
        self.cursor.execute(query, (user_id, name, weight, json.dumps(aux_info or {})))
        result = self.cursor.fetchone()
        return Product(**result)
    
    def get_products_by_user(self, user_id: str) -> List[Product]:
        query = "SELECT product_id, user_id, name, weight, aux_info FROM products WHERE user_id = %s;"
        self.cursor.execute(query, (user_id,))
        return [Product(**row) for row in self.cursor.fetchall()]
    
    # Методы для работы со складами (изменены под warehouses)
    def add_warehouse(self, user_id: str, name: str, address: str, lat: float, lon: float, aux_info: Dict = None) -> Warehouse:
        query = """
        INSERT INTO warehouses (user_id, name, address, coordinates, aux_info)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        RETURNING warehouse_id, user_id, name, address, 
                  ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, aux_info;
        """
        self.cursor.execute(query, (user_id, name, address, lon, lat, json.dumps(aux_info or {})))
        result = self.cursor.fetchone()
        return Warehouse(
            warehouse_id=result['warehouse_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info']
        )
    
    def get_warehouses_by_user(self, user_id: str) -> List[Warehouse]:
        query = """
        SELECT warehouse_id, user_id, name, address, 
               ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, aux_info
        FROM warehouses WHERE user_id = %s;
        """
        self.cursor.execute(query, (user_id,))
        return [
            Warehouse(
                warehouse_id=row['warehouse_id'],
                user_id=row['user_id'],
                name=row['name'],
                address=row['address'],
                coordinates=(row['lat'], row['lon']),
                aux_info=row['aux_info']
            ) for row in self.cursor.fetchall()
        ]
    
    # Методы для работы с пунктами сбора (новые)
    def add_collection_point(self, user_id: str, name: str, address: str, lat: float, lon: float, aux_info: Dict = None) -> CollectionPoint:
        query = """
        INSERT INTO collection_points (user_id, name, address, coordinates, aux_info)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        RETURNING point_id, user_id, name, address, 
                  ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, aux_info;
        """
        self.cursor.execute(query, (user_id, name, address, lon, lat, json.dumps(aux_info or {})))
        result = self.cursor.fetchone()
        return CollectionPoint(
            point_id=result['point_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info']
        )
    
    # Методы для работы с инвентарем (адаптированы под warehouses)
    def add_to_inventory(self, warehouse_id: int, product_id: int, quantity: int) -> Inventory:
        query = """
        INSERT INTO storage_inventory (warehouse_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (warehouse_id, product_id) 
        DO UPDATE SET quantity = storage_inventory.quantity + EXCLUDED.quantity
        RETURNING inventory_id, warehouse_id, product_id, quantity;
        """
        self.cursor.execute(query, (warehouse_id, product_id, quantity))
        result = self.cursor.fetchone()
        return Inventory(**result)
    
    def get_inventory_by_warehouse(self, warehouse_id: int) -> List[Dict]:
        query = """
        SELECT i.inventory_id, i.warehouse_id, i.product_id, i.quantity, p.name as product_name
        FROM storage_inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.warehouse_id = %s;
        """
        self.cursor.execute(query, (warehouse_id,))
        return self.cursor.fetchall()
    
    # Методы для работы с маршрутами (полностью переработаны)
    def add_route(self, user_id: str, warehouse_id: int, point_id: int, 
                 distance: float, duration: float, 
                 path_coords: List[Tuple[float, float]], waypoints: List[Dict] = None) -> Route:
        # Конвертируем координаты в PostGIS LineString
        line_string = "LINESTRING(" + ",".join([f"{lon} {lat}" for lat, lon in path_coords]) + ")"
        
        query = """
        INSERT INTO routes (user_id, warehouse_id, point_id, distance, duration, path_coordinates, waypoints)
        VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326), %s)
        RETURNING route_id, user_id, warehouse_id, point_id, distance, duration,
                  ST_AsText(path_coordinates) as path_text, waypoints;
        """
        self.cursor.execute(query, (
            user_id, warehouse_id, point_id, distance, duration, 
            line_string, json.dumps(waypoints or [])
        ))
        result = self.cursor.fetchone()
        
        # Парсим LineString обратно в список координат
        path_text = result['path_text'].replace('LINESTRING(', '').replace(')', '')
        path_coords = [(float(lat), float(lon)) for lon, lat in [c.split() for c in path_text.split(',')]]
        
        return Route(
            route_id=result['route_id'],
            user_id=result['user_id'],
            warehouse_id=result['warehouse_id'],
            point_id=result['point_id'],
            distance=result['distance'],
            duration=result['duration'],
            path_coordinates=path_coords,
            waypoints=result['waypoints']
        )
    
    def get_routes_by_user(self, user_id: str) -> List[Dict]:
        query = """
        SELECT r.route_id, r.user_id, r.distance, r.duration, 
               w.name as warehouse_name, p.name as point_name,
               ST_AsText(r.path_coordinates) as path_text, r.waypoints
        FROM routes r
        JOIN warehouses w ON r.warehouse_id = w.warehouse_id
        JOIN collection_points p ON r.point_id = p.point_id
        WHERE r.user_id = %s;
        """
        self.cursor.execute(query, (user_id,))
        routes = []
        for row in self.cursor.fetchall():
            # Парсим LineString для читаемого вывода
            path_text = row['path_text'].replace('LINESTRING(', '').replace(')', '')
            path_coords = [c.split() for c in path_text.split(',')]
            
            routes.append({
                'route_id': row['route_id'],
                'distance': row['distance'],
                'duration': row['duration'],
                'warehouse': row['warehouse_name'],
                'point': row['point_name'],
                'path_coords': path_coords,
                'waypoints': row['waypoints']
            })
        return routes

# Пример использования с новыми таблицами
if __name__ == "__main__":
    # Конфигурация подключения к БД!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    DB_CONFIG = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'raid',
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        with DatabaseManager(**DB_CONFIG) as db:
            # 1. Создаем пользователя
            user = db.create_user("geo_user", "geo@example.com", "secure_hash")
            print(f"Создан пользователь: {user.username} (ID: {user.user_id})")
            
            # 2. Добавляем продукты
            apple = db.add_product(user.user_id, "Яблоки", 0.2, {"type": "фрукты"})
            print(f"Добавлен продукт: {apple.name}")
            
            # 3. Создаем склад с координатами
            moscow_warehouse = db.add_warehouse(
                user.user_id, 
                "Московский склад", 
                "Москва, ул. Складская, 1", 
                55.751244, 37.618423
            )
            print(f"Создан склад: {moscow_warehouse.name} (координаты: {moscow_warehouse.coordinates})")
            
            # 4. Создаем пункт выдачи с координатами
            piter_point = db.add_collection_point(
                user.user_id, 
                "Пункт в Питере", 
                "Санкт-Петербург, Невский пр., 10", 
                59.934280, 30.335099
            )
            print(f"Создан пункт выдачи: {piter_point.name} (координаты: {piter_point.coordinates})")
            
            # 5. Добавляем товары на склад
            db.add_to_inventory(moscow_warehouse.warehouse_id, apple.product_id, 500)
            print("Товары добавлены на склад")
            
            # 6. Создаем маршрут с геоданными
            route_path = [
                (55.751244, 37.618423),  # Москва
                (56.326887, 38.128321),   # По пути
                (59.934280, 30.335099)    # СПб
            ]
            route = db.add_route(
                user.user_id,
                moscow_warehouse.warehouse_id,
                piter_point.point_id,
                distance=700000,  # в метрах
                duration=25200,   # 7 часов в секундах
                path_coords=route_path,
                waypoints=[{"name": "Остановка", "time": 3600}]
            )
            print(f"Создан маршрут: {moscow_warehouse.name} -> {piter_point.name}")
            
            # 7. Получаем и выводим данные
            print("\nСклады пользователя:")
            for warehouse in db.get_warehouses_by_user(user.user_id):
                print(f"- {warehouse.name}: {warehouse.coordinates}")
                
                print("  Товары на складе:")
                for item in db.get_inventory_by_warehouse(warehouse.warehouse_id):
                    print(f"  - {item['product_name']}: {item['quantity']} шт")
            
            print("\nМаршруты пользователя:")
            for route in db.get_routes_by_user(user.user_id):
                print(f"- {route['warehouse']} -> {route['point']}: {route['distance']/1000:.1f} км")
                print(f"  Путь через {len(route['path_coords'])} точек")
                
    except Exception as e:
        print(f"Ошибка: {e}")