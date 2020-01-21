#ifndef mtrk_UI_h
#define mtrk_UI_h 1

#include "MrServers/MrImaging/seq/mtrk/mtrk.h"
#include "MrServers/MrProtSrv/MrProtocol/libUICtrl/UICtrl.h"

#ifdef WIN32
    #include "MrServers/MrProtSrv/MrProtocol/libUILink/UILinkLimited.h"
    #include "MrServers/MrProtSrv/MrProtocol/libUILink/UILinkSelection.h"
#endif

class MrProt;
class SeqLim;
class SeqExpo;
class Sequence;

namespace SEQ_NAMESPACE
{
    class mtrkUI 
    {
    public:

        mtrkUI();
        virtual ~mtrkUI();
        NLS_STATUS registerUI (SeqLim &rSeqLim);

    };
};

#endif

