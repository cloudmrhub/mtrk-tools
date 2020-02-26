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

        char*       loadedMeasurementID;
        std::string loadedFilename;

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
        void updateDuration(int startTime, int duration=0);

        long int                      totalDuration;
        MrProtocolData::SeqExpoRFInfo rfInfo;       
    };


    inline void mtrk_state::updateDuration(int startTime, int duration)
    {
        int endTime=startTime + duration;
        
        if (endTime > tableDuration)
        {
            tableDuration=endTime;
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

        bool prepare(MrProt* pMrProt, MrProtocolData::SeqExpo* pSeqExpo, bool isBinarySearch=false);
        bool prepareBlocks();

        bool run(MrProt* pMrProt, MrProtocolData::SeqExpo* pSeqExpo, bool isDryRun=false);
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
        double getMeasureTimeUsec();
        MrProtocolData::SeqExpoRFInfo getRFInfo();

        MrProt*                  ptrMrProt; 
        MrProtocolData::SeqExpo* ptrSeqExpo;
    };
}


#endif
