#ifndef mtrk_common_h
#define mtrk_common_h 1

#include <iostream>
#include <string>
#include <fstream>


#define MTRK_DEFS_COUNTERS 8
#define MTRK_DEFS_FLOATS   8

#define MTRK_SECTIONS_FILE            "file"
#define MTRK_SECTIONS_SETTINGS        "settings"
#define MTRK_SECTIONS_INFOS           "infos"
#define MTRK_SECTIONS_INSTRUCTIONS    "instructions"
#define MTRK_SECTIONS_OBJECTS         "objects"
#define MTRK_SECTIONS_ARRAYS          "arrays"
#define MTRK_SECTIONS_EQUATIONS       "equations"

#define MTRK_PROPERTIES_ACTION        "action"
#define MTRK_PROPERTIES_MEASUREMENT   "measurement"
#define MTRK_PROPERTIES_STEPS         "steps"
#define MTRK_PROPERTIES_ID            "id"
#define MTRK_PROPERTIES_TYPE          "type"
#define MTRK_PROPERTIES_ENCODING      "encoding"
#define MTRK_PROPERTIES_RANGE         "range"
#define MTRK_PROPERTIES_COUNTER       "counter"
#define MTRK_PROPERTIES_FLOAT         "float"
#define MTRK_PROPERTIES_INDEX         "index"
#define MTRK_PROPERTIES_BLOCK         "block"
#define MTRK_PROPERTIES_ARRAY         "array"
#define MTRK_PROPERTIES_VALUE         "value"
#define MTRK_PROPERTIES_PRINT_MSG     "print_message"
#define MTRK_PROPERTIES_TRUE          "true"
#define MTRK_PROPERTIES_FALSE         "false"
#define MTRK_PROPERTIES_TARGET        "target"
#define MTRK_PROPERTIES_TIME          "time"
#define MTRK_PROPERTIES_DURATION      "duration"
#define MTRK_PROPERTIES_SAMPLES       "samples"
#define MTRK_PROPERTIES_TAIL          "tail"
#define MTRK_PROPERTIES_OBJECT        "object"
#define MTRK_PROPERTIES_EQUATION      "equation"
#define MTRK_PROPERTIES_INCREMENT     "increment"
#define MTRK_PROPERTIES_DATA          "data"
#define MTRK_PROPERTIES_SIZE          "size"
#define MTRK_PROPERTIES_EVENT         "event"
#define MTRK_PROPERTIES_MEMINDEX      "memindex"
#define MTRK_PROPERTIES_INITIAL_PHASE "initial_phase"
#define MTRK_PROPERTIES_THICKNESS     "thickness"
#define MTRK_PROPERTIES_FLIPANGLE     "flipangle"
#define MTRK_PROPERTIES_PURPOSE       "purpose"
#define MTRK_PROPERTIES_DWELLTIME     "dwelltime"
#define MTRK_PROPERTIES_AMPLITUDE     "amplitude"
#define MTRK_PROPERTIES_AXIS          "axis"

#define MTRK_OPTIONS_MAIN             "main"
#define MTRK_OPTIONS_BLOCK            "block"
#define MTRK_OPTIONS_COUNTER_INC      "counter_inc"
#define MTRK_OPTIONS_COUNTER_SET      "counter_set"
#define MTRK_OPTIONS_FLOAT_INC        "float_inc"
#define MTRK_OPTIONS_FLOAT_SET        "float_set"
#define MTRK_OPTIONS_FLOAT_GET        "float_get"
#define MTRK_OPTIONS_RFSPOIL          "float_rfspoil"
#define MTRK_OPTIONS_EQUATION         "equation"
#define MTRK_OPTIONS_BASE64           "base64"
#define MTRK_OPTIONS_TEXT             "text"
#define MTRK_OPTIONS_INT              "int"
#define MTRK_OPTIONS_FLOAT            "float"
#define MTRK_OPTIONS_COMPLEX_FLOAT    "complex_float"
#define MTRK_OPTIONS_DOUBLE           "double"
#define MTRK_OPTIONS_COMPLEX_DOUBLE   "complex_double"
#define MTRK_OPTIONS_EXCITATION       "excitation"
#define MTRK_OPTIONS_REFOCUS          "refocus"
#define MTRK_OPTIONS_INVERSION        "inversion"
#define MTRK_OPTIONS_READ             "read"
#define MTRK_OPTIONS_PHASE            "phase"
#define MTRK_OPTIONS_SLICE            "slice"

#define MTRK_ACTIONS_LOOP             "loop"
#define MTRK_ACTIONS_CONDITION        "condition"
#define MTRK_ACTIONS_RUN_BLOCK        "run_block"
#define MTRK_ACTIONS_INIT             "init"
#define MTRK_ACTIONS_SUBMIT           "submit"
#define MTRK_ACTIONS_RF               "rf"
#define MTRK_ACTIONS_ADC              "adc"
#define MTRK_ACTIONS_GRAD             "grad"
#define MTRK_ACTIONS_SYNC             "sync"
#define MTRK_ACTIONS_MARK             "mark"
#define MTRK_ACTIONS_CALC             "calc"
#define MTRK_ACTIONS_DEBUG            "debug"

#define MTRK_INFOS_SLICES             "slices"
#define MTRK_INFOS_FOV                "fov"
#define MTRK_INFOS_SEQSTRING          "seqstring"
#define MTRK_INFOS_DESCRIPTION        "description"
#define MTRK_INFOS_RECONSTRUCTION     "reconstruction"

#define MTRK_SETTINGS_READOUT_OS      "readout_os"

#define MTRK_LOG(x)                   std::cout << x << std::endl;
#define MTRK_DELETE(x)                if (x!=0) { delete x; x=0; }
#define MTRK_RETONFAIL(x)             if (!x) { return false; }
#define MTRK_RETONFAILMSG(x,y)        if (!x) { return false; MTRK_LOG(y) }
#define MTRK_GETITEM(a,b,c)           cJSON* c = cJSON_GetObjectItemCaseSensitive(a,b); if (c==NULL) { MTRK_LOG("Missing item: " << b) return false; }
#define MTRK_GETITEMOPT(a,b,c)        cJSON* c = cJSON_GetObjectItemCaseSensitive(a,b);

#endif
