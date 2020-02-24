#include <iostream>
#include <string>
#include <fstream>

#include "fparser.hh"
#include "mtrk_api.h"
#include "mtrk.h"

using namespace SEQ_NAMESPACE;


mtrk_sections::mtrk_sections()
{
    loadedMeasurementID=0;
    clear();
}


mtrk_sections::~mtrk_sections()
{
    clear();
}


void mtrk_sections::clear()
{
    file=0;
    settings=0;
    infos=0;
    instructions=0;
    objects=0;
    arrays=0;
    equations=0; 
    MTRK_DELETE(loadedMeasurementID);
    loadedFilename="";
}


bool mtrk_sections::isComplete()
{
    return (file && settings && infos && instructions && objects && arrays && equations);
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
            cJSON* measurementID=cJSON_GetObjectItemCaseSensitive(section, MTRK_PROPERTIES_MEASUREMENT);
            
            loadedMeasurementID=new char[strlen(measurementID->valuestring)+1];
            strcpy(loadedMeasurementID,measurementID->valuestring);
        }
        else
        if (strcmp(section->string,MTRK_SECTIONS_SETTINGS)==0)
        {
            settings=section;
        }   
        else     
        if (strcmp(section->string,MTRK_SECTIONS_INFOS)==0)
        {
            infos=section;
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


void mtrk_state::reset(bool dryRun)
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
    tableStart=0;
    tableDuration=0;    
    isDryRun=dryRun;

    totalDuration=0;
}


mtrk_api::mtrk_api()
{
    parent=0;
    sequence=0;
    equations.setStateInstance(&state);
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
        if ((!forceLoad) && (sections.loadedMeasurementID!=0) && (strcmp(sections.loadedMeasurementID,measurement_item->valuestring)==0))
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
    sections.loadedFilename=filename;

    MTRK_RETONFAIL(arrays.prepare(sections.arrays))
    MTRK_RETONFAIL(objects.prepare(sections.objects))    
    MTRK_RETONFAIL(equations.prepare(sections.equations))    
    MTRK_RETONFAIL(prepareBlocks())    

    MTRK_LOG("Sequence instructions loaded.")
    return true;
}


void mtrk_api::unloadSequence()
{
    sections.clear();
    arrays.clear();
    equations.clear();
    objects.clear();

    if (sequence)
    {
        cJSON_Delete(sequence);
        sequence=0;
    }
}


bool mtrk_api::prepare(bool isBinarySearch)
{
    if (isBinarySearch)
    {
        //return true;
    }
    
    MTRK_RETONFAIL(loadSequence("C:\\temp\\demo.mtrk"))

    // Perform a dry run to calculate the time and SAR
    run(true);

    MTRK_LOG("Total time: " << state.totalDuration)

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
            break;
        }
    }    
    recursions--;
    return success;
}



bool mtrk_api::runActionLoop(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_RANGE, range)
    MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
       
    int range_int=range->valueint;
    int counter_int=counter->valueint;

    for (state.counters[counter_int]=0; state.counters[counter_int]<range_int; state.counters[counter_int]++)
    {
        if (!runBlock(item)) 
        {
            return false;
        }
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
    MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
    MTRK_GETITEM(item, MTRK_PROPERTIES_TARGET, target)
    int counter_int=counter->valueint;
    if ((counter_int<0) || (counter_int>=MTRK_DEFS_COUNTERS))
    {
        return false;
    }

    if (state.counters[counter_int]==target->valueint)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_TRUE, trueBlock);
        if (cJSON_GetObjectItemCaseSensitive(trueBlock,MTRK_PROPERTIES_STEPS) != NULL) 
        {
            return runBlock(trueBlock);
        }        
    }
    else
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_FALSE, falseBlock);
        if (cJSON_GetObjectItemCaseSensitive(falseBlock,MTRK_PROPERTIES_STEPS) != NULL) 
        {           
            return runBlock(falseBlock);
        }
    }

    return true;
}


bool mtrk_api::runActionInit(cJSON* item)
{
    if (!state.isDryRun)
    {    
        // TODO: Update slice object
        NLSStatus result=fRTEBInit(parent->m_asSLC[0].getROT_MATRIX());
        if (result.isError())
        {
            MTRK_LOG("ERROR running fRTEBInit")
            return false;            
        }
    }
    
    state.tableDuration = 0;
    state.tableStart = 0;
    
    return true;
}


bool mtrk_api::runActionSubmit(cJSON* item)
{
    if (!state.isDryRun)
    {    
        NLSStatus result=fRTEBFinish();
        if (result.isError())
        {
            MTRK_LOG("ERROR running fRTEBFinish")
            return false;            
        }
    }

    state.clock += state.tableDuration;
    state.tableDuration = -1;
    state.tableStart = -1;

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


#define MTRK_ADD_SYNC_CASE(A,B) case mtrk_object::A: fRTEI(time->valueint, 0, 0, 0, 0, 0, 0, &(*(B*) object->eventSync)); break;

bool mtrk_api::runActionSync(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_TIME, time)
    MTRK_GETITEM(item, MTRK_PROPERTIES_OBJECT, objectName)

    mtrk_object* object = objects.getObject(objectName->valuestring);

    if (!state.isDryRun)
    {       
        switch (object->syncClass)
        {
            MTRK_ADD_SYNC_CASE(SYNC_OSC,sSYNC_OSC)
            MTRK_ADD_SYNC_CASE(SYNC_EXTTRIGGER,sSYNC_EXTTRIGGER)
            // TODO: Add remaining classes
        default:
        case mtrk_object::SYNC_INVALID:
            MTRK_LOG("ERROR: Invalid sync object requested")
            break;            
        }
    }
    state.updateDuration(time->valueint, object->duration);
      
    return true;
}


