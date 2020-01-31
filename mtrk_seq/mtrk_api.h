#ifndef mtrk_api_h
#define mtrk_api_h 1

#include "cJSON.h"

#include "mtrk_common.h"


namespace SEQ_NAMESPACE
{  
    class mtrk;

    class mtrk_sections 
    {
    public:
        mtrk_sections();

        cJSON* file;
        cJSON* settings;
        cJSON* instructions;
        cJSON* objects;
        cJSON* arrays;
        cJSON* equations;

        void clear();
        bool isComplete();
        bool load(cJSON* sequence);

        cJSON* getBlock(char* id);
    };


    class mtrk_state 
    {
    public:
        mtrk_state();

        int      counters[MTRK_DEFS_COUNTERS];
        double   floats  [MTRK_DEFS_FLOATS];
        long int clock;
        long int table_start;
        long int table_duration;

        void reset();
    };


    class mtrk_api
    {
    public:
        mtrk_api();
        virtual ~mtrk_api();

        void setParent(mtrk* parentSequence);
        mtrk* parent;

        bool loadSequence(std::string filename, bool forceLoad=false);
        void unloadSequence();

        cJSON*        sequence;
        mtrk_sections sections;
        mtrk_state    state;
        int           recursions;

        char*    loadedMeasurementID;

        bool prepare(bool isBinarySearch=false);

        bool prepareArrays();
        bool prepareObjects();
        bool prepareEquations();
        bool prepareBlocks();

        bool run();
        bool runBlock(cJSON* block);

        bool runActionLoop     (cJSON* item);
        bool runActionBlock    (cJSON* item);
        bool runActionCondition(cJSON* item);
        bool runActionInit     (cJSON* item);
        bool runActionSubmit   (cJSON* item);
        bool runActionRF       (cJSON* item);
        bool runActionADC      (cJSON* item);
        bool runActionGrad     (cJSON* item);
        bool runActionSync     (cJSON* item);
        bool runActionMark     (cJSON* item);
        bool runActionCalc     (cJSON* item);        
        bool runActionDebug    (cJSON* item);
    };

}


#endif
