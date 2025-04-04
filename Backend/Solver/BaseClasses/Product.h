#pragma once
#ifndef PRODUCT_H
#define PRODUCT_H

#include <string>
#include <map>




class Product
{
    std::string name;
    int id;
    float weight;

    using InfoTable = std::map<std::string, std::string>;
    InfoTable auxInfo;

    public:
        Product();
        Product(std::string, int, float);
        ~Product();

        //Overrides
        inline bool operator<(Product&);
        inline bool operator>(Product&);
        inline bool operator<=(Product&);
        inline bool operator>=(Product&);
        inline bool operator==(Product&);

        //Setters
        void set_name(std::string);
        void set_id(int);
        void set_weight(float);

        //Getters
        std::string get_name();
        int get_id();
        float get_weight();
};

#endif