#pragma once
#ifndef RECEIVER_H
#define RECEIVER_H

#include <Product.cpp>

class Receiver
{

    std::string name;
    int id;
    std::string address;

    using ProdMap = std::map<Product*, int>;
    ProdMap* requestedProd;
    
    using InfoTable = std::map<std::string, std::string>;
    InfoTable auxInfo;

    public:
        Receiver();
        Receiver(std::string, int, std::string);
        ~Receiver();

        void merge(const Receiver*);

        //Overrides
        inline bool operator<(const Receiver&);
        inline bool operator>(const Receiver&);
        inline bool operator<=(const Receiver&);
        inline bool operator>=(const Receiver&);
        inline bool operator==(const Receiver&);
        inline bool operator=(ProdMap*);
        inline Product& operator[](int);

        //Setters
        void set_name(std::string);
        void set_id(int);
        void set_address(std::string);
        void insert(Product*, int);
        void insert(std::string, int, float, int);
        //void set_storedProd(Product*[]);

        //Getters
        std::string get_name();
        int get_id();
        std::string get_address();
        Product* get_by_id(int);
        ProdMap* get_requestedProd();
};

#endif