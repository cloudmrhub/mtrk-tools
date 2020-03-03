#include "mtrk_common.h"
#include "mtrk_arrays.h"
#include "mtrk_api.h"


#include "MrServers/MrMeasSrv/SeqIF/libRT/libRT.h"
#include "MrServers/MrMeasSrv/MeasUtils/NLSStatus.h"
#include "MrServers/MrProtSrv/MrProt/MrProt.h"
#include "MrServers/MrImaging/libSeqUtil/libSeqUtil.h"
#include "MrServers/MrMeasSrv/MeasNuclei/IF/MeasKnownNuclei.h"

using namespace SEQ_NAMESPACE;

mtrk_api* mapiInstance=0;


mtrk_objects::mtrk_objects()
{
    objects=0;
    count=0;    
    eventObjects=0;
}


mtrk_objects::~mtrk_objects()
{
    clear();
}


void mtrk_objects::setMapiInstance(mtrk_api* pointer)
{
    mapiInstance=pointer;
}


void mtrk_objects::clear()
{
    if (eventObjects!=0)
    {
        for (int i=0; i<count; i++)
        {
            if (eventObjects[i]!=0)
            {
                delete eventObjects[i];
                eventObjects[i]=0;
            }
        }

        delete[] eventObjects;
        eventObjects=0; 
    }
    objects=0;    
    count=0;
}


bool mtrk_objects::prepare(cJSON* section)
{
    MTRK_LOG("Preparing Objects")
    clear();

    cJSON* entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        count++;
    }        
    
    MTRK_LOG("Found objects: " << count)

    eventObjects=new mtrk_object*[count];
    for (int i=0; i<count; i++)
    {
        eventObjects[i]=new mtrk_object();
    }

    MTRK_LOG("Pointers prepared")

    int index=0;
    entry=0;
    cJSON_ArrayForEach(entry, section)
    {
        MTRK_LOG("Preparing object " << index)    
        eventObjects[index]->prepare(entry);       
        cJSON_AddNumberToObject(entry, MTRK_PROPERTIES_MEMINDEX, index);
        index++;
    }    

    MTRK_LOG("Objects: " << count)
    objects=section;
    return true;
}


mtrk_object* mtrk_objects::getObject(char* name)
{
    cJSON* object = cJSON_GetObjectItemCaseSensitive(objects, name);
    if (object==NULL)
    {
        return NULL;
    }
    cJSON* indexItem = cJSON_GetObjectItemCaseSensitive(object, MTRK_PROPERTIES_MEMINDEX);
    if (indexItem==NULL)
    {
        return NULL;
    }
    return getObject(indexItem->valueint);
}


mtrk_object* mtrk_objects::getObject(int index)
{
    if ((index < 0) || (index >= count))
    {
        return NULL;
    }
    return eventObjects[index];
}


mtrk_object::mtrk_object()
{
    type=INVALID;
    syncClass=SYNC_INVALID;
    duration=0;
    tailDuration=0;

    eventGrad=0;
    eventSync=0;
    eventADC=0;
    eventRF=0;
    eventNCOSet=0;
    eventNCOReset=0;

    object=0;
}


mtrk_object::~mtrk_object()
{
    clear();
}


void mtrk_object::clear()
{
    MTRK_LOG("Object destructor")

    MTRK_DELETE(eventGrad)
    MTRK_DELETE(eventSync)
    MTRK_DELETE(eventADC)
    MTRK_DELETE(eventRF)
    MTRK_DELETE(eventNCOSet)
    MTRK_DELETE(eventNCOReset)

    object=0;
    type=INVALID;
    syncClass=SYNC_INVALID;
    duration=0;    
}


bool mtrk_object::prepare(cJSON* entry)
{
    MTRK_GETITEM(entry, MTRK_PROPERTIES_TYPE, objectType)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_DURATION, objectDuration)    
    duration=objectDuration->valueint;

    if (strcmp(objectType->valuestring, MTRK_ACTIONS_RF)==0)
    {    
        MTRK_LOG("Preparing RF")
        MTRK_RETONFAILMSG(prepareRF(entry),"ERROR: Preparing RF object failed " << entry->string)
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_ADC)==0)
    {    
        MTRK_LOG("Preparing ADC")
        MTRK_RETONFAILMSG(prepareADC(entry),"ERROR: Preparing ADC object failed " << entry->string)
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_GRAD)==0)
    {    
        MTRK_LOG("Preparing GRAD")
        MTRK_RETONFAILMSG(prepareGrad(entry),"ERROR: Preparing Grad object failed " << entry->string)
    }   
    else
    if (strcmp(objectType->valuestring, MTRK_ACTIONS_SYNC)==0)
    {    
        MTRK_LOG("Preparing SYNC")
        MTRK_RETONFAILMSG(prepareSync(entry),"ERROR: Preparing sybc object failed " << entry->string)
    }      

    object=entry;
    return true;
}


