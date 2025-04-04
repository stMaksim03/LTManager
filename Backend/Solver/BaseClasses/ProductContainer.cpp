#include "ProductContainer.h"

ProductContainer::ProductContainer()
{
    defaultValues();
}

ProductContainer::ProductContainer(std::string name, int id, std::string address)
{
    defaultValues();
    this -> name = name;
    this -> id = id;
    this -> address = address;
}

void ProductContainer::defaultValues()
{
    this -> name = "Unnamed";
    this -> id = -1;
    this -> address = "No address";
    storedProd = new ProdMap();
    storedProd->emplace(new Product("Invalid ID", -2, 0), 0);
}

ProductContainer::~ProductContainer()
{

}

void ProductContainer::merge(const ProductContainer* ProductContainer)
{
    auto currSP = this -> storedProd;
    for (auto it = (ProductContainer -> storedProd) -> begin(); it != ProductContainer -> storedProd -> end(); it++)
    {
        auto prod = it -> first;
        if ((currSP -> find(prod) == currSP -> end()))
        {
            auto count = it -> second;
            currSP -> emplace(prod, count);
        }
        else if (currSP -> at(prod) != it -> second)
        {
            it -> second = std::max(it -> second, currSP -> at(prod));
        }
    }
    delete ProductContainer -> storedProd;
}

//Override
inline bool ProductContainer::operator<(ProductContainer& rhs){ return this -> id < rhs.id; }
inline bool ProductContainer::operator>(ProductContainer& rhs){ return rhs < *this; }
inline bool ProductContainer::operator<=(ProductContainer& rhs){ return !(*this > rhs);  }
inline bool ProductContainer::operator>=(ProductContainer& rhs){ return !(*this < rhs);  }
inline bool ProductContainer::operator==(ProductContainer& rhs)
{ 
    if (this -> name == rhs.name && this -> address == rhs.address)
    {
        if (this -> storedProd != rhs.storedProd) this -> merge(&rhs);
    }
    return false;
}
inline Product* ProductContainer::operator[](int id){ return get_by_id(id); }
//Setters
void ProductContainer::set_name(std::string name){ this -> name = name; }
void ProductContainer::set_id(int id){ this -> id = id; }
void ProductContainer::set_address(std::string address){ this -> address = address; }

void ProductContainer::insert(Product* ptr_product, int count){ storedProd -> emplace(ptr_product, count); }
void ProductContainer::insert(std::string name, int id, float weight, int count) {storedProd -> emplace (new Product(name, id, weight), count);}

//Getters
std::string ProductContainer::get_name() { return name; }
int ProductContainer::get_id() { return id; }
std::string ProductContainer::get_address() { return address; }

Product* ProductContainer::get_by_id(int id)
{
    auto output = storedProd -> begin();
    for (auto it = output; it != storedProd -> end(); it++)
    {
        if (it -> first -> get_id() == id) 
        {
            output = it;
            break;
        }
    }
    
    return output -> first;
}

ProductContainer::ProdMap* ProductContainer::get_storedProd(){ return storedProd; }
