#pragma once
#ifndef PRODUCTCONTAINER_H
#define PRODUCTCONTAINER_H

#include "Product.cpp"

class ProductContainer
{
    std::string name;
    int id;
    std::string address;


    struct compare
    {
        inline bool operator()(Product* a, Product* b) const{ return *a < *b; };
    };
    
    using ProdMap = std::map<Product*, int, compare>;
    ProdMap* storedProd;
    
    using InfoTable = std::map<std::string, std::string>;
    InfoTable auxInfo;

    void defaultValues();

    public:
        ProductContainer();
        ProductContainer(std::string, int, std::string);
        ~ProductContainer();
        

        void merge(const ProductContainer*);

        //Overrides
        inline bool operator<(ProductContainer&);
        inline bool operator>(ProductContainer&);
        inline bool operator<=(ProductContainer&);
        inline bool operator>=(ProductContainer&);
        inline bool operator==(ProductContainer&);
        inline bool operator=(ProdMap*);
        inline Product* operator[](int);

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
        ProdMap* get_storedProd();

};

#endif