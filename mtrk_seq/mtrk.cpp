#include "MrServers/MrImaging/seq/mtrk/mtrk.h"
#include "MrServers/MrImaging/seq/mtrk/mtrk_UI.h"

#include "MrServers/MrMeasSrv/SeqIF/csequence.h"
#include "MrServers/MrImaging/libSeqSysProp/SysProperties.h"
#include "MrServers/MrImaging/ut/libsequt.h"

#define OnErrorReturn(S) if(!MrSucceeded(S)) return(S)

#ifndef SEQ_NAMESPACE
    #error SEQ_NAMESPACE not defined
#endif
#ifdef SEQUENCE_CLASS_mtrk
     SEQIF_DEFINE (SEQ_NAMESPACE::mtrk)
#endif
using namespace SEQ_NAMESPACE;


mtrk::mtrk(): m_pUI(NULL)      
{
    mapi.setParent(this);
}


mtrk::~mtrk()
{
    if(NULL != m_pUI)
    {
        delete m_pUI;
        m_pUI = NULL;
    }
}


NLSStatus mtrk::initialize(SeqLim &rSeqLim)
{
    static const char *ptModule = {"mtrk::initialize"};
    NLS_STATUS lStatus = SEQU__NORMAL;

    rSeqLim.setAllowedFrequency(8000000, 500000000);
    rSeqLim.enableSliceShift();
    rSeqLim.enableMSMA();
    rSeqLim.enableOffcenter();
    rSeqLim.setAllowedSliceOrientation(SEQ::DOUBLE_OBLIQUE);   
    rSeqLim.setReadoutFOV(100, 500, 1, 300);
    rSeqLim.setPhaseFOV(100, 500, 1, 300);
    rSeqLim.setSlices(1, K_NO_SLI_MAX, 1, 1);
    rSeqLim.setMultipleSeriesMode(SEQ::MULTIPLE_SERIES_OFF, SEQ::MULTIPLE_SERIES_EACH_MEASUREMENT, SEQ::MULTIPLE_SERIES_EACH_SLICE, SEQ::MULTIPLE_SERIES_EACH_SLICE_AND_MEASUREMENT);
    rSeqLim.setAdjShim(SEQ::ADJSHIM_STANDARD, SEQ::ADJSHIM_TUNEUP);
    rSeqLim.setReadoutOSFactor(2.0);

    if((MRRESULT_SEV & (lStatus = createUI(rSeqLim))) == MRRESULT_SEV) 
    {
        MRTRACE("Instantiation of UI class failed!");
        return lStatus;
    }

#ifdef WIN32
    if(NULL == m_pUI) 
    {
        MRTRACE("UI object pointer is null (creation failed probably)!");
        return ( SEQU_ERROR );
    }
    lStatus = m_pUI->registerUI(rSeqLim);
    if(MrSeverity(lStatus) != MRRESULT_SUCCESS) 
    {
        MRTRACE("Registering UI object failed! Errorcode: %i", lStatus);
        return lStatus;
    }

    rSeqLim.setDefaultEVAProt (_T("%SiemensEvaDefProt%\\Inline\\Inline.evp"));
#endif

    return lStatus;
}