bool mtrk_api::runActionMark(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_TIME, time)

    if (!state.isDryRun)
    {
        fRTEI(time->valueint, 0, 0, 0, 0, 0, 0, 0);
    }
    state.updateDuration(time->valueint);
    
    return true;
}


bool mtrk_api::runActionCalc(cJSON* item)
{
    MTRK_GETITEM(item, MTRK_PROPERTIES_TYPE, type)

    if (strcmp(type->valuestring, MTRK_OPTIONS_COUNTER_INC)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
        int counter_int=counter->valueint;
        if ((counter_int<0) || (counter_int>=MTRK_DEFS_COUNTERS))
        {
            return false;
        }
        state.counters[counter_int]++;
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_COUNTER_SET)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
        MTRK_GETITEM(item, MTRK_PROPERTIES_VALUE, value)
        int counter_int=counter->valueint;
        if ((counter_int<0) || (counter_int>=MTRK_DEFS_COUNTERS))
        {
            return false;
        }       
        state.counters[counter_int]=value->valueint;
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_FLOAT_INC)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_FLOAT, index)
        int index_int=index->valueint;
        if ((index_int<0) || (index_int>=MTRK_DEFS_FLOATS))
        {
            return false;
        }        
        state.floats[index_int]+=1.;
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_FLOAT_SET)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_FLOAT, index)
        MTRK_GETITEM(item, MTRK_PROPERTIES_VALUE, value)
        int index_int=index->valueint;
        if ((index_int<0) || (index_int>=MTRK_DEFS_FLOATS))
        {
            return false;
        }              
        state.floats[index_int]=value->valuedouble;
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_EQUATION)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_EQUATION, equation)

        int index=0;
        bool targetIsFloat=true;
        cJSON* float_target = cJSON_GetObjectItemCaseSensitive(item,MTRK_PROPERTIES_FLOAT); 
        if (float_target!=NULL) 
        { 
            index=float_target->valueint;
        }
        else
        {
            targetIsFloat=false;
            cJSON* counter_target = cJSON_GetObjectItemCaseSensitive(item,MTRK_PROPERTIES_COUNTER); 
            if (counter_target==NULL)
            {
                MTRK_LOG("Missing item " << MTRK_PROPERTIES_COUNTER);
                return false; 
            }
            index=float_target->valueint;
        }

        double equationValue=equations.evaluate(equation->valuestring);

        if (targetIsFloat) 
        {
            state.floats[index]=equationValue;
        }
        else
        {
            state.counters[index]=int(equationValue);
        }
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_RFSPOIL)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_INCREMENT, increment)
        MTRK_GETITEM(item, MTRK_PROPERTIES_FLOAT, index)
        int index_int=index->valueint;

        // Note: Two floats are needed for the RF spoiling scheme
        if ((index_int<0) || (index_int>=MTRK_DEFS_FLOATS-1))
        {
            return false;
        }

        // Increase the increment
        state.floats[index_int+1]+=increment->valuedouble;

        // Increase the actual RF phase with the increment
        state.floats[index_int]+=state.floats[index_int+1];
    }
    else
    if (strcmp(type->valuestring, MTRK_OPTIONS_FLOAT_GET)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_ARRAY, array)
        MTRK_GETITEM(item, MTRK_PROPERTIES_FLOAT, target)
        MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)
        int target_int=target->valueint;      
        int counter_int=counter->valueint;      

        if ((target_int<0) || (target_int>=MTRK_DEFS_FLOATS))
        {
            return false;
        }

        // TODO
        state.floats[target_int]=0.;
    }

    return true;
}


bool mtrk_api::runActionDebug(cJSON* item)
{
    return true;
}


bool mtrk_api::run(bool isDryRun)
{
    MTRK_LOG("Running sequence")
    state.reset(isDryRun);
    recursions=0;

    MTRK_LOG("RunBlock")
    MTRK_RETONFAIL(runBlock(sections.getBlock(MTRK_OPTIONS_MAIN)))
    if (state.tableStart != -1)
    {
        MTRK_LOG("ERROR: Sequence not properly terminated")
        return false;
    }
    state.totalDuration=state.clock;
   
    //MTRK_LOG("EQ1 = " << equations.evaluate("kspace_pe"))
    //MTRK_LOG("EQ2 = " << equations.evaluate("test"))
    //MTRK_LOG("SEQNAME = " << getInfoString(MTRK_INFOS_SEQSTRING,"M"))
    //arrays.dumpAll();

    return true;
}


int mtrk_api::getInfoInt(char* name, int defaultValue)
{
    cJSON* item = cJSON_GetObjectItemCaseSensitive(sections.infos,name);
    if (item==NULL)
    {
        return defaultValue;
    }    
    else
    {
        return item->valueint;    
    }
}


double mtrk_api::getInfoDouble(char* name, double defaultValue)
{
    cJSON* item = cJSON_GetObjectItemCaseSensitive(sections.infos,name);
    if (item==NULL)
    {
        return defaultValue;
    }    
    else
    {
        return item->valuedouble;
    }
}


char* mtrk_api::getInfoString(char* name, char* defaultValue)
{
    cJSON* item = cJSON_GetObjectItemCaseSensitive(sections.infos,name);
    if (item==NULL)
    {
        return defaultValue;
    }    
    else
    {
        return item->valuestring;    
    }
}
