#include "Transport.h"

Transport::Transport()
{
    this -> name = "Unnamed";
    this -> id = -1;
    this -> weightLift = -1.0;
}

Transport::Transport(std::string name, int id, float weightLiftLift)
{
    this -> name = name;
    this -> id = id;
    this -> weightLift = weightLiftLift;
}

Transport::~Transport()
{

}

//Override
inline bool Transport::operator<(Transport& rhs){ return this -> id < rhs.id; }
inline bool Transport::operator>(Transport& rhs){ return rhs < *this; }
inline bool Transport::operator<=(Transport& rhs){ return !(*this > rhs);  }
inline bool Transport::operator>=(Transport& rhs){ return !(*this < rhs);  }
inline bool Transport::operator==(Transport& rhs){ return this -> name == rhs.name && this -> weightLift == rhs.weightLift; }

//Setters
void Transport::set_name(std::string name){ this -> name = name; }
void Transport::set_id(int id){ this -> id = id; }
void Transport::set_weightLift(float weightLift){ this -> weightLift = weightLift; }

//Getters
std::string Transport::get_name() { return name; }
int Transport::get_id() { return id; }
float Transport::get_weightLift() { return weightLift; }
