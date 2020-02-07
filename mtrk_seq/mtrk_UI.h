#ifndef mtrk_UI_h
#define mtrk_UI_h 1

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
    namespace MTRK_UI
    {
        bool getLimitsReadoutFOV(LINK_DOUBLE_TYPE* const pThis, std::vector<MrLimitDouble>& rLimitVector, unsigned long& rulVerify, long /*lIndex*/);
        double setValueReadFOV(LINK_DOUBLE_TYPE* const pThis, double dDesiredPhaseFOV, long lIndex);
        double getValuePhaseFOV(LINK_DOUBLE_TYPE* const pThis, long lIndex);
    }
    
    class mtrkUI 
    {
    public:

        mtrkUI();
        virtual ~mtrkUI();
        NLS_STATUS registerUI (SeqLim &rSeqLim);

        UILimitedElement<LINK_DOUBLE_TYPE> m_ReadFoV;
        UILimitedElement<LINK_DOUBLE_TYPE> m_PhaseFoV;

        void test(SeqLim& rSeqLim);

    };
};

#endif
