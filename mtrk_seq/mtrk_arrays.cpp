#include <stdlib.h> 

#include "mtrk_common.h"
#include "mtrk_arrays.h"
#include "mtrk_api.h"
#include "mtrk_b64.h"


using namespace SEQ_NAMESPACE;


mtrk_array::mtrk_array()
{
    data=0;
    size=-1;
    type=INVALID;
    elementSize=0;
}


mtrk_array::~mtrk_array()
{
    clear();
}


bool mtrk_array::allocate(int dataType, int dataSize)
{
    switch (dataType)
    {
    case INTEGER:
        elementSize=sizeof(int);
        break;
    case FLOAT:
        elementSize=sizeof(float);    
        break;
    case COMPLEX_FLOAT:
        elementSize=2*sizeof(float);    
        break;
    case DOUBLE:
        elementSize=sizeof(double);        
        break;
    case COMPLEX_DOUBLE:
        elementSize=2*sizeof(double);        
        break;   
    case INVALID:
    default:
        return false;
        break;
    }

    type=dataType;
    size=dataSize;
    data=calloc(dataSize,elementSize);

    return (data != 0);
}


void mtrk_array::clear()
{
    if (data!=0)
    {
        free(data);
        data=0;
    }
}


bool mtrk_array::load(cJSON* dataItem, int encoding)
{
    if (encoding==TEXT) 
    {
        return loadText(dataItem);
    }
    else
    if (encoding==BASE64) 
    {
        return loadBase64(dataItem);
    }

    MTRK_LOG("ERROR: Unkown encoding encountered.")
    return false;
}


bool mtrk_array::loadText(cJSON* dataItem)
{
    if (!cJSON_IsArray(dataItem)) 
    {
        MTRK_LOG("ERROR: Data item is not an array.");
    }

    int i=0;
    cJSON* entry=0;

    if (type==INTEGER)
    {
        cJSON_ArrayForEach(entry, dataItem)
        {
            ((int*) data)[i]=entry->valueint;
            i++;
            if (i>size) 
            {
                MTRK_LOG("ERROR: Array exceeds expected size")
                return false;
            }
        }
        if (i!=size) 
        {
            MTRK_LOG("ERROR: Array size different from prediction")
            return false;
        }
    }
    else
    if (type==FLOAT)        
    {
        cJSON_ArrayForEach(entry, dataItem)
        {
            ((float*) data)[i]=(float) entry->valuedouble;
            i++;
            if (i>size) 
            {
                MTRK_LOG("ERROR: Array exceeds expected size")
                return false;
            }
        }    
        if (i!=size) 
        {
            MTRK_LOG("ERROR: Array size different from prediction")
            return false;
        }                
    }
    else
    if (type==DOUBLE)        
    {
        cJSON_ArrayForEach(entry, dataItem)
        {
            ((double*) data)[i]=entry->valuedouble;
            i++;
            if (i>size) 
            {
                MTRK_LOG("ERROR: Array exceeds expected size")
                return false;
            }
        }
        if (i!=size) 
        {
            MTRK_LOG("ERROR: Array size different from prediction")
            return false;
        }        
    }
    else
    if (type==COMPLEX_FLOAT)        
    {
        cJSON_ArrayForEach(entry, dataItem)
        {
            ((float*) data)[i]=(float) entry->valuedouble;
            i++;
            if (i>2*size) 
            {
                MTRK_LOG("ERROR: Array exceeds expected size")
                return false;
            }
        }
        if (i!=2*size) 
        {
            MTRK_LOG("ERROR: Array size different from prediction")
            return false;
        }           
    }
    else
    if (type==COMPLEX_DOUBLE)        
    {
        cJSON_ArrayForEach(entry, dataItem)
        {
            ((double*) data)[i]=entry->valuedouble;
            i++;
            if (i>2*size) 
            {
                MTRK_LOG("ERROR: Array exceeds expected size")
                return false;
            }
        }            
        if (i!=2*size) 
        {
            MTRK_LOG("ERROR: Array size different from prediction")
            return false;
        }                   
    }
    else
    {
        MTRK_LOG("ERROR: Unkown array type encountered.")
        return false;
    }

    return true;
}


bool mtrk_array::loadBase64(cJSON* dataItem)
{
    if (!cJSON_IsString(dataItem)) 
    {
        MTRK_LOG("ERROR: Data item is not a base64 string.");
    }
    
    return true;
}


double mtrk_array::getDouble(int index)
{
    if ((index<0) || (index>=size))
    {
        return 0.;
    }
    
    switch (type)
    {
    case INTEGER:
        return ((int*) data)[index];
        break;
    case FLOAT:
        return ((float*) data)[index];
        break;
    case COMPLEX_FLOAT:
        return ((float*) data)[2*index];
        break;
    case DOUBLE:
        return ((double*) data)[index];
        break;
    case COMPLEX_DOUBLE:
        return ((double*) data)[2*index];
        break;   
    case INVALID:
    default:
        return 0.;
        break;
    }
    return 0.;
}


