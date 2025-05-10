import RouteClasses as rc
import BaseClasses as bc



def main():
    a = bc.ProductStorage("zavod", 0)
    a.insert(bc.Product(0, "apple", 2), 2)
    a.insert(bc.Product(1, "orange", 0.5), 6)
    a.insert(bc.Product(2, "lemon", 2.5), 10)
    a.insert(bc.Product(3, "bomb", 20), 100)
    for product, count in a:
        print(f"{product.id} {product.name} {product.weight} {count}")
    a = rc.Route()
    
    return 0

main()
