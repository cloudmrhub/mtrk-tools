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
    
    MTRK_LOG("Found objects: " << count)

    eventObjects=new mtrk_object*[count];
    for (int i=0; i<count; i++)
    {
        eventObjects[i]=new mtrk_object();
    }

    MTRK_LOG("Pointers prepared")

    int index=0;
    entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        MTRK_LOG("Preparing object " << index)    
        eventObjects[index]->prepare(entry);       
        cJSON_AddNumberToObject(entry, MTRK_PROPERTIES_MEMINDEX, index);
        index++;
    }    

    MTRK_LOG("Objects: " << count)
    objects=section;
    return true;
}


mtrk_object* mtrk_objects::getObject(char* name)
{
    cJSON* object = cJSON_GetObjectItemCaseSensitive(objects, name);
    if (object==NULL)
    {
        return NULL;
    }
    cJSON* indexItem = cJSON_GetObjectItemCaseSensitive(object, MTRK_PROPERTIES_MEMINDEX);
    if (indexItem==NULL)
    {
        return NULL;
    }
    return getObject(indexItem->valueint);
}


mtrk_object* mtrk_objects::getObject(int index)
{
    if ((index < 0) || (index >= count))
    {
        return NULL;
    }
    return eventObjects[index];
}


mtrk_object::mtrk_object()
{
    type=INVALID;
    syncClass=SYNC_INVALID;
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
    syncClass=SYNC_INVALID;
    duration=0;    
}


bool mtrk_object::prepare(cJSON* entry)
{
    MTRK_GETITEM(entry, MTRK_PROPERTIES_TYPE, objectType)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_DURATION, objectDuration)    

    if (strcmp(objectType->valuestring, MTRK_ACTIONS_RF)==0)
    {    
        MTRK_LOG("Preparing RF")
        type=RF;
        eventRF=new sRF_PULSE_ARB();
        eventRF->setIdent(entry->string);
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_ADC)==0)
    {    
        MTRK_LOG("Preparing ADC")
        type=ADC;
        eventADC=new sREADOUT();
        eventADC->setIdent(entry->string);
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_GRAD)==0)
    {    
        MTRK_LOG("Preparing GRAD")
        type=GRAD;
        eventGrad=new sGRAD_PULSE_ARB();
        eventGrad->setIdent(entry->string);
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_SYNC)==0)
    {    
        MTRK_LOG("Preparing SYNC")
        type=SYNC;

        MTRK_GETITEM(entry, MTRK_PROPERTIES_EVENT, eventChannel)

        // Distinguish dending on the event type
        if (strcmp(eventChannel->valuestring, "osc0")==0)
        {
            syncClass=SYNC_OSC;
            sSYNC_OSC* eventInstance=new sSYNC_OSC();
            eventInstance->setCode(SYNCCODE_OSC0);
            eventSync=(sSYNC*) eventInstance;
        }
        else   
        if (strcmp(eventChannel->valuestring, "osc1")==0)
        {
            syncClass=SYNC_OSC;            
            sSYNC_OSC* eventInstance=new sSYNC_OSC();
            eventInstance->setCode(SYNCCODE_OSC1);
            eventSync=(sSYNC*) eventInstance;
        }
        else   
        if (strcmp(eventChannel->valuestring, "trig0")==0)
        {
            syncClass=SYNC_EXTTRIGGER;            
            sSYNC_EXTTRIGGER* eventInstance=new sSYNC_EXTTRIGGER();
            eventInstance->setCode(SYNCCODE_EXT_TRIG0);
            eventSync=(sSYNC*) eventInstance;
        }
        else   
        if (strcmp(eventChannel->valuestring, "trig1")==0)
        {
            syncClass=SYNC_EXTTRIGGER;            
            sSYNC_EXTTRIGGER* eventInstance=new sSYNC_EXTTRIGGER();
            eventInstance->setCode(SYNCCODE_EXT_TRIG1);
            eventSync=(sSYNC*) eventInstance;
        }
        else
        {
            MTRK_LOG("ERROR: Unknown event type " << eventChannel->valuestring)
            return false;
        }

        eventSync->setIdent(entry->string);
        eventSync->setDuration(objectDuration->valueint);        
    }      

    object=entry;
}


