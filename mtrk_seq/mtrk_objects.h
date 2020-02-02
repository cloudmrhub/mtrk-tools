#ifndef mtrk_objects_h
#define mtrk_objects_h 1

#include "cJSON.h"

namespace SEQ_NAMESPACE
{  
    class mtrk_state;

    class mtrk_objects
    {    
    public:
        mtrk_objects();
        virtual ~mtrk_objects();
        
        void clear();
        bool prepare(cJSON* section);

        cJSON* objects;
        int count;
    };



}

#endif
