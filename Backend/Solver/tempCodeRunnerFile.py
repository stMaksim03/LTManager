
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из DB.env

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Data classes for all tables
@dataclass
class User:
    user_id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

@dataclass
class Product:
    product_id: int
    user_id: str
    name: str
    weight: float
    aux_info: Dict
    created_at: datetime
    updated_at: datetime

@dataclass
class Transport:
    transport_id: int
    user_id: str
    name: str
    weight_lift: float
    aux_info: Dict
    created_at: datetime
    updated_at: datetime

@dataclass
class Warehouse:
    warehouse_id: int
    user_id: str
    name: str
    address: str
    coordinates: Tuple[float, float]
    aux_info: Dict
    created_at: datetime
    updated_at: datetime

@dataclass
class CollectionPoint:
    point_id: int
    user_id: str
    name: str
    address: str
    coordinates: Tuple[float, float]
    aux_info: Dict
    created_at: datetime
    updated_at: datetime

@dataclass
class Inventory:
    inventory_id: int
    warehouse_id: int
    product_id: int
    quantity: int
    last_updated: datetime

@dataclass
class Route:
    route_id: int
    user_id: str
    warehouse_id: int
    point_id: int
    distance: float
    duration: float
    path_coordinates: List[Tuple[float, float]]
    waypoints: List[Dict]
    created_at: datetime
    updated_at: datetime

@dataclass
class RouteMatrix:
    matrix_id: int
    user_id: str
    name: str
    description: Optional[str]
    aux_info: Dict
    created_at: datetime