bool mtrk_object::prepareRF(cJSON* entry)
{
    type=RF;    
    MTRK_GETITEM(entry, MTRK_PROPERTIES_FLIPANGLE, flipAngle)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_THICKNESS, thickness)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_INITIAL_PHASE, initialPhase)           
    MTRK_GETITEM(entry, MTRK_PROPERTIES_ARRAY, arrayName)
    MTRK_GETITEMOPT(entry, MTRK_PROPERTIES_PURPOSE, purpose)    

    mtrk_array* array=mapiInstance->arrays.getArray(arrayName->valuestring);

    if (array==0)
    {
        MTRK_LOG("ERROR: Array not found " << arrayName->valuestring)
        return false;
    }
    if (array->type!=mtrk_array::COMPLEX_FLOAT)
    {
        MTRK_LOG("ERROR: Invalid type of array " << arrayName->valuestring)
        return false;
    }

    double realAmpl = 0.; 
    double imagAmpl = 0.;    

    for (int i=0; i<array->size; i++)
    {  
        realAmpl += array->getAbsolute(i) * cos(array->getPhase(i));   
        imagAmpl += array->getAbsolute(i) * sin(array->getPhase(i));  
    } 

    double effectiveAmplIntegral = sqrt(realAmpl*realAmpl + imagAmpl*imagAmpl);

    eventRF=new sRF_PULSE_ARB();    
    eventRF->setIdent(entry->string);
    eventRF->setDuration(duration);
    eventRF->setFlipAngle(flipAngle->valuedouble);
    eventRF->setInitialPhase(initialPhase->valuedouble);
    eventRF->setThickness(thickness->valuedouble);
    eventRF->setSamples(array->size);

    if (purpose!=NULL)
    {
        if (strcmp(purpose->valuestring, MTRK_OPTIONS_EXCITATION)==0)
        {
            eventRF->setTypeExcitation();
        }        
        else
        if (strcmp(purpose->valuestring, MTRK_OPTIONS_REFOCUS)==0)
        {
            eventRF->setTypeRefocussing();
        }        
    }

    if (!eventRF->prepArbitrary(mapiInstance->ptrMrProt->getProtData(), mapiInstance->ptrSeqExpo, (sSample*) array->data, effectiveAmplIntegral))  
    {   
        MTRK_LOG("ERROR: Preparing RF pulse " << entry->string << " Reason: " << eventRF->getNLSStatus())
        return false;  
    };

    char* buffer=0;
    buffer=new char[1024];

    strcpy(buffer,entry->string);
    strcat(buffer,"_NCOSet");
    eventNCOSet=new sFREQ_PHASE();
    eventNCOSet->setIdent(buffer);
    eventNCOSet->setFrequency(0.);
    eventNCOSet->setPhase(0.);

    strcpy(buffer,entry->string);
    strcat(buffer,"_NCOReset");
    eventNCOReset=new sFREQ_PHASE();
    eventNCOReset->setIdent(buffer);
    eventNCOReset->setFrequency(0.);
    eventNCOReset->setPhase(0.);

    MTRK_DELETE(buffer)

    return true;

    //For later update: eventRF->prep(mapiInstance->ptrMrProt->getProtData(), mapiInstance->ptrSeqExpo);    
}


bool mtrk_object::prepareADC(cJSON* entry)
{
    type=ADC;

    MTRK_GETITEM(entry, MTRK_PROPERTIES_SAMPLES, samples)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_DWELLTIME, dwelltime)
  
    eventADC=new sREADOUT();
    eventADC->setIdent(entry->string);
    eventADC->setColumns(samples->valueint);
    eventADC->setDwellTime(dwelltime->valueint);

    eventADC->getMDH().setCslc(0);
    eventADC->getMDH().setCacq(0);
    eventADC->getMDH().setCpar(0);
    eventADC->getMDH().setCseg(0);
    eventADC->getMDH().setCeco(0);
    eventADC->getMDH().setClin(0);
    eventADC->getMDH().setCphs(0);
    eventADC->getMDH().setCrep(0);
    eventADC->getMDH().setFirstScanInSlice(false);
    eventADC->getMDH().setLastScanInSlice(false);
    eventADC->getMDH().setLastScanInMeas(false);
    eventADC->getMDH().setLastScanInConcat(false);
    eventADC->getMDH().setPhaseFT(false);
    eventADC->getMDH().setKSpaceCentreLineNo(0);
    eventADC->getMDH().setKSpaceCentrePartitionNo(0);

    if (!eventADC->prep())
    {
        MTRK_LOG("ERROR: Preparing ADC " << entry->string << " Reason: " << eventADC->getNLSStatus())
        return false;  
    }

    char* buffer=0;
    buffer=new char[1024];

    strcpy(buffer,entry->string);
    strcat(buffer,"_NCOSet");
    eventNCOSet=new sFREQ_PHASE();
    eventNCOSet->setIdent(buffer);
    eventNCOSet->setFrequency(0.);
    eventNCOSet->setPhase(0.);

    strcpy(buffer,entry->string);
    strcat(buffer,"_NCOReset");
    eventNCOReset=new sFREQ_PHASE();
    eventNCOReset->setIdent(buffer);
    eventNCOReset->setFrequency(0.);
    eventNCOReset->setPhase(0.);

    calcNCOReset();

    // TODO: Configure MDH

    MTRK_DELETE(buffer)    
           
    return true;
}


