#ifndef mtrk_h
#define mtrk_h 1

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

#include "MrCommon/MrGlobalDefinitions/ImpExpCtrl.h"

#include "mtrk_api.h"


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

        const mtrkUI* getUI (void) const;

        mtrk_api mapi;

        /*
        double m_dRFSpoilPhase;
        double m_dRFSpoilIncrement;
        int32_t m_lCenterLine;
        double m_dMinRiseTime;
        double m_dGradMaxAmpl;
        int32_t m_lLinesPerSec;
        int32_t m_lLinesToMeasure;
        */

        sSLICE_POS       m_asSLC[K_NO_SLI_MAX];

        /*
        sRF_PULSE_SINC   m_sSRF01;
        sFREQ_PHASE      m_sSRF01zSet;
        sFREQ_PHASE      m_sSRF01zNeg;
        sREADOUT         m_sADC01;
        sFREQ_PHASE      m_sADC01zSet;
        sFREQ_PHASE      m_sADC01zNeg;
        sGRAD_PULSE      m_sGSliSel;
        sGRAD_PULSE      m_sGSliSelReph;
        sGRAD_PULSE_RO   m_sGradRO;
        sGRAD_PULSE      m_sGReadDeph;
        sGRAD_PULSE_PE   m_sGPhasEnc;
        sGRAD_PULSE_PE   m_sGPhasEncRew;
        sGRAD_PULSE      m_sGSpoil;
        sSYNC_OSC        m_sOscBit;
        */

        mtrkUI* m_pUI;
        NLS_STATUS createUI (SeqLim &rSeqLim);

        template< class TYPE > void UnusedArg (TYPE Argument) const { if( false ) { TYPE Dummy; Dummy = Argument; } };

    private:
        mtrk (const mtrk &right);
        mtrk & operator=(const mtrk &right);
    };
};    

#endif