NLSStatus mtrk::prepare(MrProt &rMrProt, SeqLim &rSeqLim, MrProtocolData::SeqExpo &rSeqExpo)
{
    static const char *ptModule = {"mtrk::prepare"};
    NLS_STATUS   lStatus = SEQU__NORMAL;

    mapi.prepare(&rMrProt,&rSeqExpo,rSeqLim.isContextPrepForBinarySearch());

#ifdef WIN32
    //if (!rSeqLim.isContextPrepForBinarySearch())
    {
        Slice slice(rMrProt.sliceSeries()[0]);
        slice.readoutFOV(mapi.getInfoDouble(MTRK_INFOS_FOV,300.));
        slice.phaseFOV(mapi.getInfoDouble(MTRK_INFOS_FOV,300.));
       // rMrProt.sliceGroupList().;
    }
#endif   

    int lLinesToMeasure=0;

    OnErrorReturn(fSSLSetRxGain(K_RX_GAIN_CODE_HIGH, rMrProt, rSeqLim));
    OnErrorReturn(fSUPrepSlicePosArray (rMrProt, rSeqLim, m_asSLC));
    fSUSetSequenceString(mapi.getInfoString(MTRK_INFOS_SEQSTRING,"MTRK"), rMrProt, rSeqExpo);
    rSeqExpo.setRFInfo              (mapi.getRFInfo());
    rSeqExpo.setMeasureTimeUsec     (mapi.getMeasureTimeUsec());
    rSeqExpo.setTotalMeasureTimeUsec(mapi.getMeasureTimeUsec());
    rSeqExpo.setMeasuredPELines     (mapi.getInfoInt(MTRK_INFOS_PELINES,128));
    rSeqExpo.setOnlineFFT           (SEQ::ONLINE_FFT_PHASE);
    rSeqExpo.setICEProgramFilename  (mapi.getInfoString(MTRK_INFOS_RECONSTRUCTION,"%SiemensIceProgs%\\IceProgram2D"));
    rSeqLim.setReadoutOSFactor      (mapi.getReadoutOS());

    return (lStatus);
}


NLSStatus mtrk::check(MrProt &rMrProt, SeqLim &rSeqLim, MrProtocolData::SeqExpo &rSeqExpo, SEQCheckMode *)
{
    static const char *ptModule = {"mtrk::check"};
    NLS_STATUS   lStatus = SEQU__NORMAL;

    int lL       = 0;
    int alLCk[4] = {0, 1, rSeqExpo.getMeasuredPELines() - 2, rSeqExpo.getMeasuredPELines() - 1};

    while (lL < 4 )
    {
        //OnErrorReturn(runKernel(rMrProt, rSeqLim, rSeqExpo, KERNEL_CHECK, 0, 0, alLCk[lL]));
        lL++;
    }

    return(lStatus);
}


NLSStatus mtrk::run(MrProt  &rMrProt, SeqLim &rSeqLim, MrProtocolData::SeqExpo &rSeqExpo)
{
    static const char *ptModule = {"mtrk::run"};
    NLS_STATUS lStatus          = SEQU__NORMAL;

    if(IS_UNIT_TEST_ACTIVE(rSeqLim))
    {
        mSEQTest(rMrProt, rSeqLim, rSeqExpo, RTEB_ORIGIN_fSEQRunStart, 0, 0, 0, 0, 0);
    }

    mapi.run(&rMrProt,&rSeqExpo);

    if(IS_UNIT_TEST_ACTIVE(rSeqLim))
    {
        mSEQTest(rMrProt, rSeqLim, rSeqExpo, RTEB_ORIGIN_fSEQRunFinish, 0, 0, 0, 0, 0);
    }

    return(lStatus);
}


NLS_STATUS mtrk::runKernel(MrProt &rMrProt, SeqLim &rSeqLim,  MrProtocolData::SeqExpo &rSeqExpo,
                                long lKernelMode, long /* m_lSlice */, long /* m_lPartition */, long lLine)
{
    static const char *ptModule = {"mtrk::runKernel"};
    NLS_STATUS lStatus  = SEQU__NORMAL;

    return(lStatus);
}


NLS_STATUS mtrk::createUI (SeqLim&)
{
#ifdef WIN32
    static const char *ptModule = {"mtrk::createUI"};

    if(m_pUI)  
    {
        delete m_pUI;
        m_pUI = NULL;
    }

    try 
    {
        m_pUI = new mtrkUI();
    }
    catch (...) 
    {
        delete m_pUI;
        m_pUI = NULL;

        TRACE_PUT1(TC_ALWAYS, TF_SEQ,"%s: Cannot instantiate UI class !", ptModule);
        return ( SEQU_ERROR );
    }
#endif
    return ( SEQU_NORMAL );
}  


const mtrkUI* mtrk::getUI (void) const
{
    return ( m_pUI );
}