void mtrk_object::calcNCOReset()
{
    if ((eventNCOSet==0) || (eventNCOReset==0))
    {
        return;
    }
    double freq=eventNCOSet->getFrequency();
    double startPhase=eventNCOSet->getPhase();
    double resetPhase=0.00036*duration*freq+startPhase;
    eventNCOReset->setPhase(-resetPhase);
}


bool mtrk_object::prepareGrad(cJSON* entry)
{
    type=GRAD;
    MTRK_GETITEM(entry, MTRK_PROPERTIES_ARRAY, arrayName)
    MTRK_GETITEM(entry, MTRK_PROPERTIES_AMPLITUDE, amplitude)
    MTRK_GETITEMOPT(entry, MTRK_PROPERTIES_TAIL, tail)
    
    mtrk_array* array=mapiInstance->arrays.getArray(arrayName->valuestring);

    if (array==0)
    {
        MTRK_LOG("ERROR: Array not found " << arrayName->valuestring)
        return false;
    }
    if (array->type!=mtrk_array::FLOAT)
    {
        MTRK_LOG("ERROR: Invalid type of array " << arrayName->valuestring)
        return false;
    }

    int rampDown=0;
    if (tail!=0) 
    {
        rampDown=tail->valueint;
    }
    tailDuration=rampDown;
    int rampUp=array->size-rampDown;

    eventGrad=new sGRAD_PULSE_ARB();
    eventGrad->setIdent(entry->string);
    eventGrad->setRampShape((float*) array->data, rampUp, rampDown);
    eventGrad->setAmplitude(amplitude->valuedouble);
    eventGrad->setDuration(rampUp);

    if (!eventGrad->prep())
    {
        MTRK_LOG("ERROR: Preparing GRAD " << entry->string << " Reason: " << eventGrad->getNLSStatus())
        return false;          
    }

    return true;
}


bool mtrk_object::prepareSync(cJSON* entry)
{
    type=SYNC;
    MTRK_GETITEM(entry, MTRK_PROPERTIES_EVENT, eventChannel)

    // Distinguish dending on the event type
    if (strcmp(eventChannel->valuestring, "osc0")==0)
    {
        syncClass=SYNC_OSC;
        sSYNC_OSC* eventInstance=new sSYNC_OSC();
        eventInstance->setCode(SYNCCODE_OSC0);
        eventSync=(sSYNC*) eventInstance;
    }
    else   
    if (strcmp(eventChannel->valuestring, "osc1")==0)
    {
        syncClass=SYNC_OSC;            
        sSYNC_OSC* eventInstance=new sSYNC_OSC();
        eventInstance->setCode(SYNCCODE_OSC1);
        eventSync=(sSYNC*) eventInstance;
    }
    else   
    if (strcmp(eventChannel->valuestring, "trig0")==0)
    {
        syncClass=SYNC_EXTTRIGGER;            
        sSYNC_EXTTRIGGER* eventInstance=new sSYNC_EXTTRIGGER();
        eventInstance->setCode(SYNCCODE_EXT_TRIG0);
        eventSync=(sSYNC*) eventInstance;
    }
    else   
    if (strcmp(eventChannel->valuestring, "trig1")==0)
    {
        syncClass=SYNC_EXTTRIGGER;            
        sSYNC_EXTTRIGGER* eventInstance=new sSYNC_EXTTRIGGER();
        eventInstance->setCode(SYNCCODE_EXT_TRIG1);
        eventSync=(sSYNC*) eventInstance;
    }
    else
    {
        MTRK_LOG("ERROR: Unknown event type " << eventChannel->valuestring)
        return false;
    }

    eventSync->setIdent(entry->string);        
    eventSync->setDuration(duration);  
    
    return true;
}


