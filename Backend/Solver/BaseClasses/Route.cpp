#include "Route.h"

Route::Route()
{
    this -> id = -1;
    this -> length = -1.0;
}

Route::Route(int id, float length, ProductContainer* storage_ptr, ProductContainer* receiver_ptr)
{
    this -> id = id;
    this -> length = length;
    this -> storage_ptr = storage_ptr;
    this -> receiver_ptr = receiver_ptr;
}

Route::~Route()
{

}

//Override
inline bool Route::operator<(Route& rhs){ return this -> id < rhs.id; }
inline bool Route::operator>(Route& rhs){ return rhs < *this; }
inline bool Route::operator<=(Route& rhs){ return !(*this > rhs);  }
inline bool Route::operator>=(Route& rhs){ return !(*this < rhs);  }
inline bool Route::operator==(Route& rhs){ return this -> storage_ptr == rhs.storage_ptr && this -> receiver_ptr == rhs.receiver_ptr; }

//Setters
void Route::set_id(int id){ this -> id = id; }
void Route::set_length(float length){ this -> length = length; }

//Getters
int Route::get_id() { return id; }
float Route::get_length() { return length; }
