#include <iostream>
#include <string>
#include <fstream>

#include "cJSON.h"
#include "fparser.hh"
#include "mtrk_api.h"

mtrk_api::mtrk_api()
{

}


mtrk_api::~mtrk_api()
{

}


void mtrk_api::readFile()
{

    std::ifstream file("C:\\temp\\demo.mtrk");
    std::string contents((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());

    cJSON* json = cJSON_Parse(contents.c_str());
    const cJSON* section = NULL;

    std::cout << "Sections found:" << std::endl;

    cJSON_ArrayForEach(section, json)
    {
        std::cout << section->string << std::endl;
    }

    std::cout << "Done" << std::endl;
    cJSON_Delete(json);
}

