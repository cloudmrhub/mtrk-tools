export function MTRK_LOG(text) {
    console.log(text);
};

export const MTRK_ACTIONS_RF = "rf";

/*

(function(exports){

    exports.MTRK_LOG = function(text){
        console.log(text);
    };

    exports.MTRK_DEFS_COUNTERS             = 64;
    exports.MTRK_DEFS_FLOATS               = 64;

    exports.MTRK_COUNTER_SLICE             = 0;

    exports.MTRK_SECTIONS_FILE             = "file";
    exports.MTRK_SECTIONS_SETTINGS         = "settings";
    exports.MTRK_SECTIONS_INFOS            = "infos";
    exports.MTRK_SECTIONS_INSTRUCTIONS     = "instructions";
    exports.MTRK_SECTIONS_OBJECTS          = "objects";
    exports.MTRK_SECTIONS_ARRAYS           = "arrays";
    exports.MTRK_SECTIONS_EQUATIONS        = "equations";
    exports.MTRK_SECTIONS_GENERATOR        = "generator";

    exports.MTRK_PROPERTIES_ACTION         = "action";
    exports.MTRK_PROPERTIES_MEASUREMENT    = "measurement";
    exports.MTRK_PROPERTIES_STEPS          = "steps";
    exports.MTRK_PROPERTIES_ID             = "id";
    exports.MTRK_PROPERTIES_TYPE           = "type";
    exports.MTRK_PROPERTIES_ENCODING       = "encoding";
    exports.MTRK_PROPERTIES_RANGE          = "range";
    exports.MTRK_PROPERTIES_COUNTER        = "counter";
    exports.MTRK_PROPERTIES_FLOAT          = "float";
    exports.MTRK_PROPERTIES_INDEX          = "index";
    exports.MTRK_PROPERTIES_BLOCK          = "block";
    exports.MTRK_PROPERTIES_ARRAY          = "array";
    exports.MTRK_PROPERTIES_VALUE          = "value";
    exports.MTRK_PROPERTIES_TRUE           = "true";
    exports.MTRK_PROPERTIES_FALSE          = "false";
    exports.MTRK_PROPERTIES_TARGET         = "target";
    exports.MTRK_PROPERTIES_TIME           = "time";
    exports.MTRK_PROPERTIES_DURATION       = "duration";
    exports.MTRK_PROPERTIES_SAMPLES        = "samples";
    exports.MTRK_PROPERTIES_TAIL           = "tail";
    exports.MTRK_PROPERTIES_OBJECT         = "object";
    exports.MTRK_PROPERTIES_EQUATION       = "equation";
    exports.MTRK_PROPERTIES_INCREMENT      = "increment";
    exports.MTRK_PROPERTIES_DATA           = "data";
    exports.MTRK_PROPERTIES_SIZE           = "size";
    exports.MTRK_PROPERTIES_EVENT          = "event";
    exports.MTRK_PROPERTIES_MEMINDEX       = "memindex";
    exports.MTRK_PROPERTIES_INITIAL_PHASE  = "initial_phase";
    exports.MTRK_PROPERTIES_THICKNESS      = "thickness";
    exports.MTRK_PROPERTIES_FLIPANGLE      = "flipangle";
    exports.MTRK_PROPERTIES_PURPOSE        = "purpose";
    exports.MTRK_PROPERTIES_DWELLTIME      = "dwelltime";
    exports.MTRK_PROPERTIES_AMPLITUDE      = "amplitude";
    exports.MTRK_PROPERTIES_AXIS           = "axis";
    exports.MTRK_PROPERTIES_FREQUENCY      = "frequency";
    exports.MTRK_PROPERTIES_PHASE          = "phase";
    exports.MTRK_PROPERTIES_ADDED_PHASE    = "added_phase";
    exports.MTRK_PROPERTIES_MDH            = "mdh";
    exports.MTRK_PROPERTIES_COMMENT        = "comment";
    exports.MTRK_PROPERTIES_MESSAGE        = "message";

    exports.MTRK_OPTIONS_MAIN              = "main";
    exports.MTRK_OPTIONS_BLOCK             = "block";
    exports.MTRK_OPTIONS_COUNTER_INC       = "counter_inc";
    exports.MTRK_OPTIONS_COUNTER_SET       = "counter_set";
    exports.MTRK_OPTIONS_FLOAT_INC         = "float_inc";
    exports.MTRK_OPTIONS_FLOAT_SET         = "float_set";
    exports.MTRK_OPTIONS_FLOAT_GET         = "float_get";
    exports.MTRK_OPTIONS_RFSPOIL           = "float_rfspoil";
    exports.MTRK_OPTIONS_EQUATION          = "equation";
    exports.MTRK_OPTIONS_BASE64            = "base64";
    exports.MTRK_OPTIONS_TEXT              = "text";
    exports.MTRK_OPTIONS_INT               = "int";
    exports.MTRK_OPTIONS_FLOAT             = "float";
    exports.MTRK_OPTIONS_ARRAY             = "array";
    exports.MTRK_OPTIONS_COUNTER           = "counter";
    exports.MTRK_OPTIONS_FLIP              = "flip";
    exports.MTRK_OPTIONS_COMPLEX_FLOAT     = "complex_float";
    exports.MTRK_OPTIONS_DOUBLE            = "double";
    exports.MTRK_OPTIONS_COMPLEX_DOUBLE    = "complex_double";
    exports.MTRK_OPTIONS_EXCITATION        = "excitation";
    exports.MTRK_OPTIONS_REFOCUS           = "refocus";
    exports.MTRK_OPTIONS_INVERSION         = "inversion";
    exports.MTRK_OPTIONS_READ              = "read";
    exports.MTRK_OPTIONS_PHASE             = "phase";
    exports.MTRK_OPTIONS_SLICE             = "slice";
    exports.MTRK_OPTIONS_VALUE             = "value";

    exports.MTRK_ACTIONS_LOOP              = "loop";
    exports.MTRK_ACTIONS_CONDITION         = "condition";
    exports.MTRK_ACTIONS_RUN_BLOCK         = "run_block";
    exports.MTRK_ACTIONS_INIT              = "init";
    exports.MTRK_ACTIONS_SUBMIT            = "submit";
    exports.MTRK_ACTIONS_RF                = "rf";
    exports.MTRK_ACTIONS_ADC               = "adc";
    exports.MTRK_ACTIONS_GRAD              = "grad";
    exports.MTRK_ACTIONS_SYNC              = "sync";
    exports.MTRK_ACTIONS_MARK              = "mark";
    exports.MTRK_ACTIONS_CALC              = "calc";
    exports.MTRK_ACTIONS_DEBUG             = "debug";

    exports.MTRK_MDH_LINE                  = "line";
    exports.MTRK_MDH_SLICE                 = "slice";
    exports.MTRK_MDH_PARTITION             = "partition";
    exports.MTRK_MDH_ACQUISITION           = "acquisition";
    exports.MTRK_MDH_ECHO                  = "echo";
    exports.MTRK_MDH_REPETITION            = "repetition";
    exports.MTRK_MDH_SEGMENT               = "segment";
    exports.MTRK_MDH_SET                   = "set";
    exports.MTRK_MDH_IDA                   = "ida";
    exports.MTRK_MDH_IDB                   = "idb";
    exports.MTRK_MDH_IDC                   = "idc";
    exports.MTRK_MDH_IDD                   = "idd";
    exports.MTRK_MDH_IDE                   = "ide";
    exports.MTRK_MDH_CENTER_LINE           = "center_line";
    exports.MTRK_MDH_CENTER_PARTITION      = "center_partition";
    exports.MTRK_MDH_CENTER_COLUMN         = "center_column";
    exports.MTRK_MDH_FIRST_SCAN_SLICE      = "first_scan_slice";
    exports.MTRK_MDH_LAST_SCAN_SLICE       = "last_scan_slice";
    exports.MTRK_MDH_LAST_SCAN_MEAS        = "last_scan_meas";
    exports.MTRK_MDH_LAST_SCAN_CONCAT      = "last_scan_concat";
    exports.MTRK_MDH_LAST_LINE             = "last_line";
    exports.MTRK_MDH_ICE_PARAMETER         = "ice_parameter";
    exports.MTRK_MDH_RAWDATACORRECTION     = "rawdata_correction";
    exports.MTRK_MDH_SWAPPED               = "swapped";
    exports.MTRK_MDH_PAT_REF               = "patrefscan";
    exports.MTRK_MDH_PAT_REFIMA            = "patrefimascan";

    exports.MTRK_INFOS_FOV                 = "fov";
    exports.MTRK_INFOS_SEQSTRING           = "seqstring";
    exports.MTRK_INFOS_DESCRIPTION         = "description";
    exports.MTRK_INFOS_RECONSTRUCTION      = "reconstruction";
    exports.MTRK_INFOS_PELINES             = "pelines";

    exports.MTRK_SETTINGS_READOUT_OS       = "readout_os";
    exports.MTRK_SETTINGS_SLICES           = "slices"    

  
})(typeof exports === 'undefined'? this['mtrk_common']={}: exports);

*/