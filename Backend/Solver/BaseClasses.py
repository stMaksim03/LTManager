from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional


@dataclass(order=True, frozen=True)
class Product:
    id: int = -1
    name: str = field(default="Unnamed", compare=False)
    weight: float = -1.0
    aux_info: Dict[str, str] = field(default_factory=dict, compare=False)

    def __eq__(self, other):
        return (
            isinstance(other, Product)
            and self.name == other.name
            and self.weight == other.weight
        )


@dataclass(order=True, frozen=True)
class Transport:
    id: int = -1
    name: str = field(default="Unnamed", compare=False)
    fuel_cost: float = 1.0
    weight_lift: float = -1.0
    aux_info: Dict[str, str] = field(default_factory=dict, compare=False)

    def __eq__(self, other):
        return (
            isinstance(other, Transport)
            and self.name == other.name
            and self.weight_lift == other.weight_lift
        )


class ProductStorage:
    def __init__(self, name="Unnamed", id=-1, address="No address"):
        self.name = name
        self.id = id
        self.address = address
        self._stored_products: Dict[Product, int] = {}
        self.aux_info: Dict[str, str] = {}

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        if not isinstance(other, ProductStorage):
            return NotImplemented
        if self.name == other.name and self.address == other.address:
            return True
        return False
    
    def __hash__(self):
        return hash((self.name, self.address))

    def __getitem__(self, product_id: int) -> Optional[Product]:
        return next((p for p in self._stored_products if p.id == product_id), None)
    
    def __iter__(self):
        return iter(self.stored_products.items())

    def insert(self, product: Product, count: int):
        self._stored_products[product] = count

    def insert_raw(self, name: str, id: int, weight: float, count: int):
        self.insert(Product(name=name, id=id, weight=weight), count)

    def merge(self, other: "ProductStorage"):
        for product, count in other._stored_products.items():
            self._stored_products[product] = max(
                self._stored_products.get(product, 0), count
            )

    def get_pair_by_id(self, product_id: int) -> Optional[Tuple[Product, int]]:
        return next(
            ((product, count) for product, count in self._stored_products.items()
             if product.id == product_id),
            None
        )

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        pair = self.get_pair_by_id(product_id)
        return pair[0] if pair else None

    def get_count_by_id(self, product_id: int) -> int:
        pair = self.get_pair_by_id(product_id)
        return pair[1] if pair else 0

    @property
    def size(self) -> int:
        return len(self._stored_products)

    @property
    def stored_products(self) -> Dict[Product, int]:
        return self._stored_products
