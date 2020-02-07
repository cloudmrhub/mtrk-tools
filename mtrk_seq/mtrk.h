#ifndef mtrk_h
#define mtrk_h 1

#define MTRK_SEQ_LABEL "MTRK Driver Sequence v 0.1a"

#include "MrServers/MrImaging/libSBB/StdSeqIF.h"
#include "MrServers/MrImaging/libSeqUtil/libSeqUtil.h"
#include "MrServers/MrMeasSrv/SeqFW/libGSL/libGSL.h"
#include "MrServers/MrMeasSrv/SeqFW/libSSL/libSSL.h"
#include "MrServers/MrImaging/libSBB/libSBBmsg.h"
#include "MrServers/MrProtSrv/MrProt/KSpace/MrKSpace.h"
#include "MrServers/MrProtSrv/MrProt/MeasParameter/MrSysSpec.h"
#include "MrServers/MrProtSrv/MrProt/MeasParameter/MrRXSpec.h"
#include "MrServers/MrProtSrv/MrProt/MrProt.h"
#include "ProtBasic/Interfaces/SeqLim.h"
#include "MrServers/MrProtSrv/MrProt/SeqIF/SeqExpo.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sREADOUT.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sGRAD_PULSE.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sRF_PULSE.h"
#include "MrServers/MrMeasSrv/SeqIF/libRT/sFREQ_PHASE.h"
#include "MrCommon/MrGlobalDefinitions/MrResult.h"
#include "MrServers/MrMeasSrv/SeqIF/Sequence/sequmsg.h"

#ifdef WIN32
    #include "TCHAR.h"
#endif

#ifdef BUILD_SEQU
    #define __OWNER
#endif

#include "mtrk_api.h"

#include "MrCommon/MrGlobalDefinitions/ImpExpCtrl.h"

class MrProt;
class SeqLim;
class SeqExpo;
class Sequence;

namespace SEQ_NAMESPACE
{
    class mtrkUI;

    class __IMP_EXP mtrk : public StdSeqIF
    {
    public:
        mtrk();
        ~mtrk();
        NLSStatus initialize(SeqLim& rSeqLim);
        NLSStatus prepare(MrProt& rMrProt, SeqLim& rSeqLim, MrProtocolData::SeqExpo& rSeqExpo);
        NLSStatus check(MrProt& rMrProt, SeqLim& rSeqLim, MrProtocolData::SeqExpo& rSeqExpo, SEQCheckMode* pSEQCheckMode);
        NLSStatus run(MrProt& rMrProt, SeqLim& rSeqLim, MrProtocolData::SeqExpo& rSeqExpo);
        NLS_STATUS runKernel(MrProt& rMrProt, SeqLim& rSeqLim, MrProtocolData::SeqExpo& rSeqExpo, long lKernelMode, long lSlice, long lPartition, long lLine);

        mtrkUI* m_pUI;
        NLS_STATUS createUI (SeqLim &rSeqLim);
        const mtrkUI* getUI (void) const;

        sSLICE_POS       m_asSLC[K_NO_SLI_MAX];

        mtrk_api mapi;

        template< class TYPE > void UnusedArg (TYPE Argument) const { if( false ) { TYPE Dummy; Dummy = Argument; } };

    private:
        mtrk (const mtrk &right);
        mtrk & operator=(const mtrk &right);
    };
};    

#endif
