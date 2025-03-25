#include "Storage.h"

Storage::Storage()
{
    this -> name = "Unnamed";
    this -> id = -1;
    this -> address = "No address";
}

Storage::Storage(std::string name, int id, std::string address)
{
    this -> name = name;
    this -> id = id;
    this -> address = address;
}

Storage::~Storage()
{

}

void Storage::merge(const Storage* storage)
{
    auto currSP = this -> storedProd;
    for (auto it = (storage -> storedProd) -> begin(); it != storage -> storedProd -> end(); it++)
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
    delete storage -> storedProd;
}

//Override
inline bool Storage::operator<(const Storage& rhs){ return this -> id < rhs.id; }
inline bool Storage::operator>(const Storage& rhs){ return *this < rhs; }
inline bool Storage::operator<=(const Storage& rhs){ return !(*this > rhs);  }
inline bool Storage::operator>=(const Storage& rhs){ return !(*this < rhs);  }
inline bool Storage::operator==(const Storage& rhs)
{ 
    if (this -> name == rhs.name && this -> address == rhs.address)
    {
        if (this -> storedProd != rhs.storedProd) this -> merge(&rhs);
    }
    return false;
}
inline Product& Storage::operator[](int id){ return *get_by_id(id); }
//Setters
void Storage::set_name(std::string name){ this -> name = name; }
void Storage::set_id(int id){ this -> id = id; }
void Storage::set_address(std::string address){ this -> address = address; }

void Storage::insert(Product* ptr_product, int count){ storedProd -> emplace(ptr_product, count); }
void Storage::insert(std::string name, int id, float weight, int count) {storedProd -> emplace (new Product(name, id, weight), count);}

//Getters
std::string Storage::get_name() { return name; }
int Storage::get_id() { return id; }
std::string Storage::get_address() { return address; }

Product* Storage::get_by_id(int id)
{
    auto it = storedProd -> begin();
    for (it; it != storedProd -> end(); it++)
    {
        if (it -> first -> get_id() == id) break;
    }
    
    return it -> first;
}

Storage::ProdMap* Storage::get_storedProd(){ return storedProd; }
