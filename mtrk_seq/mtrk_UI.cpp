#include "MrServers/MrMeasSrv/SeqIF/Sequence/Sequence.h"
#ifdef WIN32
    #include "MrServers/MrProtSrv/MrProtocol/UILink/MrStdNameTags.h"
#endif
#include "MrServers/MrImaging/seq/mtrk/mtrk.h"
#include "MrServers/MrImaging/seq/mtrk/mtrk_UI.h"

#ifndef SEQ_NAMESPACE
#error SEQ_NAMESPACE not defined
#endif

using namespace SEQ_NAMESPACE;


#ifdef WIN32

mtrk* getSeq (MrUILinkBase* const pThis)
{
    return ( static_cast<mtrk*>(pThis->sequence().getSeq()) );
}


const mtrkUI* getUI (MrUILinkBase* const pThis)
{
    return ( static_cast<mtrk*>(pThis->sequence().getSeq())->getUI() );
}


mtrkUI::mtrkUI()
{
}


mtrkUI::~mtrkUI()
{
}


bool MTRK_UI::getLimitsReadoutFOV(LINK_DOUBLE_TYPE* const pThis, std::vector<MrLimitDouble>& rLimitVector, unsigned long& rulVerify, long lIndex)
{
    std::cout << "UI Limit" << std::endl;

    double dMin = 380., dMax = 380., dInc = 1.;

    rulVerify = LINK_DOUBLE_TYPE::VERIFY_BINARY_SEARCH;
    rLimitVector.resize(1);
    //rLimitVector[0].setEqualSpaced(dMin,dMax,dInc);
    //rLimitVector[0].setEqualSpaced(100.,480.,1.);
    rLimitVector[0].setLonely(dMin);

/*
    LINK_DOUBLE_TYPE* pItem = _search<LINK_DOUBLE_TYPE>(pThis, MR_TAG_READOUT_FOV);

    if ( pItem != NULL )
        if (pItem->value(dMin,0) != dMin)
        {
            std::cout << "ERR" << std::endl;
            return ( 0 );
        }
*/

    return true;
}

double MTRK_UI::setValueReadFOV(LINK_DOUBLE_TYPE* const pThis, double dDesiredFOV, long lIndex)
{   
    std::cout << "Set Call " <<  dDesiredFOV << std::endl;

    dDesiredFOV=380;

    const mtrkUI* pSeqUI = static_cast<mtrk*>(pThis->sequence().getSeq())->m_pUI;
    if ( pSeqUI->m_ReadFoV.getOrigSetValueHandler() )
    {
        dDesiredFOV = ( *pSeqUI->m_ReadFoV.getOrigSetValueHandler() )(pThis, dDesiredFOV, lIndex);
    }


    double dMin = 380.;

/*
    LINK_DOUBLE_TYPE* pItem = _search<LINK_DOUBLE_TYPE>(pThis, MR_TAG_READOUT_FOV);
    if ( pItem != NULL )
        if (pItem->value(dMin,0) != dMin)
        {
            std::cout << "ERR" << std::endl;
            return ( 0 );
        }    
*/
    return dDesiredFOV;
}


NLS_STATUS mtrkUI::registerUI(SeqLim& rSeqLim)
{
    static const char * const ptModule = {"mtrkUI::registerUI"};

    std::cout << "Registering UI" << std::endl;

    m_ReadFoV.registerGetLimitsHandler(rSeqLim, MR_TAG_READOUT_FOV,MTRK_UI::getLimitsReadoutFOV);
    m_ReadFoV.registerSetValueHandler (rSeqLim, MR_TAG_READOUT_FOV,MTRK_UI::setValueReadFOV);

/*
    if( LINK_LONG_TYPE* pFOV = _search<LINK_LONG_TYPE>(rSeqLim, MR_TAG_READOUT_FOV) )
    {  
        std::cout << "GetLimits" << std::endl;
        pFOV->registerGetLimitsHandler(MTRK_UI::getLimitsReadoutFOV);  
    }
*/
    //MR_TAG_SG_SIZE

    std::cout << "Done" << std::endl;

    return ( SEQU__NORMAL );
};


void mtrkUI::test(SeqLim& rSeqLim)
{
    double val=380;

    LINK_DOUBLE_TYPE* pItem = _search<LINK_DOUBLE_TYPE>(rSeqLim, MR_TAG_READOUT_FOV);
    if ( pItem != NULL )
        if (pItem->value(val,0) != val)
        {
            std::cout << "ERR" << std::endl;
        }     
}

#endif
