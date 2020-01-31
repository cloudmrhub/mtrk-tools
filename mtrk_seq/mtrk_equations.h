#ifndef mtrk_equations_h
#define mtrk_equations_h 1

#include "fparser.hh"
#include "cJSON.h"


namespace SEQ_NAMESPACE
{  
    class mtrk_state;

    class mtrk_equations
    {
    public:
        mtrk_equations();
        virtual ~mtrk_equations();
        void setStateInstance(mtrk_state* pointer);

        void clear();

        bool prepare(cJSON* section);
        double evaluate(char* name);

        FunctionParser** parsedFunctions;
        int count;

        cJSON* equations;
    };


}

#endif