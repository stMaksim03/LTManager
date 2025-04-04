#include <iostream>
#include "BaseClasses/Product.cpp"
#include "BaseClasses/ProductContainer.cpp"

int main (int argc, char** argv)
{
    auto apple = new Product("apple", 0, 0.5);
    auto orange = new Product("orange", 8, 0.5);
    //std::cout << apple -> get_name();
    auto Storage = new ProductContainer();
    Storage->insert(apple, 5);
    Storage->insert("Orange", 5, 10, 110);
    //std::cout << (*apple < *orange) << std::endl;

    std::cout << Storage->get_by_id(0)->get_name() << std::endl;
    std::cout << Storage->get_by_id(5)->get_name() << std::endl;
    std::cout << Storage->get_by_id(3)->get_name() << std::endl;
    
    /*
    auto mapp = Storage -> get_storedProd();
    for (auto it = mapp -> begin(); it != mapp ->end(); it++)
    {
        std::cout << it -> first -> get_name() << " " << it -> first -> get_id() << "\n";
    }
    */
    getchar();
}