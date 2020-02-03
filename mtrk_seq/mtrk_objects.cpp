#include "mtrk_common.h"
#include "mtrk_arrays.h"
#include "mtrk_api.h"


using namespace SEQ_NAMESPACE;

mtrk_objects::mtrk_objects()
{
    objects=0;
    count=0;    
    eventObjects=0;
}


mtrk_objects::~mtrk_objects()
{
    clear();
}


void mtrk_objects::clear()
{
    if (eventObjects!=0)
    {
        for (int i=0; i<count; i++)
        {
            if (eventObjects[i]!=0)
            {
                delete eventObjects[i];
                eventObjects[i]=0;
            }
        }

        delete[] eventObjects;
        eventObjects=0; 
    }
    objects=0;    
    count=0;
}


bool mtrk_objects::prepare(cJSON* section)
{
    MTRK_LOG("Preparing Objects")
    clear();

    cJSON* entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        count++;
    }        
    
    eventObjects=new mtrk_object*[count];
    for (int i=0; i<count; i++)
    {
        eventObjects[i]=new mtrk_object();
    }

    int index=0;

    entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        eventObjects[index]->prepare(entry);       
        cJSON_AddNumberToObject(entry, MTRK_PROPERTIES_MEMINDEX, index);
        index++;
    }    

    MTRK_LOG("Objects: " << count)
    objects=section;
    return true;
}




mtrk_object::mtrk_object()
{
    type=INVALID;
    duration=0;

    eventGrad=0;
    eventSync=0;
    eventADC=0;
    eventRF=0;
    eventNCOSet=0;
    eventNCOReset=0;

    object=0;
}


mtrk_object::~mtrk_object()
{
    clear();
}


void mtrk_object::clear()
{
    MTRK_LOG("Object destructor")

    MTRK_DELETE(eventGrad)
    MTRK_DELETE(eventSync)
    MTRK_DELETE(eventADC)
    MTRK_DELETE(eventRF)
    MTRK_DELETE(eventNCOSet)
    MTRK_DELETE(eventNCOReset)

    object=0;
    type=INVALID;
    duration=0;    
}


bool mtrk_object::prepare(cJSON* entry)
{
    MTRK_GETITEM(entry, MTRK_PROPERTIES_TYPE, objectType)

    if (strcmp(objectType->valuestring, MTRK_ACTIONS_RF)==0)
    {    
        MTRK_LOG("Preparing RF")
        type=RF;
        eventRF=new sRF_PULSE_ARB();
        eventRF->setIdent(entry->string);
    }

    object=entry;
}

