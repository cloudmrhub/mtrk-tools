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


NLS_STATUS mtrkUI::registerUI (SeqLim & /*rSeqLim*/)
{
    static const char * const ptModule = {"mtrkUI::registerUI"};
    return ( SEQU__NORMAL );
};

#endif
