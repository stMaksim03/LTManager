#pragma once
#ifndef Transport_H
#define Transport_H

#include <string>
#include <map>




class Transport
{
    std::string name;
    int id;
    float weightLift;

    using InfoTable = std::map<std::string, std::string>;
    InfoTable auxInfo;

    public:
        Transport();
        Transport(std::string, int, float);
        ~Transport();

        //Overrides
        inline bool operator<(Transport&);
        inline bool operator>(Transport&);
        inline bool operator<=(Transport&);
        inline bool operator>=(Transport&);
        inline bool operator==(Transport&);

        //Setters
        void set_name(std::string);
        void set_id(int);
        void set_weightLift(float);

        //Getters
        std::string get_name();
        int get_id();
        float get_weightLift();
};

#endif