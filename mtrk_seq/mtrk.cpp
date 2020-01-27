#include "MrServers/MrImaging/seq/mtrk/mtrk.h"
#include "MrServers/MrImaging/seq/mtrk/mtrk_UI.h"

#include "MrServers/MrMeasSrv/SeqIF/csequence.h"                        // Sequence enumerations
#include "MrServers/MrImaging/libSeqSysProp/SysProperties.h"            // System properties ("imprint" data)
#include "MrServers/MrImaging/ut/libsequt.h"                            // Unit Test


#define OnErrorReturn(S) if(!MrSucceeded(S)) return(S)


#ifndef SEQ_NAMESPACE
    #error SEQ_NAMESPACE not defined
#endif


#ifdef SEQUENCE_CLASS_mtrk
     SEQIF_DEFINE (SEQ_NAMESPACE::mtrk)
#endif
using namespace SEQ_NAMESPACE;

mtrk::mtrk()
            : m_dRFSpoilPhase       (0.0)
            , m_dRFSpoilIncrement   (0.0)
            , m_lCenterLine         (0)
            , m_dMinRiseTime        (100000.0)
            , m_dGradMaxAmpl        (0.0)
            , m_lLinesPerSec        (0)
			, m_lLinesToMeasure     (0)
			, m_sSRF01              ("fl_templ_ex")
            , m_sSRF01zSet          ("sSRF01zSet")
            , m_sSRF01zNeg          ("sSRF01zNeg")
            , m_sADC01              ("sADC01")
            , m_sADC01zSet          ("sADC01zSet")
            , m_sADC01zNeg          ("sADC01zNeg")
            , m_sGSliSel            ("sGSliSel")
            , m_sGSliSelReph        ("sGSliSelReph")
            , m_sGradRO             ("m_sGradRO")
            , m_sGReadDeph          ("m_sGReadDeph")
            , m_sGPhasEnc           ("sGPhasEnc")
            , m_sGPhasEncRew        ("sGPhasEncRew")
            , m_sGSpoil             ("m_sGSpoil")
            , m_sOscBit             ("m_sOscBit")
            , m_pUI                 (NULL)
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

    rSeqLim.setAllowedFrequency     (    8000000,  500000000);
    rSeqLim.setTR                   (    0,  100,    5000000,           10,    20000);
    rSeqLim.setTE                   (    0,  100,     100000,           10,    10000);
    rSeqLim.setBandWidthPerPixel    (    0,   80,        900,           10,      260);
    rSeqLim.setFlipAngle            (       10.0,       90.0,          1.0,   15.000);
    rSeqLim.setBaseResolution       (         64,        512,  SEQ::INC_64,      128);
    rSeqLim.setReadoutFOV           (        100,        500,            1,      300);
    rSeqLim.setPhaseFOV             (        100,        500,            1,      300);
    rSeqLim.setPELines              (         32,       1024,            1,      128);
    rSeqLim.setSlices               (          1,          1,            1,        1);
    rSeqLim.setSliceThickness       (      2.000,     10.000,        0.500,    5.000);

    if((MRRESULT_SEV & (lStatus = createUI(rSeqLim))) == MRRESULT_SEV) 
    {
        MRTRACE("Instantiation of MiniFlashUI class failed!");
        return lStatus;
    }

#ifdef WIN32
    if(NULL == m_pUI) 
    {
        MRTRACE("MiniFlashUI object pointer is null (creation failed probably)!");
        return ( SEQU_ERROR );
    }
    lStatus = m_pUI->registerUI(rSeqLim);
    if(MrSeverity(lStatus) != MRRESULT_SUCCESS) 
    {
        MRTRACE("Registering MiniFlashUI object failed! Errorcode: %i", lStatus);
        return lStatus;
    }

    rSeqLim.setDefaultEVAProt (_T("%SiemensEvaDefProt%\\Inline\\Inline.evp"));
#endif

    return lStatus;
}


