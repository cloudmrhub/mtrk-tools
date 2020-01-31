#include "mtrk_common.h"
#include "mtrk_equations.h"
#include "mtrk_api.h"

using namespace SEQ_NAMESPACE;


mtrk_state* stateInstance=0;


mtrk_equations::mtrk_equations()
{
    parsedFunctions=0;
    count=0;
    equations=0;
}


mtrk_equations::~mtrk_equations()
{
    clear();
}


void mtrk_equations::setStateInstance(mtrk_state* pointer)
{
    stateInstance=pointer;
}


void mtrk_equations::clear()
{
    if (parsedFunctions!=0)
    {
        for (int i=0; i<count; i++)
        {
            if (parsedFunctions[i]!=0)
            {
                delete parsedFunctions[i];
                parsedFunctions[i]=0;
            }
        }

        delete[] parsedFunctions;
        parsedFunctions=0; 
    }
    equations=0;
}


double getCounter(const double* p)
{
    int index=int(p[0]);
    if ((index<0) || (index>=MTRK_DEFS_COUNTERS))
    {
        return -1;
    }
    return stateInstance->counters[index];
}


double getFloat(const double* p)
{
    int index=int(p[0]);
    if ((index<0) || (index>=MTRK_DEFS_FLOATS))
    {
        return -1;
    }
    return stateInstance->floats[index];
}


bool mtrk_equations::prepare(cJSON* section)
{
    clear();

    cJSON* entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        count++;
    }        
    
    parsedFunctions=new FunctionParser*[count];
    for (int i=0; i<count; i++)
    {
        parsedFunctions[i]=new FunctionParser;
    }

    int index=0;

    entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        MTRK_GETITEM(entry, MTRK_PROPERTIES_EQUATION, equation)
        std::string equation_str(equation->valuestring);

        parsedFunctions[index]->AddFunction("ctr", getCounter, 1);
        parsedFunctions[index]->AddFunction("flt", getFloat, 1);
        parsedFunctions[index]->Parse(equation_str, "x");
        cJSON_AddNumberToObject(entry, MTRK_PROPERTIES_MEMINDEX, index);

        index++;
    }    

    MTRK_LOG("Equation: " << count)
    equations=section;

    return true;
}


double mtrk_equations::evaluate(char* name)
{
    cJSON* equation = cJSON_GetObjectItemCaseSensitive(equations, name);
    if (equation==NULL)
    {
        return 0.;
    }
    cJSON* index = cJSON_GetObjectItemCaseSensitive(equation, MTRK_PROPERTIES_MEMINDEX);
    if (index==NULL)
    {
        return 0.;
    }
    double variables[1] = { 1.0 };
    return parsedFunctions[index->valueint]->Eval(variables);
}
