import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import List, Dict, Optional
import json
from dataclasses import dataclass

# Классы данных (соответствуют таблицам в БД)
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
class Storage:
    storage_id: int
    user_id: str
    name: str
    address: str
    aux_info: Dict

@dataclass
class Inventory:
    inventory_id: int
    storage_id: int
    product_id: int
    quantity: int

@dataclass
class Route:
    route_id: int
    user_id: str
    storage_from_id: int
    storage_to_id: int
    length: float
    input_data: Dict

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
    
    # Методы для работы с пользователями
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
    
    def authenticate_user(self, email: str, password_hash: str) -> Optional[User]:
        query = """
        SELECT user_id, username, email, is_active 
        FROM users 
        WHERE email = %s AND password_hash = %s;
        """
        self.cursor.execute(query, (email, password_hash))
        result = self.cursor.fetchone()
        return User(**result) if result else None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        query = """
        SELECT user_id, username, email, is_active 
        FROM users 
        WHERE user_id = %s;
        """
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return User(**result) if result else None
    
    # Методы для работы с продуктами
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
    
    # Методы для работы со складами
    def add_storage(self, user_id: str, name: str, address: str, aux_info: Dict = None) -> Storage:
        query = """
        INSERT INTO product_storages (user_id, name, address, aux_info)
        VALUES (%s, %s, %s, %s)
        RETURNING storage_id, user_id, name, address, aux_info;
        """
        self.cursor.execute(query, (user_id, name, address, json.dumps(aux_info or {})))
        result = self.cursor.fetchone()
        return Storage(**result)
    
    def get_storages_by_user(self, user_id: str) -> List[Storage]:
        query = "SELECT storage_id, user_id, name, address, aux_info FROM product_storages WHERE user_id = %s;"
        self.cursor.execute(query, (user_id,))
        return [Storage(**row) for row in self.cursor.fetchall()]
    
    # Методы для работы с инвентарем
    def add_to_inventory(self, storage_id: int, product_id: int, quantity: int) -> Inventory:
        query = """
        INSERT INTO storage_inventory (storage_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (storage_id, product_id) 
        DO UPDATE SET quantity = storage_inventory.quantity + EXCLUDED.quantity
        RETURNING inventory_id, storage_id, product_id, quantity;
        """
        self.cursor.execute(query, (storage_id, product_id, quantity))
        result = self.cursor.fetchone()
        return Inventory(**result)
    
    def get_inventory_by_storage(self, storage_id: int) -> List[Inventory]:
        query = """
        SELECT i.inventory_id, i.storage_id, i.product_id, i.quantity, p.name as product_name
        FROM storage_inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.storage_id = %s;
        """
        self.cursor.execute(query, (storage_id,))
        return self.cursor.fetchall()  # Возвращаем словари для удобства
    
    # Методы для работы с маршрутами
    def add_route(self, user_id: str, storage_from_id: int, storage_to_id: int, length: float, input_data: Dict = None) -> Route:
        query = """
        INSERT INTO routes (user_id, storage_from_id, storage_to_id, length, input_data)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING route_id, user_id, storage_from_id, storage_to_id, length, input_data;
        """
        self.cursor.execute(query, (user_id, storage_from_id, storage_to_id, length, json.dumps(input_data or {})))
        result = self.cursor.fetchone()
        return Route(**result)
    
    def get_routes_by_user(self, user_id: str) -> List[Route]:
        query = """
        SELECT r.route_id, r.user_id, r.storage_from_id, r.storage_to_id, r.length, r.input_data,
               sf.name as from_name, st.name as to_name
        FROM routes r
        JOIN product_storages sf ON r.storage_from_id = sf.storage_id
        JOIN product_storages st ON r.storage_to_id = st.storage_id
        WHERE r.user_id = %s;
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()  # Возвращаем словари для удобства

# Пример использования
if __name__ == "__main__":
    # Конфигурация подключения к БД
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
            user = db.create_user("test_user", "test@example.com", "hashed_password")
            print(f"Создан пользователь: {user.username} (ID: {user.user_id})")
            
            # 2. Добавляем продукты
            apple = db.add_product(user.user_id, "Яблоки", 0.2, {"color": "red"})
            banana = db.add_product(user.user_id, "Бананы", 0.3, {"color": "yellow"})
            print(f"Добавлены продукты: {apple.name}, {banana.name}")
            
            # 3. Создаем склады
            moscow = db.add_storage(user.user_id, "Московский склад", "Москва")
            piter = db.add_storage(user.user_id, "Питерский склад", "Санкт-Петербург")
            print(f"Созданы склады: {moscow.name}, {piter.name}")
            
            # 4. Добавляем товары на склад
            db.add_to_inventory(moscow.storage_id, apple.product_id, 1000)
            db.add_to_inventory(moscow.storage_id, banana.product_id, 500)
            db.add_to_inventory(piter.storage_id, apple.product_id, 800)
            print("Товары добавлены на склады")
            
            # 5. Создаем маршрут
            route = db.add_route(
                user.user_id, 
                moscow.storage_id, 
                piter.storage_id, 
                700.0, 
                {"time_hours": 10.5, "cost": 15000}
            )
            print(f"Создан маршрут: Москва -> Питер ({route.length} км)")
            
            # 6. Получаем и выводим данные
            print("\nСписок складов пользователя:")
            for storage in db.get_storages_by_user(user.user_id):
                print(f"- {storage.name} ({storage.address})")
                
                print("  Товары на складе:")
                for item in db.get_inventory_by_storage(storage.storage_id):
                    print(f"  - {item['product_name']}: {item['quantity']} шт")
            
            print("\nМаршруты пользователя:")
            for route in db.get_routes_by_user(user.user_id):
                print(f"- {route['from_name']} -> {route['to_name']}: {route['length']} км")
                
    except Exception as e:
        print(f"Ошибка: {e}")