NLSStatus mtrk::prepare(MrProt &rMrProt, SeqLim &rSeqLim, MrProtocolData::SeqExpo &rSeqExpo)
{
    mapi.prepare(rSeqLim.isContextPrepForBinarySearch());

    static const char *ptModule = {"mtrk::prepare"};
    NLS_STATUS   lStatus = SEQU__NORMAL;

    int32_t lMinRequiredTE, lMinRequiredTR, lPhaseEncTotalTime;
    double dMeasureTimeUsec = 0.0;

    m_dMinRiseTime = SysProperties::getGradMinRiseTime(rMrProt.gradSpec().mode()); // Minimum gradient rise time
    m_dGradMaxAmpl = SysProperties::getGradMaxAmpl(rMrProt.gradSpec().mode());     // Maximum gradient amplitude
                                                                                   // selected in protocol

    OnErrorReturn(rMrProt.kSpace().linesToMeasure(m_lLinesToMeasure));             // Call by non-constant reference
    m_lCenterLine  = rMrProt.kSpace().echoLine();                                  // 1/2 base resolution for symmetric PE

    dMeasureTimeUsec = (double)m_lLinesToMeasure * rMrProt.tr()[0];
    m_lLinesPerSec =  std::max<int32_t>(1,int32_t(m_lLinesToMeasure * 1000000. / dMeasureTimeUsec));
    rSeqExpo.setRelevantReadoutsForMeasTime(m_lLinesToMeasure / m_lLinesPerSec);

    m_sSRF01.setTypeExcitation       ();                                           // Resets all moments to 0 in Unit test
    m_sSRF01.setDuration             (2560);                                       // Most times are in microseconds
    m_sSRF01.setFlipAngle            (rMrProt.flipAngle());                        // Sets flip angle based on UI (in degrees)
    m_sSRF01.setInitialPhase         (0);                                          // Sets B1 orientation to 0 degrees (+x) in rotating frame 
    m_sSRF01.setThickness            (rMrProt.sliceSeries().aFront().thickness()); // Sets thickness based on UI (in mm)
    m_sSRF01.setSamples              (128);                                        // Number of complex points in waveform
    m_sSRF01.setBandwidthTimeProduct (2.70);                                       // Only sRF_PULSE_SINC objects have the BW*t attribute

    if(! m_sSRF01.prepSinc(rMrProt,rSeqExpo)) return (m_sSRF01.getNLSStatus());

    m_sADC01.setColumns (rMrProt.kSpace().getlBaseResolution());
    m_sADC01.setDwellTime (long((rMrProt.rxSpec().effDwellTime(rSeqLim.getReadoutOSFactor())[0]) + 0.5));
    m_sADC01.getMDH().setKSpaceCentreColumn((unsigned short)(rMrProt.kSpace().getlBaseResolution() / 2));

    if(!m_sGradRO.prepRO(rMrProt, static_cast<double>( m_sADC01.getDwellTime() ) )) return(m_sGradRO.getNLSStatus());
    m_sGradRO.setRampTimes(fSDSRoundUpGRT(m_dMinRiseTime * m_sGradRO.getAmplitude()));
    m_sGradRO.setDuration(fSDSRoundUpGRT((double)( m_sGradRO.getRampUpTime() + m_sADC01.getDuration() )));
    if(!m_sGradRO.prep()) return (m_sGradRO.getNLSStatus());
    if(!m_sGradRO.check()) return (m_sGradRO.getNLSStatus());

    m_sGPhasEnc.setMaxMagnitude(m_dGradMaxAmpl);     // set highest performance value (maximum allowed gradient amplitude)
    m_sGPhasEnc.setMinRiseTime(m_dMinRiseTime);      // set highest performance value (shortest allowed gradient rise time)

    if( !m_sGPhasEnc.prepPEShortestTime(rMrProt, SEQ::DIR_ASCENDING, 0.0, m_lLinesToMeasure - m_lCenterLine - 1))
        return(m_sGPhasEnc.getNLSStatus());

    if( !m_sGPhasEnc.check()) return(m_sGPhasEnc.getNLSStatus());

    lPhaseEncTotalTime = static_cast<int32_t>( m_sGPhasEnc.getTotalTime() );

    if( !m_sGPhasEnc.prepPEShortestTime(rMrProt, SEQ::DIR_ASCENDING, 0.0, -m_lCenterLine )) return(m_sGPhasEnc.getNLSStatus());
    if( !m_sGPhasEnc.check()) return(m_sGPhasEnc.getNLSStatus());
    if (lPhaseEncTotalTime > m_sGPhasEnc.getTotalTime())
    {
        if( !m_sGPhasEnc.prepPEShortestTime(rMrProt, SEQ::DIR_ASCENDING, 0.0, m_lLinesToMeasure - m_lCenterLine - 1))
            return(m_sGPhasEnc.getNLSStatus());
    }

    m_sGPhasEncRew = m_sGPhasEnc;
    m_sGSliSel.setAmplitude(m_sSRF01.getGSAmplitude());
    m_sGSliSel.setRampTimes(fSDSRoundUpGRT( std::max<long>((long)(m_dMinRiseTime * m_sGSliSel.getAmplitude()), SysProperties::getCoilCtrlLead())));
    m_sGSliSel.setDuration(fSDSRoundUpGRT(m_sSRF01.getDuration() + m_sGSliSel.getRampUpTime()));

    if (!m_sGSliSel.prep())  return (m_sGSliSel.getNLSStatus());
    if (!m_sGSliSel.check()) return (m_sGSliSel.getNLSStatus());

    m_sGSliSel.setStartTime(0);

    m_sGSliSelReph.setMaxMagnitude(m_dGradMaxAmpl);
    m_sGSliSelReph.setMinRiseTime (m_dMinRiseTime);
    if (!m_sGSliSelReph.prepSymmetricTOTShortestTime(-m_sGSliSel.getMomentum(m_sGSliSel.getDuration() - m_sSRF01.getDuration() / 2,
        m_sGSliSel.getTotalTime())))
        return (m_sGSliSelReph.getNLSStatus());

    m_sGReadDeph.setMaxMagnitude(m_dGradMaxAmpl);
    m_sGReadDeph.setMinRiseTime (m_dMinRiseTime);
    if (!m_sGReadDeph.prepSymmetricTOTShortestTime(-m_sGradRO.getMomentum(0 , m_sGradRO.getRampUpTime() + (long)m_sADC01.getDuration() / 2)))
        return (m_sGReadDeph.getNLSStatus());

    m_sGSpoil.setMaxMagnitude(m_dGradMaxAmpl);
    m_sGSpoil.setMinRiseTime (m_dMinRiseTime);
    if(!m_sGSpoil.prepSymmetricTOTShortestTime(m_sGSliSel.getMomentum(0, m_sGSliSel.getDuration() - m_sSRF01.getDuration() / 2 ))) 
        return (m_sGSpoil.getNLSStatus());

    lMinRequiredTE = static_cast<int32_t>( m_sSRF01.getDuration()/2 + m_sGReadDeph.getTotalTime() + m_sGradRO.getRampUpTime()
        + m_sADC01.getRoundedDuration()/2 );

    lMinRequiredTE =  static_cast<int32_t>( std::max<long>(lMinRequiredTE, m_sSRF01.getDuration() / 2 + m_sGPhasEnc.getTotalTime()
        + m_sADC01.getRoundedDuration()/2) );

    lMinRequiredTE =  std::max<int32_t>(lMinRequiredTE, static_cast<int32_t>( m_sSRF01.getDuration() / 2 + m_sGSliSel.getRampDownTime()
        + m_sGSliSelReph.getTotalTime() + m_sADC01.getRoundedDuration() / 2) );

    if (lMinRequiredTE >(rMrProt.te()[0])) return SBB_NEGATIV_TEFILL ;

    m_sGradRO.setStartTime(fSDSRoundUpGRT(m_sGSliSel.getDuration() - m_sSRF01.getDuration() / 2 + rMrProt.te()[0]
        - m_sADC01.getRoundedDuration() / 2 - m_sGradRO.getRampUpTime()));

    m_sADC01.setStartTime(m_sGradRO.getStartTime() + m_sGradRO.getRampUpTime());

    lMinRequiredTR = (int32_t)(m_sGSliSel.getDuration() - m_sSRF01.getDuration() / 2 ) + rMrProt.te()[0] + int32_t(m_sADC01.getDuration()/2)
        +  std::max<int32_t>((int32_t)m_sGPhasEncRew.getTotalTime(), (int32_t)m_sGSpoil.getTotalTime());
    if (lMinRequiredTR > rMrProt.tr()[0]) return SBB_NEGATIV_TRFILL ;

    m_sOscBit.setCode(SYNCCODE_OSC0);
    m_sOscBit.setDuration(10);

    OnErrorReturn(fSSLSetRxGain(K_RX_GAIN_CODE_HIGH, rMrProt, rSeqLim));
    OnErrorReturn(fSUPrepSlicePosArray (rMrProt, rSeqLim, m_asSLC));

    fSUSetSequenceString               ("fl", rMrProt, rSeqExpo);

    rSeqExpo.setRFInfo                (m_lLinesToMeasure * m_sSRF01.getRFInfo());
    rSeqExpo.setMeasureTimeUsec       (dMeasureTimeUsec);
    rSeqExpo.setTotalMeasureTimeUsec  (dMeasureTimeUsec);
    rSeqExpo.setMeasuredPELines       (m_lLinesToMeasure);
    rSeqExpo.setOnlineFFT             (SEQ::ONLINE_FFT_PHASE);
    rSeqExpo.setICEProgramFilename    ("%SiemensIceProgs%\\IceProgram2D");

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
        OnErrorReturn(runKernel(rMrProt, rSeqLim, rSeqExpo, KERNEL_CHECK, 0, 0, alLCk[lL]));
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

    int32_t lLine;
    int32_t lCurrKernelCalls = 0;

    OnErrorReturn(fSBBMeasRepetDelaysRun (rMrProt, rSeqLim, rSeqExpo, 0));

    m_sADC01.getMDH().addToEvalInfoMask(MDH_ONLINE);
    m_sADC01.getMDH().setKSpaceCentreLineNo((unsigned short)rMrProt.kSpace().echoLine());
    m_sADC01.getMDH().setKSpaceCentrePartitionNo(0);

    if(IS_UNIT_TEST_ACTIVE(rSeqLim))
    {
        mSEQTest (rMrProt, rSeqLim, rSeqExpo, RTEB_ClockInitTR, 0, 0, m_asSLC[0].getSliceIndex(), 0, 0);
    }

    for (lLine = 0; lLine < m_lLinesToMeasure; lLine++)
    {
        lCurrKernelCalls ++;
        if(!(lCurrKernelCalls % m_lLinesPerSec)) m_sADC01.setRelevantForMeasTime();

        m_sADC01.getMDH().setFirstScanInSlice(lLine == 0);
        m_sADC01.getMDH().setLastScanInSlice (lLine == m_lLinesToMeasure - 1);
        m_sADC01.getMDH().setLastScanInConcat(lLine == m_lLinesToMeasure - 1);
        m_sADC01.getMDH().setLastScanInMeas  (lLine == m_lLinesToMeasure - 1);

        OnErrorReturn(runKernel(rMrProt, rSeqLim, rSeqExpo, KERNEL_IMAGE, 0, 0, lLine));
    }

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

    if(!m_sGPhasEnc.prepPE(rMrProt, lLine - m_lCenterLine))    return (m_sGPhasEnc.getNLSStatus());
    if(!m_sGPhasEncRew.prepPE(rMrProt, m_lCenterLine - lLine)) return (m_sGPhasEncRew.getNLSStatus());

    m_sADC01.getMDH().setClin   ((unsigned short) lLine);
    m_sADC01.getMDH().setPhaseFT(lLine == m_lLinesToMeasure - 1);

    m_sSRF01zSet.prepSet(m_asSLC[0], m_sSRF01);
    m_sSRF01zNeg.prepNeg(m_asSLC[0], m_sSRF01);

    m_sADC01zSet.prepSet(m_asSLC[0], m_sADC01, m_sGradRO, lLine - m_lCenterLine, 0);
    m_sADC01zNeg.prepNeg(m_asSLC[0], m_sADC01, m_sGradRO, lLine - m_lCenterLine, 0);

    m_dRFSpoilIncrement += RFSPOIL_INCREMENTdeg;
    m_dRFSpoilPhase     += m_dRFSpoilIncrement;
    m_dRFSpoilPhase      = fmod(m_dRFSpoilPhase,     (double) RFMAXPHASEdeg);
    m_dRFSpoilIncrement  = fmod(m_dRFSpoilIncrement, (double) RFMAXPHASEdeg);

    m_sSRF01zSet.increasePhase(m_dRFSpoilPhase);
    m_sSRF01zNeg.decreasePhase(m_dRFSpoilPhase);
    m_sADC01zSet.increasePhase(m_dRFSpoilPhase);
    m_sADC01zNeg.decreasePhase(m_dRFSpoilPhase);

    fRTEBInit(m_asSLC[0].getROT_MATRIX());
    // - **************************************** S E Q U E N C E   T I M I N G ******************************************
    // - *           Start Time    |    NCO    |   SRF   |   ADC   |            Gradient Events            |   Sync
    // - *             (usec)      |   Event   |  Event  |  Event  |    phase   |   read     |    slice    |   Event
    // - *****************************************************************************************************************
    fRTEI(                        0,          0,        0,        0,            0,            0,  &m_sGSliSel,&m_sOscBit);

    fRTEI(m_sGSliSel.getDuration()
        - m_sSRF01.getDuration() ,&m_sSRF01zSet,&m_sSRF01,        0,            0,            0,            0,         0);

    fRTEI(m_sGSliSel.getDuration(),&m_sSRF01zNeg,      0,         0,&m_sGPhasEnc,&m_sGReadDeph,             0,         0);

    fRTEI(m_sGSliSel.getTotalTime() ,          0,      0,         0,            0,            0,&m_sGSliSelReph,       0);

    fRTEI(m_sGradRO.getStartTime()  ,          0,      0,         0,            0,   &m_sGradRO,            0,         0);

    fRTEI(m_sADC01.getStartTime()   ,&m_sADC01zSet,    0, &m_sADC01,            0,            0,            0,         0);
    fRTEI(m_sADC01.getStartTime() 
        + m_sADC01.getRoundedDuration(),&m_sADC01zNeg, 0,         0,            0,            0,            0,         0);

    fRTEI(m_sGradRO.getStartTime()
        + m_sGradRO.getDuration()   ,        0,        0,         0,&m_sGPhasEncRew,          0,  &m_sGSpoil,          0);

    fRTEI(rMrProt.tr()[0]          ,         0,        0,         0,            0,            0,            0,         0);


    if(IS_UNIT_TEST_ACTIVE(rSeqLim))
    {
        if (lKernelMode == KERNEL_CHECK)
            mSEQTest(rMrProt, rSeqLim, rSeqExpo, RTEB_ORIGIN_fSEQCheck,     10, lLine, m_asSLC[0].getSliceIndex(), 0, 0);
        else
            mSEQTest(rMrProt, rSeqLim, rSeqExpo, RTEB_ORIGIN_fSEQRunKernel, 10, lLine, m_asSLC[0].getSliceIndex(), 0, 0);

        mSEQTest(rMrProt, rSeqLim, rSeqExpo, RTEB_ClockCheck, 10, lLine, m_asSLC[0].getSliceIndex(), 0, 0);
    }

    OnErrorReturn(fRTEBFinish());

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
