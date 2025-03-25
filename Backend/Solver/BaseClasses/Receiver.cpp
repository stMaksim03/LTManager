#include "Receiver.h"

Receiver::Receiver()
{
    this -> name = "Unnamed";
    this -> id = -1;
    this -> address = "No address";
}

Receiver::Receiver(std::string name, int id, std::string address)
{
    this -> name = name;
    this -> id = id;
    this -> address = address;
}

Receiver::~Receiver()
{

}

void Receiver::merge(const Receiver* Receiver)
{
    auto currSP = this -> requestedProd;
    for (auto it = (Receiver -> requestedProd) -> begin(); it != Receiver -> requestedProd -> end(); it++)
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
    delete Receiver -> requestedProd;
}

//Override
inline bool Receiver::operator<(const Receiver& rhs){ return this -> id < rhs.id; }
inline bool Receiver::operator>(const Receiver& rhs){ return *this < rhs; }
inline bool Receiver::operator<=(const Receiver& rhs){ return !(*this > rhs);  }
inline bool Receiver::operator>=(const Receiver& rhs){ return !(*this < rhs);  }
inline bool Receiver::operator==(const Receiver& rhs)
{ 
    if (this -> name == rhs.name && this -> address == rhs.address)
    {
        if (this -> requestedProd != rhs.requestedProd) this -> merge(&rhs);
    }
    return false;
}
inline Product& Receiver::operator[](int id){ return *get_by_id(id); }
//Setters
void Receiver::set_name(std::string name){ this -> name = name; }
void Receiver::set_id(int id){ this -> id = id; }
void Receiver::set_address(std::string address){ this -> address = address; }

void Receiver::insert(Product* ptr_product, int count){ requestedProd -> emplace(ptr_product, count); }
void Receiver::insert(std::string name, int id, float weight, int count) {requestedProd -> emplace (new Product(name, id, weight), count);}

//Getters
std::string Receiver::get_name() { return name; }
int Receiver::get_id() { return id; }
std::string Receiver::get_address() { return address; }

Product* Receiver::get_by_id(int id)
{
    auto it = requestedProd -> begin();
    for (it; it != requestedProd -> end(); it++)
    {
        if (it -> first -> get_id() == id) break;
    }
    
    return it -> first;
}

Receiver::ProdMap* Receiver::get_requestedProd(){ return requestedProd; }
