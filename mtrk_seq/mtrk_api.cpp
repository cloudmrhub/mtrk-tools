#include <iostream>
#include <string>
#include <fstream>


#include "fparser.hh"
#include "mtrk_api.h"
#include "mtrk.h"

using namespace SEQ_NAMESPACE;


mtrk_sections::mtrk_sections()
{
    clear();
}


void mtrk_sections::clear()
{
    file=0;
    settings=0;
    instructions=0;
    objects=0;
    arrays=0;
    equations=0; 
}


bool mtrk_sections::isComplete()
{
    return (file && settings && instructions && objects && arrays && equations);
}


bool mtrk_sections::load(cJSON* sequence)
{
    clear();

    cJSON* section = NULL;
    cJSON_ArrayForEach(section, sequence)
    {
        if (strcmp(section->string,MTRK_SECTIONS_FILE)==0)
        {
            file=section;
        }
        else
        if (strcmp(section->string,MTRK_SECTIONS_SETTINGS)==0)
        {
            settings=section;
        }   
        else     
        if (strcmp(section->string,MTRK_SECTIONS_INSTRUCTIONS)==0)
        {
            instructions=section;
        }   
        else
        if (strcmp(section->string,MTRK_SECTIONS_OBJECTS)==0)
        {
            objects=section;
        }
        else
        if (strcmp(section->string,MTRK_SECTIONS_ARRAYS)==0)
        {
            arrays=section;
        }   
        else      
        if (strcmp(section->string,MTRK_SECTIONS_EQUATIONS)==0)
        {
            equations=section;
        }                    
    }

    return isComplete();
}


cJSON* mtrk_sections::getBlock(char* id)
{
    cJSON* block=cJSON_GetObjectItemCaseSensitive(instructions, id);

    if (block==0)
    {
        MTRK_LOG("ERROR: Requested block not found " << id)
    }

    return block;    
}


mtrk_state::mtrk_state()
{
    reset();
}


void mtrk_state::reset()
{
    for (int i=0; i<MTRK_DEFS_COUNTERS; i++)
    {
        counters[i]=0;        
    }
    for (int i=0; i<MTRK_DEFS_FLOATS; i++)
    {
        floats[i]=0.;
    }
    clock=0;
    table_start=0;
    table_duration=0;    
}


mtrk_api::mtrk_api()
{
    parent=0;
    sequence=0;
    loadedMeasurementID=0;
}


void mtrk_api::setParent(mtrk* parentSequence)
{
    parent=parentSequence;
}


mtrk_api::~mtrk_api()
{
    unloadSequence();
}


