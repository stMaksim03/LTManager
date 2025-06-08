import pandas as pd
#pip install pandas openpyxl
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Product:
    sku: str
    name: str
    weight: float
    features: str

@dataclass
class Warehouse:
    id: str
    name: str
    address: str
    metadata: dict

@dataclass
class InventoryItem:
    warehouse_id: str
    product_sku: str
    quantity: int

@dataclass
class Destination:
    id: str
    name: str
    address: str
    product_sku: str
    required_quantity: int

@dataclass
class Transport:
    id: str
    name: str
    max_load: float
    fuel_consumption: float

class TransportTaskData:
    def __init__(self):
        self.products: List[Product] = []
        self.warehouses: List[Warehouse] = []
        self.inventory: List[InventoryItem] = []
        self.destinations: List[Destination] = []
        self.transports: List[Transport] = []
    
    def load_from_excel(self, file_path: str):
        """Загружает данные из Excel файла"""
        
        # Загрузка листов
        products_df = pd.read_excel(file_path, sheet_name='Товары')
        warehouses_df = pd.read_excel(file_path, sheet_name='Склады')
        inventory_df = pd.read_excel(file_path, sheet_name='Товары на складах')
        destinations_df = pd.read_excel(file_path, sheet_name='ПП')
        transport_df = pd.read_excel(file_path, sheet_name='ТС')
        
        for _, row in products_df.iterrows():
            self.products.append(
                Product(
                    sku=str(row['SKU']),
                    name=row['Название'],
                    weight=float(row['Вес (кг)']),
                    features=row.get('Особенности', '')
                )
            )
        
        for _, row in warehouses_df.iterrows():
            self.warehouses.append(
                Warehouse(
                    id=row['ID'],
                    name=row['Название'],
                    address=row['Адрес'],
                    metadata=eval(row.get('Доп. информация', '{}'))
                )
            )
        
        for _, row in inventory_df.iterrows():
            self.inventory.append(
                InventoryItem(
                    warehouse_id=row['Склад ID'],
                    product_sku=str(row['SKU товара']),
                    quantity=int(row['Количество'])
                )
            )
        
        for _, row in destinations_df.iterrows():
            self.destinations.append(
                Destination(
                    id=row['ID'],
                    name=row['Название'],
                    address=row['Адрес'],
                    product_sku=str(row['SKU товара']),
                    required_quantity=float(row['Требуемое кол-во'])
                )
            )
        
        for _, row in transport_df.iterrows():
            self.transports.append(
                Transport(
                    id=row['ID'],
                    name=row['Название'],
                    max_load=float(row['Грузоподъемность (кг)']),
                    fuel_consumption=float(row['Расход топлива (л/100км)'])
                )
            )
    
    def get_warehouse_by_id(self, warehouse_id: str) -> Optional[Warehouse]:
        """Находит склад по ID"""
        return next((w for w in self.warehouses if w.id == warehouse_id), None)
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Находит товар по SKU"""
        return next((p for p in self.products if p.sku == sku), None)
    
    def get_inventory_for_warehouse(self, warehouse_id: str) -> List[InventoryItem]:
        """Возвращает инвентарь для указанного склада"""
        return [item for item in self.inventory if item.warehouse_id == warehouse_id]
    
    def get_destinations_for_product(self, product_sku: str) -> List[Destination]:
        """Возвращает пункты назначения для указанного товара"""
        return [d for d in self.destinations if d.product_sku == product_sku]
    
    def validate_data(self) -> bool:
        """Проверяет целостность данных"""
        for item in self.inventory:
            if not self.get_warehouse_by_id(item.warehouse_id):
                print(f"Ошибка: склад {item.warehouse_id} не найден для товара {item.product_sku}")
                return False
        
        for item in self.inventory:
            if not self.get_product_by_sku(item.product_sku):
                print(f"Ошибка: товар {item.product_sku} не найден на складе {item.warehouse_id}")
                return False
        
        return True

# Пример использования
if __name__ == "__main__":
    data = TransportTaskData()
    data.load_from_excel("C:/Users/Владимир/Desktop/Матрица.xlsx")
    if data.validate_data():
        print("Данные загружены успешно!")
        print(f"Загружено: {len(data.products)} товаров, {len(data.warehouses)} складов")
        
        warehouse = data.warehouses[0]
        print(f"\nИнвентарь на складе {warehouse.name}:")
        for item in data.get_inventory_for_warehouse(warehouse.id):
            product = data.get_product_by_sku(item.product_sku)
            print(f"- {product.name}: {item.quantity} шт.")
    else:
        print("Обнаружены ошибки в данных!")