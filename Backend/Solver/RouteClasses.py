from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from . import BaseClasses as bc


@dataclass
class Route:
    id: int = -1
    length: int = -1
    storage_ptr: Optional[bc.ProductStorage] = None
    receiver_ptr: Optional[bc.ProductStorage] = None
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
    def __init__(self, product : bc.Product):
        self.storages: list[bc.ProductStorage] = []
        self.receivers: list[bc.ProductStorage] = []
        self.routes: Dict[Tuple[bc.ProductStorage, bc.ProductStorage], Route] = {}
        self.aux_info: Dict[str, str] = {}
        self.product: bc.Product = product

    def add_storage(self, storage: bc.ProductStorage):
        if storage not in self.storages:
            self.storages.append(storage)

    def add_receiver(self, receiver: bc.ProductStorage):
        if receiver not in self.receivers:
            self.receivers.append(receiver)

    def set_at(self, storage: bc.ProductStorage, receiver: bc.ProductStorage, route: Route):
        self.add_storage(storage)
        self.add_receiver(receiver)
        self.routes[(storage, receiver)] = route

    def get_at(self, storage: bc.ProductStorage, receiver: bc.ProductStorage) -> Route:
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

    def get_storage_vector(self) -> list[bc.ProductStorage]:
        return self.storages

    def get_receiver_vector(self) -> list[bc.ProductStorage]:
        return self.receivers