bool mtrk_api::loadSequence(std::string filename, bool forceLoad)
{
    if (sequence==0)
    {
        forceLoad=true;
    }

    std::ifstream file(filename.c_str());
    std::string contents((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());

    cJSON* tempSequence = cJSON_Parse(contents.c_str());

    if (tempSequence==NULL) 
    {
        MTRK_LOG("Unable to parse sequence file")      
        return false;        
    }

    cJSON* file_section=cJSON_GetObjectItemCaseSensitive(tempSequence, MTRK_SECTIONS_FILE);
    if (file_section==NULL) 
    {
        MTRK_LOG("Invalid MTRK file (file section missing)")
        return false;
    }
    cJSON* measurement_item=cJSON_GetObjectItemCaseSensitive(file_section, MTRK_PROPERTIES_MEASUREMENT);
    if (cJSON_IsString(measurement_item) && (measurement_item->valuestring != NULL))
    {
        if ((!forceLoad) && (loadedMeasurementID!=0) && (strcmp(loadedMeasurementID,measurement_item->valuestring)==0))
        {
            MTRK_LOG("Sequence already loaded")
            cJSON_Delete(tempSequence);
            return true;
        }
    }
    else 
    {
        MTRK_LOG("Invalid MTRK file (measurement item missing)")
        return false;
    }

    state.reset();
    unloadSequence();

    sequence=tempSequence;

    if (!sections.load(sequence))
    {
        MTRK_LOG("ERROR: Sequence file incomplete.")
        unloadSequence();
        return false;
    }

    MTRK_LOG("Sequence instructions loaded.")
    return true;
}


void mtrk_api::unloadSequence()
{
    if (sequence)
    {
        cJSON_Delete(sequence);
        sequence=0;
    }
    MTRK_DELETE(loadedMeasurementID)    
}


bool mtrk_api::prepare(bool isBinarySearch)
{
    if (isBinarySearch)
    {
        //return true;
    }
    
    MTRK_RETONFAIL(loadSequence("C:\\temp\\demo.mtrk"))
    MTRK_RETONFAIL(prepareArrays())
    MTRK_RETONFAIL(prepareObjects())    
    MTRK_RETONFAIL(prepareEquations())    
    MTRK_RETONFAIL(prepareBlocks())    

    // DEBUG
    run();

    return true;
}


bool mtrk_api::prepareArrays()
{
    return true;
}


bool mtrk_api::prepareObjects()
{
    return true;
}


bool mtrk_api::prepareEquations()
{
    return true;
}


bool mtrk_api::prepareBlocks()
{
    return true;
}


bool mtrk_api::runBlock(cJSON* block)
{
    if (block==0) 
    {
        MTRK_LOG("ERROR: Empty block started.")        
        return false;
    }
    recursions++;
    if (recursions > 1000) 
    {
        MTRK_LOG("ERROR: Recursion limit reached. Aborting.")
        return false;
    }
    
    cJSON* steps=cJSON_GetObjectItemCaseSensitive(block, MTRK_PROPERTIES_STEPS);
    if (steps==0)
    {
        MTRK_LOG("ERROR: Steps missing in block. Aborting.")
        return false;
    }

    bool success=true;
    cJSON* step=0;
    cJSON_ArrayForEach(step, steps)
    {
        cJSON* action = cJSON_GetObjectItemCaseSensitive(step, MTRK_PROPERTIES_ACTION);
        //MTRK_LOG("RunBlock " << state.counters[0]  << " " << state.counters[1]  << " "  << state.counters[2])

        if (strcmp(action->valuestring, MTRK_ACTIONS_LOOP)==0)
        {
            success=runActionLoop(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_RUN_BLOCK)==0)
        {
            success=runActionBlock(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_CONDITION)==0)
        {
            success=runActionCondition(step);
        }
        else      
        if (strcmp(action->valuestring, MTRK_ACTIONS_INIT)==0)
        {
            success=runActionInit(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_SUBMIT)==0)
        {
            success=runActionSubmit(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_RF)==0)
        {
            success=runActionRF(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_ADC)==0)
        {
            success=runActionADC(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_GRAD)==0)
        {
            success=runActionGrad(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_SYNC)==0)
        {
            success=runActionSync(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_MARK)==0)
        {
            success=runActionMark(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_CALC)==0)
        {
            success=runActionCalc(step);
        }
        else
        if (strcmp(action->valuestring, MTRK_ACTIONS_DEBUG)==0)
        {
            success=runActionDebug(step);
        }
        else
        {
            MTRK_LOG("ERROR: Unknown action found " << action->valuestring)
        }

        if (!success)
        {
            MTRK_LOG("Processing steps terminated")
            break;
        }
    }    
    recursions--;
    return success;
}


#define MTRK_GETITEM(a,b,c) cJSON* c = cJSON_GetObjectItemCaseSensitive(a,b); if (a==NULL) { MTRK_LOG("Missing item " << MTRK_PROPERTIES_RANGE) return false; }

bool mtrk_api::runActionLoop(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_RANGE, range)
    MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
       
    int range_int=range->valueint;
    int counter_int=counter->valueint;

    for (state.counters[counter_int]=0; state.counters[counter_int]<range_int; state.counters[counter_int]++)
    {
        runBlock(item);
    }

    return true;
}


bool mtrk_api::runActionBlock(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_BLOCK, blockName)
    cJSON* block = sections.getBlock(blockName->valuestring);    
    return runBlock(block);
}


bool mtrk_api::runActionCondition(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionInit(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionSubmit(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionRF(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionADC(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionGrad(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionSync(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionMark(cJSON* item)
{
    return true;
}


bool mtrk_api::runActionCalc(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_TYPE, type)
    MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)

    if (strcmp(type->valuestring, MTRK_OPTIONS_COUNTER_INC)==0)
    {
        int counter_int=counter->valueint;
        state.counters[counter_int]++;
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_COUNTER_SET)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_VALUE, value)

        int counter_int=counter->valueint;
        int value_int=value->valueint;
        state.counters[counter_int]=value_int;
    }

    return true;
}


bool mtrk_api::runActionDebug(cJSON* item)
{
    return true;
}


bool mtrk_api::run()
{
    MTRK_LOG("Running sequence")
    state.reset();
    recursions=0;

    MTRK_LOG("RunBlock")
    MTRK_RETONFAIL(runBlock(sections.getBlock(MTRK_OPTIONS_MAIN)))
   
    return true;
}

