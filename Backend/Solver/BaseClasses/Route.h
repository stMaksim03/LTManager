#pragma once
#ifndef ROUTE_H
#define ROUTE_H

#include <string>
#include <map>
#include "ProductContainer.cpp"

class Route
{
    int id;
    float length;
    ProductContainer* storage_ptr;
    ProductContainer* receiver_ptr;

    using Data = std::map<std::string, std::string>;
    Data inputData;

    public:
        Route();
        Route(int, float, ProductContainer*, ProductContainer*);
        ~Route();

        //Overrides
        inline bool operator<(Route&);
        inline bool operator>(Route&);
        inline bool operator<=(Route&);
        inline bool operator>=(Route&);
        inline bool operator==(Route&);

        //Setters
        void set_id(int);
        void set_length(float);

        //Getters
        int get_id();
        float get_length();
};

#endif