#include "Product.h"

Product::Product()
{
    this -> name = "Unnamed";
    this -> id = -1;
    this -> weight = -1.0;
}

Product::Product(std::string name, int id, float weight)
{
    this -> name = name;
    this -> id = id;
    this -> weight = weight;
}

Product::~Product()
{

}

//Override
inline bool Product::operator<(Product& rhs){ return this -> id < rhs.id; }
inline bool Product::operator>(Product& rhs){ return rhs < *this; }
inline bool Product::operator<=(Product& rhs){ return !(*this > rhs);  }
inline bool Product::operator>=(Product& rhs){ return !(*this < rhs);  }
inline bool Product::operator==(Product& rhs){ return this -> name == rhs.name && this -> weight == rhs.weight; }

//Setters
void Product::set_name(std::string name){ this -> name = name; }
void Product::set_id(int id){ this -> id = id; }
void Product::set_weight(float weight){ this -> weight = weight; }

//Getters
std::string Product::get_name() { return name; }
int Product::get_id() { return id; }
float Product::get_weight() { return weight; }