#define MTRK_ADDCASE_MDH_INT(A,B) if (strcmp(field->string, A)==0) { MTRK_RETONFAIL(getMDHValue(field, valueInt, index)) eventADC->getMDH().B((uint16_t) valueInt); continue; }
#define MTRK_ADDCASE_MDH_BOOL(A,B) if (strcmp(field->string, A)==0) { MTRK_RETONFAIL(getMDHValue(field, valueBool)) eventADC->getMDH().B(valueBool); continue; }

bool mtrk_object::updateMDH(cJSON* entry)
{
    int  index=0;
    int  valueInt=0;
    bool valueBool=false;
    cJSON* field=0;
    cJSON_ArrayForEach(field, entry)
    {
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_LINE,             setClin)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_SLICE,            setCslc)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_PARTITION,        setCpar)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_ACQUISITION,      setCacq)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_ECHO,             setCeco)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_REPETITION,       setCrep)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_IDA,              setCida)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_IDB,              setCidb)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_IDC,              setCidc)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_IDD,              setCidd)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_IDE,              setCide)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_CENTER_LINE,      setKSpaceCentreLineNo)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_CENTER_PARTITION, setKSpaceCentrePartitionNo)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_CENTER_COLUMN,    setKSpaceCentreColumn)

        if (strcmp(field->string, MTRK_MDH_ICE_PARAMETER)==0) 
        { 
            MTRK_RETONFAIL(getMDHValue(field, valueInt, index)) 
            MTRK_CHECKRANGE(index, 0, MDH_NUMBEROFICEPROGRAMPARA, "MDH ICE parameter index")
            eventADC->getMDH().setIceProgramPara((uint16_t) index, (uint16_t) valueInt);
        }

        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_FIRST_SCAN_SLICE, setFirstScanInSlice)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_LAST_SCAN_SLICE,  setLastScanInSlice)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_LAST_SCAN_MEAS,   setLastScanInMeas)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_LAST_SCAN_CONCAT, setLastScanInConcat)     
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_LAST_LINE,        setLastMeasuredLine)

        MTRK_ADDCASE_MDH_INT (MTRK_MDH_SEGMENT,          setCseg)
        MTRK_ADDCASE_MDH_INT (MTRK_MDH_SET,              setCset)

        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_PAT_REFIMA,       setPATRefAndImaScan)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_PAT_REF,          setPATRefScan)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_RAWDATACORRECTION,setRawDataCorrection)
        MTRK_ADDCASE_MDH_BOOL(MTRK_MDH_SWAPPED,          setPRSwapped)        
    }    
    return true;
}


bool mtrk_object::getMDHValue(cJSON* field, int& value, int& index)
{
    index=0;

    if (cJSON_IsNumber(field))
    {
        value=field->valueint;
        return true;
    }
    else
    if (cJSON_IsObject(field))
    {
        MTRK_GETITEM(field, MTRK_PROPERTIES_TYPE, fieldType)    
        MTRK_GETITEMOPT(field, MTRK_PROPERTIES_INDEX, indexItem)

        if (indexItem!=0)
        {
            index=indexItem->valueint;
        }

        if (strcmp(fieldType->valuestring, MTRK_OPTIONS_COUNTER)==0)
        {
            MTRK_GETITEM(field, MTRK_PROPERTIES_COUNTER, counter)
            MTRK_CHECKRANGE(counter->valueint,0,MTRK_DEFS_COUNTERS,"MDH value counter")
            value=mapiInstance->state.counters[counter->valueint];
            return true;
        }
        else
        {
            MTRK_LOG("ERROR: Invalid MDH value type")
            return false;
        }
    }
    else
    {
        MTRK_LOG("ERROR: Invalid MDH value")
        return false;
    }
}


bool mtrk_object::getMDHValue(cJSON* field, bool& value)
{
    if (cJSON_IsBool(field))
    {
        value=cJSON_IsTrue(field);
        return true;
    }
    else
    if (cJSON_IsObject(field))
    {
        MTRK_GETITEM(field, MTRK_PROPERTIES_TYPE, fieldType)        

        if (strcmp(fieldType->valuestring, MTRK_OPTIONS_COUNTER)==0)
        {
            MTRK_GETITEM(field, MTRK_PROPERTIES_COUNTER, counter)
            MTRK_CHECKRANGE(counter->valueint,0,MTRK_DEFS_COUNTERS,"MDH value counter")
            MTRK_GETITEM(field, MTRK_PROPERTIES_TARGET, target)            
            value=(mapiInstance->state.counters[counter->valueint]==target->valueint);
            return true;
        }
        else
        {
            MTRK_LOG("ERROR: Invalid MDH value type")
            return false;
        }        
    }
    else
    {
        MTRK_LOG("ERROR: Invalid MDH value")
        return false;
    }
}
