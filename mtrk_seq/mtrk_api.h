#ifndef mtrk_api_h
#define mtrk_api_h 1

#include "cJSON.h"

#include "MrServers/MrMeasSrv/SeqIF/libRT/libRT.h"
#include "MrServers/MrMeasSrv/MeasUtils/NLSStatus.h"

#include "mtrk_common.h"
#include "mtrk_equations.h"
#include "mtrk_arrays.h"
#include "mtrk_objects.h"


namespace SEQ_NAMESPACE
{  
    class mtrk;

    class mtrk_sections 
    {
    public:
        mtrk_sections();
        ~mtrk_sections();

        cJSON* file;
        cJSON* settings;
        cJSON* infos;
        cJSON* instructions;
        cJSON* objects;
        cJSON* arrays;
        cJSON* equations;

        char*  loadedMeasurementID;

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
        long int tableStart;
        long int tableDuration;

        bool     isDryRun;

        void reset(bool dryRun=true);

        void updateDuration(int time);
    };


    inline void mtrk_state::updateDuration(int time)
    {
        if (time > tableDuration)
        {
            tableDuration=time;
        }
    }


    class mtrk_api
    {
    public:
        mtrk_api();
        virtual ~mtrk_api();

        void setParent(mtrk* parentSequence);
        mtrk* parent;

        bool loadSequence(std::string filename, bool forceLoad=false);
        void unloadSequence();

        cJSON*         sequence;
        mtrk_sections  sections;
        mtrk_state     state;
        mtrk_equations equations;
        mtrk_arrays    arrays;
        mtrk_objects   objects;

        int            recursions;

        bool prepare(bool isBinarySearch=false);
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

        int    getInfoInt   (char* name, int defaultValue);
        double getInfoDouble(char* name, double defaultValue);
        char*  getInfoString(char* name, char* defaultValue);
    };

}


#endif
