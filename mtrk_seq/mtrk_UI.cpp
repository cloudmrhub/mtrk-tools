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


enum eSeqSpecialParameters 
{
    WIP_Checkbox_1 = 1, 
    WIP_Checkbox_2
};


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

    //dDesiredFOV=380;

    const mtrkUI* pSeqUI = static_cast<mtrk*>(pThis->sequence().getSeq())->m_pUI;
    if ( pSeqUI->m_ReadFoV.getOrigSetValueHandler() )
    {
        dDesiredFOV = ( *pSeqUI->m_ReadFoV.getOrigSetValueHandler() )(pThis, dDesiredFOV, lIndex);
    }


    //double dMin = 380.;

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


double MTRK_UI::getValuePhaseFOV(LINK_DOUBLE_TYPE* const pThis, long lIndex)
{   
    std::cout << "Get Call ";

    double value=0;

    const mtrkUI* pSeqUI = static_cast<mtrk*>(pThis->sequence().getSeq())->m_pUI;
    if ( pSeqUI->m_PhaseFoV.getOrigGetValueHandler() )
    {
        value = ( *pSeqUI->m_PhaseFoV.getOrigGetValueHandler() )(pThis, lIndex);
    }    
/*
    if ( pSeqUI->m_ReadFoV.getOrigSetValueHandler() )
    {
        ( *pSeqUI->m_ReadFoV.getOrigSetValueHandler() )(pThis, 380., lIndex);
    }
*/
    return value;
}



unsigned wipCheckboxGetToolTipId(LINK_BOOL_TYPE* const pThis, char* arg_list[], long lIndex)
{
    static char tLine    [100];
    static char tToolTip[1000];
    MrProt rMrProt (pThis->prot());

    const mtrk* pSeq = static_cast<mtrk*>(pThis->sequence().getSeq());

    tToolTip[0] = '\0';
    std::string fname=pSeq->mapi.sections.loadedFilename;

    switch (lIndex)
    {
    case WIP_Checkbox_1 :
        sprintf(tLine,"Loaded File: %s",fname.c_str()); strcat(tToolTip,tLine);
        arg_list[0] = tToolTip;
        return MRI_STD_STRING;
        break;

    default : break;
    }

    return 0;
}


unsigned wipCheckboxGetLabelId(LINK_BOOL_TYPE* const, char* arg_list[], long lIndex)
{
    static const char* const pszLabel0 = MTRK_SEQ_LABEL;

    switch(lIndex)
    {
    case WIP_Checkbox_1: 
        arg_list[0] = (char*)pszLabel0   ; break;
    default: 
        break;
    }
    return MRI_STD_STRING;
}


bool wipCheckboxGetOptions(LINK_BOOL_TYPE* const /*pThis*/ , std::vector<unsigned>& rOptionVector, unsigned long& rulVerify, long /*lIndex*/)
{
    rulVerify = LINK_BOOL_TYPE::VERIFY_ON;
    rOptionVector.resize(2);
    rOptionVector[0] = false;
    rOptionVector[1] = true;
    return true;
}


bool wipCheckboxGetValue(LINK_BOOL_TYPE* const pThis , long lIndex)
{
    return false;
}


bool wipCheckboxSetValue(LINK_BOOL_TYPE* const pThis, bool value, long lIndex)
{
    return true;
}


NLS_STATUS mtrkUI::registerUI(SeqLim& rSeqLim)
{
    static const char * const ptModule = {"mtrkUI::registerUI"};

    //m_ReadFoV.registerGetLimitsHandler(rSeqLim, MR_TAG_READOUT_FOV,MTRK_UI::getLimitsReadoutFOV);
    //m_ReadFoV.registerSetValueHandler (rSeqLim, MR_TAG_READOUT_FOV,MTRK_UI::setValueReadFOV);
    //m_PhaseFoV.registerGetValueHandler(rSeqLim, MR_TAG_PHASE_FOV,MTRK_UI::getValuePhaseFOV);

    //MR_TAG_SG_SIZE

    if (LINK_BOOL_TYPE* pBool = _create< LINK_BOOL_TYPE >(rSeqLim, MR_TAG_SEQ_WIP1, WIP_Checkbox_1))
    {       
        pBool->registerGetLabelIdHandler  (wipCheckboxGetLabelId);
        pBool->registerGetToolTipIdHandler(wipCheckboxGetToolTipId);
        pBool->registerGetOptionsHandler  (wipCheckboxGetOptions);
        pBool->registerGetValueHandler    (wipCheckboxGetValue);
        pBool->registerSetValueHandler    (wipCheckboxSetValue);        
    }

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