@dataclass
class MatrixEntry:
    entry_id: int
    matrix_id: int
    route_id: int
    warehouse_id: int
    point_id: int
    created_at: datetime

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
    
    # Helper methods
    def _execute_and_fetchone(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()
    
    def _execute_and_fetchall(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()
    
    # User CRUD methods
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING user_id, username, email, password_hash, created_at, last_login, is_active;
        """
        result = self._execute_and_fetchone(query, (username, email, password_hash))
        return User(**result)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        query = """
        SELECT user_id, username, email, password_hash, created_at, last_login, is_active
        FROM users WHERE user_id = %s;
        """
        result = self._execute_and_fetchone(query, (user_id,))
        return User(**result) if result else None
    
    def delete_user(self, user_id: str) -> bool:
        query = "DELETE FROM users WHERE user_id = %s;"
        self.cursor.execute(query, (user_id,))
        return self.cursor.rowcount > 0
    
    # Product CRUD methods
    def create_product(self, user_id: str, name: str, weight: float, aux_info: Dict = None) -> Product:
        query = """
        INSERT INTO products (user_id, name, weight, aux_info)
        VALUES (%s, %s, %s, %s)
        RETURNING product_id, user_id, name, weight, aux_info, created_at, updated_at;
        """
        result = self._execute_and_fetchone(query, (user_id, name, weight, json.dumps(aux_info or {})))
        return Product(**result)
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        query = """
        SELECT product_id, user_id, name, weight, aux_info, created_at, updated_at
        FROM products WHERE product_id = %s;
        """
        result = self._execute_and_fetchone(query, (product_id,))
        return Product(**result) if result else None
    
    def delete_product(self, product_id: int) -> bool:
        query = "DELETE FROM products WHERE product_id = %s;"
        self.cursor.execute(query, (product_id,))
        return self.cursor.rowcount > 0
    
    # Transport CRUD methods
    def create_transport(self, user_id: str, name: str, weight_lift: float, aux_info: Dict = None) -> Transport:
        query = """
        INSERT INTO transport (user_id, name, weight_lift, aux_info)
        VALUES (%s, %s, %s, %s)
        RETURNING transport_id, user_id, name, weight_lift, aux_info, created_at, updated_at;
        """
        result = self._execute_and_fetchone(query, (user_id, name, weight_lift, json.dumps(aux_info or {})))
        return Transport(**result)
    
    def get_transport_by_id(self, transport_id: int) -> Optional[Transport]:
        query = """
        SELECT transport_id, user_id, name, weight_lift, aux_info, created_at, updated_at
        FROM transport WHERE transport_id = %s;
        """
        result = self._execute_and_fetchone(query, (transport_id,))
        return Transport(**result) if result else None
    
    def delete_transport(self, transport_id: int) -> bool:
        query = "DELETE FROM transport WHERE transport_id = %s;"
        self.cursor.execute(query, (transport_id,))
        return self.cursor.rowcount > 0
    
    # Warehouse CRUD methods
    def create_warehouse(self, user_id: str, name: str, address: str, lat: float, lon: float, aux_info: Dict = None) -> Warehouse:
        query = """
        INSERT INTO warehouses (user_id, name, address, coordinates, aux_info)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        RETURNING warehouse_id, user_id, name, address, 
                  ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, 
                  aux_info, created_at, updated_at;
        """
        result = self._execute_and_fetchone(query, (user_id, name, address, lon, lat, json.dumps(aux_info or {})))
        return Warehouse(
            warehouse_id=result['warehouse_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def get_warehouse_by_id(self, warehouse_id: int) -> Optional[Warehouse]:
        query = """
        SELECT warehouse_id, user_id, name, address, 
               ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, 
               aux_info, created_at, updated_at
        FROM warehouses WHERE warehouse_id = %s;
        """
        result = self._execute_and_fetchone(query, (warehouse_id,))
        if not result:
            return None
        return Warehouse(
            warehouse_id=result['warehouse_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def delete_warehouse(self, warehouse_id: int) -> bool:
        query = "DELETE FROM warehouses WHERE warehouse_id = %s;"
        self.cursor.execute(query, (warehouse_id,))
        return self.cursor.rowcount > 0
    
    # Collection Point CRUD methods
    def create_collection_point(self, user_id: str, name: str, address: str, lat: float, lon: float, aux_info: Dict = None) -> CollectionPoint:
        query = """
        INSERT INTO collection_points (user_id, name, address, coordinates, aux_info)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        RETURNING point_id, user_id, name, address, 
                  ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, 
                  aux_info, created_at, updated_at;
        """
        result = self._execute_and_fetchone(query, (user_id, name, address, lon, lat, json.dumps(aux_info or {})))
        return CollectionPoint(
            point_id=result['point_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def get_collection_point_by_id(self, point_id: int) -> Optional[CollectionPoint]:
        query = """
        SELECT point_id, user_id, name, address, 
               ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon, 
               aux_info, created_at, updated_at
        FROM collection_points WHERE point_id = %s;
        """
        result = self._execute_and_fetchone(query, (point_id,))
        if not result:
            return None
        return CollectionPoint(
            point_id=result['point_id'],
            user_id=result['user_id'],
            name=result['name'],
            address=result['address'],
            coordinates=(result['lat'], result['lon']),
            aux_info=result['aux_info'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def delete_collection_point(self, point_id: int) -> bool:
        query = "DELETE FROM collection_points WHERE point_id = %s;"
        self.cursor.execute(query, (point_id,))
        return self.cursor.rowcount > 0
    
    # Inventory CRUD methods
    def create_inventory(self, warehouse_id: int, product_id: int, quantity: int) -> Inventory:
        query = """
        INSERT INTO storage_inventory (warehouse_id, product_id, quantity)
        VALUES (%s, %s, %s)
        RETURNING inventory_id, warehouse_id, product_id, quantity, last_updated;
        """
        result = self._execute_and_fetchone(query, (warehouse_id, product_id, quantity))
        return Inventory(**result)
    
    def get_inventory_by_id(self, inventory_id: int) -> Optional[Inventory]:
        query = """
        SELECT inventory_id, warehouse_id, product_id, quantity, last_updated
        FROM storage_inventory WHERE inventory_id = %s;
        """
        result = self._execute_and_fetchone(query, (inventory_id,))
        return Inventory(**result) if result else None
    
    def delete_inventory(self, inventory_id: int) -> bool:
        query = "DELETE FROM storage_inventory WHERE inventory_id = %s;"
        self.cursor.execute(query, (inventory_id,))
        return self.cursor.rowcount > 0
    
    # Route CRUD methods
    def create_route(self, user_id: str, warehouse_id: int, point_id: int, 
                    distance: float, duration: float, 
                    path_coords: List[Tuple[float, float]], waypoints: List[Dict] = None) -> Route:
        # Convert coordinates to PostGIS LineString
        line_string = "LINESTRING(" + ",".join([f"{lon} {lat}" for lat, lon in path_coords]) + ")"
        
        query = """
        INSERT INTO routes (user_id, warehouse_id, point_id, distance, duration, path_coordinates, waypoints)
        VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326), %s)
        RETURNING route_id, user_id, warehouse_id, point_id, distance, duration,
                  ST_AsText(path_coordinates) as path_text, waypoints, created_at, updated_at;
        """
        result = self._execute_and_fetchone(query, (
            user_id, warehouse_id, point_id, distance, duration, 
            line_string, json.dumps(waypoints or [])))
        
        # Parse LineString back to coordinates list
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
            waypoints=result['waypoints'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def get_route_by_id(self, route_id: int) -> Optional[Route]:
        query = """
        SELECT route_id, user_id, warehouse_id, point_id, distance, duration,
               ST_AsText(path_coordinates) as path_text, waypoints, created_at, updated_at
        FROM routes WHERE route_id = %s;
        """
        result = self._execute_and_fetchone(query, (route_id,))
        if not result:
            return None
        
        # Parse LineString
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
            waypoints=result['waypoints'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def delete_route(self, route_id: int) -> bool:
        query = "DELETE FROM routes WHERE route_id = %s;"
        self.cursor.execute(query, (route_id,))
        return self.cursor.rowcount > 0
    
    # Route Matrix CRUD methods
    def create_route_matrix(self, user_id: str, name: str, description: str = None, aux_info: Dict = None) -> RouteMatrix:
        query = """
        INSERT INTO route_matrices (user_id, name, description, aux_info)
        VALUES (%s, %s, %s, %s)
        RETURNING matrix_id, user_id, name, description, aux_info, created_at;
        """
        result = self._execute_and_fetchone(query, (user_id, name, description, json.dumps(aux_info or {})))
        return RouteMatrix(**result)
    
    def get_route_matrix_by_id(self, matrix_id: int) -> Optional[RouteMatrix]:
        query = """
        SELECT matrix_id, user_id, name, description, aux_info, created_at
        FROM route_matrices WHERE matrix_id = %s;
        """
        result = self._execute_and_fetchone(query, (matrix_id,))
        return RouteMatrix(**result) if result else None
    
    def delete_route_matrix(self, matrix_id: int) -> bool:
        query = "DELETE FROM route_matrices WHERE matrix_id = %s;"
        self.cursor.execute(query, (matrix_id,))
        return self.cursor.rowcount > 0
    
    # Matrix Entry CRUD methods
    def create_matrix_entry(self, matrix_id: int, route_id: int, warehouse_id: int, point_id: int) -> MatrixEntry:
        query = """
        INSERT INTO matrix_entries (matrix_id, route_id, warehouse_id, point_id)
        VALUES (%s, %s, %s, %s)
        RETURNING entry_id, matrix_id, route_id, warehouse_id, point_id, created_at;
        """
        result = self._execute_and_fetchone(query, (matrix_id, route_id, warehouse_id, point_id))
        return MatrixEntry(**result)
    
    def get_matrix_entry_by_id(self, entry_id: int) -> Optional[MatrixEntry]:
        query = """
        SELECT entry_id, matrix_id, route_id, warehouse_id, point_id, created_at
        FROM matrix_entries WHERE entry_id = %s;
        """
        result = self._execute_and_fetchone(query, (entry_id,))
        return MatrixEntry(**result) if result else None
    
    def delete_matrix_entry(self, entry_id: int) -> bool:
        query = "DELETE FROM matrix_entries WHERE entry_id = %s;"
        self.cursor.execute(query, (entry_id,))
        return self.cursor.rowcount > 0
    
    # Context manager methods
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()
        
        
# Пример создания и работы с транспортом
with DatabaseManager(**DB_CONFIG) as db:
    # Создаем транспорт
    truck = db.create_transport(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        name="Грузовик",
        weight_lift=5000.0,
        aux_info={"type": "грузовой", "fuel": "дизель"}
    )
    print(f"Создан транспорт: {truck.name} (ID: {truck.transport_id})")
    
    # Получаем транспорт по ID
    same_truck = db.get_transport_by_id(truck.transport_id)
    print(f"Получен транспорт: {same_truck.name}, грузоподъемность: {same_truck.weight_lift}кг")
    
    # Удаляем транспорт
    if db.delete_transport(truck.transport_id):
        print(f"Транспорт ID {truck.transport_id} удален")