int mtrk_array::getInt(int index)
{
    if ((index<0) || (index>=size))
    {
        return 0;
    }

    switch (type)
    {
    case INTEGER:
        return ((int*) data)[index];
        break;
    case FLOAT:
        return int(((float*) data)[index]);
        break;
    case COMPLEX_FLOAT:
        return int(((float*) data)[2*index]);
        break;
    case DOUBLE:
        return int(((double*) data)[index]);
        break;
    case COMPLEX_DOUBLE:
        return int(((double*) data)[2*index]);
        break;   
    case INVALID:
    default:
        return 0;
        break;
    }
    return 0;
}


double mtrk_array::getFreqency(int index)
{
    if ((index<0) || (index>=size))
    {
        return 0;
    }

    switch (type)
    {
    case COMPLEX_FLOAT:
        return ((float*) data)[2*index+1];
        break;
    case COMPLEX_DOUBLE:
        return ((double*) data)[2*index+1];
        break;   
    case INTEGER:
    case FLOAT:
    case DOUBLE:
    case INVALID:
    default:
        return 0.;
        break;
    }    

    return 0.;
}


double mtrk_array::getPhase(int index)
{
    if ((index<0) || (index>=size))
    {
        return 0;
    }

    switch (type)
    {
    case COMPLEX_FLOAT:
        return ((float*) data)[2*index+1];
        break;
    case COMPLEX_DOUBLE:
        return ((double*) data)[2*index+1];
        break;   
    case INTEGER:
    case FLOAT:
    case DOUBLE:
    case INVALID:
    default:
        return 0.;
        break;
    }    

    return 0.;
}


float* mtrk_array::getData()
{
    return (float*) data;
}


mtrk_arrays::mtrk_arrays()
{
    arrays=0;
    arrayData=0;
    count=0;
}


mtrk_arrays::~mtrk_arrays()
{
    clear();
}


void mtrk_arrays::clear()
{
    if (arrayData!=0)
    {
        for (int i=0; i<count; i++)
        {
            if (arrayData[i]!=0)
            {
                delete arrayData[i];
                arrayData[i]=0;
            }
        }

        delete[] arrayData;
        arrayData=0; 
    }
    arrays=0;    
    count=0;
}


bool mtrk_arrays::prepare(cJSON* section)
{
    MTRK_LOG("Preparing Arrays")

    clear();

    cJSON* entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        count++;
    }        
    
    arrayData=new mtrk_array*[count];
    for (int i=0; i<count; i++)
    {
        arrayData[i]=new mtrk_array();
    }

    int index=0;

    entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        MTRK_GETITEM(entry, MTRK_PROPERTIES_TYPE, arrayType)
        MTRK_GETITEM(entry, MTRK_PROPERTIES_ENCODING, encoding)
        MTRK_GETITEM(entry, MTRK_PROPERTIES_SIZE, size)
        MTRK_GETITEM(entry, MTRK_PROPERTIES_DATA, data)

        int type_int=mtrk_array::INVALID;
        int size_int=size->valueint;       
        int encoding_int=mtrk_array::TEXT;
        
        if (strcmp(encoding->valuestring, MTRK_OPTIONS_BASE64)==0)
        {
            encoding_int=mtrk_array::BASE64;
        }

        if (strcmp(arrayType->valuestring, MTRK_OPTIONS_INTEGER)==0)
        {
            type_int=mtrk_array::INTEGER;
        }
        else
        if (strcmp(arrayType->valuestring, MTRK_OPTIONS_FLOAT)==0)
        {
            type_int=mtrk_array::FLOAT;            
        }
        else
        if (strcmp(arrayType->valuestring, MTRK_OPTIONS_COMPLEX_FLOAT)==0)
        {
            type_int=mtrk_array::COMPLEX_FLOAT;            
        }
        else
        if (strcmp(arrayType->valuestring, MTRK_OPTIONS_DOUBLE)==0)
        {
            type_int=mtrk_array::DOUBLE;            
        }
        else
        if (strcmp(arrayType->valuestring, MTRK_OPTIONS_COMPLEX_DOUBLE)==0)
        {
            type_int=mtrk_array::COMPLEX_DOUBLE;            
        }

        cJSON_AddNumberToObject(entry, MTRK_PROPERTIES_MEMINDEX, index);
        arrayData[index]->allocate(type_int, size_int);
        
        if (!arrayData[index]->load(data, encoding_int))
        {
            return false;
        }

        index++;
    }    

    MTRK_LOG("Arrays: " << count)
    arrays=section;
    
    return true;
}