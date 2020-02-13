#ifndef mtrk_objects_h
#define mtrk_objects_h 1

#include "cJSON.h"

#include "MrServers/MrMeasSrv/SeqIF/libRT/libRT.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sREADOUT.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sRF_PULSE.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sGRAD_PULSE.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sSYNC.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sFREQ_PHASE.h"
#include "MrServers/MrMeasSrv/MeasUtils/NLSStatus.h"


namespace SEQ_NAMESPACE
{  
    class mtrk_state;

    class mtrk_object
    {
    public:
        enum {
            INVALID=-1,
            GRAD=0,
            RF=1,
            ADC=2,
            SYNC=3
        };

        enum {
            SYNC_INVALID=0,
            SYNC_OSC,
            SYNC_EXTTRIGGER
        };

        mtrk_object();
        virtual ~mtrk_object();
        void clear();

        bool prepare(cJSON* entry);

        int type;
        int duration;
        int syncClass;

        sGRAD_PULSE_ARB* eventGrad;
        sSYNC*           eventSync;
        sREADOUT*        eventADC;
        sRF_PULSE_ARB*   eventRF;
        sFREQ_PHASE*     eventNCOSet;
        sFREQ_PHASE*     eventNCOReset;
        
        cJSON* object;

        //bool insert(cJSON* item);
        //int  getDuration(bool includeOverhang);    
    };


    class mtrk_objects
    {    
    public:
        mtrk_objects();
        virtual ~mtrk_objects();
        
        void clear();
        bool prepare(cJSON* section);

        mtrk_object* getObject(char* name);
        mtrk_object* getObject(int index);

        mtrk_object** eventObjects;
        cJSON* objects;
        int count;
    };

}

#endif
