#include <iostream>
#include "BaseClasses/Product.cpp"

int main (int argc, char** argv)
{
    auto apple = new Product("apple", 0, 0.5);
    std::cout << apple -> get_name();
    getchar();
}