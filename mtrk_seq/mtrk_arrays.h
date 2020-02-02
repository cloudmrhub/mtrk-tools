#ifndef mtrk_arrays_h
#define mtrk_arrays_h 1

#include "cJSON.h"

namespace SEQ_NAMESPACE
{  
    class mtrk_state;

    class mtrk_array 
    {
    public:   
        enum
        {
            INVALID=-1,
            INT=0,
            FLOAT=1,
            COMPLEX_FLOAT=2,
            DOUBLE=3,
            COMPLEX_DOUBLE=4
        };

        enum 
        {
            TEXT=0,
            BASE64=1
        };

        mtrk_array();
        virtual ~mtrk_array();

        void clear();
        bool allocate(int dataType, int dataSize);
        bool load(cJSON* dataItem, int encoding);
        bool loadText(cJSON* dataItem);
        bool loadBase64(cJSON* dataItem);

        double getDouble  (int index);
        int    getInt     (int index);
        double getFreqency(int index);
        double getPhase   (int index);

        float* getData();
        
        void dump();

        void* data;
        int size;
        int type;
        size_t elementSize;
    };


    class mtrk_arrays
    {    
    public:
        mtrk_arrays();
        virtual ~mtrk_arrays();
        
        void clear();
        bool prepare(cJSON* section);
        mtrk_array* getArray(int index);
        mtrk_array* getArray(char* name);      

        void dumpAll();

        mtrk_array** arrayData;
        cJSON* arrays;
        int count;
    };

}

#endif
