#pragma once
#ifndef ROUTER_H
#define ROUTER_H

#include <string>
#include <map>
#include "Route.cpp"

class Router
{
    std::string api_key;

    using Data = std::map<std::string, std::string>;
    Data inputData;

    public:
        Router();
        Router(std::string);
        virtual ~Router();

        //Overrides


        //Setters
        virtual void set_api(std::string);
        virtual void set_inputData(Data*);

        //Getters
        virtual std::string get_api();
        virtual Data* get_inputData();
};

#endif