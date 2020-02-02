#include "mtrk_common.h"
#include "mtrk_arrays.h"
#include "mtrk_api.h"


using namespace SEQ_NAMESPACE;

mtrk_objects::mtrk_objects()
{
    objects=0;
    count=0;    
}


mtrk_objects::~mtrk_objects()
{
    clear();
}


void mtrk_objects::clear()
{
    // TODO
}


bool mtrk_objects::prepare(cJSON* section)
{
    // TODO
    objects=section;

    return true;
}

