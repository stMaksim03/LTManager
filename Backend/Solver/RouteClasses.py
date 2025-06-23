from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from Backend.Solver.BaseClasses import ProductStorage, Product


@dataclass
class Route:
    id: int = -1
    length: int = -1
    storage_ptr: Optional[ProductStorage] = None
    receiver_ptr: Optional[ProductStorage] = None
    raw_data: Dict[str, str] = field(default_factory=dict)

    def __lt__(self, other: 'Route') -> bool:
        return self.id < other.id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return NotImplemented
        return self.storage_ptr == other.storage_ptr and self.receiver_ptr == other.receiver_ptr
    
    def __hash__(self):
        return hash((self.storage_ptr, self.receiver_ptr))

    def __le__(self, other: 'Route') -> bool:
        return self < other or self == other

    def __gt__(self, other: 'Route') -> bool:
        return not self <= other

    def __ge__(self, other: 'Route') -> bool:
        return not self < other
    
    def get_ptrs(self):
        return (self.storage_ptr, self.receiver_ptr)


class RouteMatrix:
    def __init__(self, product : Product):
        self.storages: list[ProductStorage] = []
        self.receivers: list[ProductStorage] = []
        self.routes: Dict[Tuple[ProductStorage, ProductStorage], Route] = {}
        self.aux_info: Dict[str, str] = {}
        self.product: Product = product

    def add_storage(self, storage: ProductStorage):
        if storage not in self.storages:
            self.storages.append(storage)

    def add_receiver(self, receiver: ProductStorage):
        if receiver not in self.receivers:
            self.receivers.append(receiver)

    def set_at(self, storage: ProductStorage, receiver: ProductStorage, route: Route):
        self.add_storage(storage)
        self.add_receiver(receiver)
        self.routes[(storage, receiver)] = route

    def get_at(self, storage: ProductStorage, receiver: ProductStorage) -> Route:
        return self.routes.get((storage, receiver), Route())

    def get_by_indices(self, storage_index: int, receiver_index: int) -> Route:
        try:
            storage = self.storages[storage_index]
            receiver = self.receivers[receiver_index]
            return self.get_at(storage, receiver)
        except IndexError:
            return Route()

    @property
    def lines(self) -> int:
        return len(self.storages)

    @property
    def columns(self) -> int:
        return len(self.receivers)

    def get_storage_vector(self) -> list[ProductStorage]:
        return self.storages

    def get_receiver_vector(self) -> list[ProductStorage]:
        return self.receivers
