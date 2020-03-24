var logToConsole=true;
var logOutput=[];

export function MTRK_SetLogToConsole(value) {
    logToConsole=value;
}


export function MTRK_GetLogOutput() {
    return logOutput;
}


export function MTRK_LOG(text) {
    if (logToConsole) {
        console.log(text);
    } else {
        logOutput.push(text.toString());
    }    
};


export function jsonIsNumber(item) {
    if (typeof item === "number") {
        return true;
    } else {
        return false;
    }
}


export function jsonIsString(item) {
    if (typeof item === "string") {
        return true;
    } else {
        return false;
    }
}


export function jsonIsObject(item) {
    if (typeof item === "object") {
        return true;
    } else {
        return false;
    }
}


export const def = {

    MTRK_DEFS_COUNTERS:              64,
    MTRK_DEFS_FLOATS:                64,

    MTRK_COUNTER_SLICE:              0,

    MTRK_SECTIONS_FILE:              "file",
    MTRK_SECTIONS_SETTINGS:          "settings",
    MTRK_SECTIONS_INFOS:             "infos",
    MTRK_SECTIONS_INSTRUCTIONS:      "instructions",
    MTRK_SECTIONS_OBJECTS:           "objects",
    MTRK_SECTIONS_ARRAYS:            "arrays",
    MTRK_SECTIONS_EQUATIONS:         "equations",
    MTRK_SECTIONS_GENERATOR:         "generator",

    MTRK_PROPERTIES_ACTION:          "action",
    MTRK_PROPERTIES_MEASUREMENT:     "measurement",
    MTRK_PROPERTIES_STEPS:           "steps",
    MTRK_PROPERTIES_ID:              "id",
    MTRK_PROPERTIES_TYPE:            "type",
    MTRK_PROPERTIES_ENCODING:        "encoding",
    MTRK_PROPERTIES_RANGE:           "range",
    MTRK_PROPERTIES_COUNTER:         "counter",
    MTRK_PROPERTIES_FLOAT:           "float",
    MTRK_PROPERTIES_INDEX:           "index",
    MTRK_PROPERTIES_BLOCK:           "block",
    MTRK_PROPERTIES_ARRAY:           "array",
    MTRK_PROPERTIES_VALUE:           "value",
    MTRK_PROPERTIES_TRUE:            "true",
    MTRK_PROPERTIES_FALSE:           "false",
    MTRK_PROPERTIES_TARGET:          "target",
    MTRK_PROPERTIES_TIME:            "time",
    MTRK_PROPERTIES_DURATION:        "duration",
    MTRK_PROPERTIES_SAMPLES:         "samples",
    MTRK_PROPERTIES_TAIL:            "tail",
    MTRK_PROPERTIES_OBJECT:          "object",
    MTRK_PROPERTIES_EQUATION:        "equation",
    MTRK_PROPERTIES_INCREMENT:       "increment",
    MTRK_PROPERTIES_DATA:            "data",
    MTRK_PROPERTIES_SIZE:            "size",
    MTRK_PROPERTIES_EVENT:           "event",
    MTRK_PROPERTIES_MEMINDEX:        "memindex",
    MTRK_PROPERTIES_INITIAL_PHASE:   "initial_phase",
    MTRK_PROPERTIES_THICKNESS:       "thickness",
    MTRK_PROPERTIES_FLIPANGLE:       "flipangle",
    MTRK_PROPERTIES_PURPOSE:         "purpose",
    MTRK_PROPERTIES_DWELLTIME:       "dwelltime",
    MTRK_PROPERTIES_AMPLITUDE:       "amplitude",
    MTRK_PROPERTIES_AXIS:            "axis",
    MTRK_PROPERTIES_FREQUENCY:       "frequency",
    MTRK_PROPERTIES_PHASE:           "phase",
    MTRK_PROPERTIES_ADDED_PHASE:     "added_phase",
    MTRK_PROPERTIES_MDH:             "mdh",
    MTRK_PROPERTIES_COMMENT:         "comment",
    MTRK_PROPERTIES_MESSAGE:         "message",

    MTRK_OPTIONS_MAIN:               "main",
    MTRK_OPTIONS_BLOCK:              "block",
    MTRK_OPTIONS_COUNTER_INC:        "counter_inc",
    MTRK_OPTIONS_COUNTER_SET:        "counter_set",
    MTRK_OPTIONS_FLOAT_INC:          "float_inc",
    MTRK_OPTIONS_FLOAT_SET:          "float_set",
    MTRK_OPTIONS_FLOAT_GET:          "float_get",
    MTRK_OPTIONS_RFSPOIL:            "float_rfspoil",
    MTRK_OPTIONS_EQUATION:           "equation",
    MTRK_OPTIONS_BASE64:             "base64",
    MTRK_OPTIONS_TEXT:               "text",
    MTRK_OPTIONS_INT:                "int",
    MTRK_OPTIONS_FLOAT:              "float",
    MTRK_OPTIONS_ARRAY:              "array",
    MTRK_OPTIONS_COUNTER:            "counter",
    MTRK_OPTIONS_FLIP:               "flip",
    MTRK_OPTIONS_COMPLEX_FLOAT:      "complex_float",
    MTRK_OPTIONS_DOUBLE:             "double",
    MTRK_OPTIONS_COMPLEX_DOUBLE:     "complex_double",
    MTRK_OPTIONS_EXCITATION:         "excitation",
    MTRK_OPTIONS_REFOCUS:            "refocus",
    MTRK_OPTIONS_INVERSION:          "inversion",
    MTRK_OPTIONS_READ:               "read",
    MTRK_OPTIONS_PHASE:              "phase",
    MTRK_OPTIONS_SLICE:              "slice",
    MTRK_OPTIONS_VALUE:              "value",

    MTRK_ACTIONS_LOOP:               "loop",
    MTRK_ACTIONS_CONDITION:          "condition",
    MTRK_ACTIONS_RUN_BLOCK:          "run_block",
    MTRK_ACTIONS_INIT:               "init",
    MTRK_ACTIONS_SUBMIT:             "submit",
    MTRK_ACTIONS_RF:                 "rf",
    MTRK_ACTIONS_ADC:                "adc",
    MTRK_ACTIONS_GRAD:               "grad",
    MTRK_ACTIONS_SYNC:               "sync",
    MTRK_ACTIONS_MARK:               "mark",
    MTRK_ACTIONS_CALC:               "calc",
    MTRK_ACTIONS_DEBUG:              "debug",

    MTRK_MDH_LINE:                   "line",
    MTRK_MDH_SLICE:                  "slice",
    MTRK_MDH_PARTITION:              "partition",
    MTRK_MDH_ACQUISITION:            "acquisition",
    MTRK_MDH_ECHO:                   "echo",
    MTRK_MDH_REPETITION:             "repetition",
    MTRK_MDH_SEGMENT:                "segment",
    MTRK_MDH_SET:                    "set",
    MTRK_MDH_IDA:                    "ida",
    MTRK_MDH_IDB:                    "idb",
    MTRK_MDH_IDC:                    "idc",
    MTRK_MDH_IDD:                    "idd",
    MTRK_MDH_IDE:                    "ide",
    MTRK_MDH_CENTER_LINE:            "center_line",
    MTRK_MDH_CENTER_PARTITION:       "center_partition",
    MTRK_MDH_CENTER_COLUMN:          "center_column",
    MTRK_MDH_FIRST_SCAN_SLICE:       "first_scan_slice",
    MTRK_MDH_LAST_SCAN_SLICE:        "last_scan_slice",
    MTRK_MDH_LAST_SCAN_MEAS:         "last_scan_meas",
    MTRK_MDH_LAST_SCAN_CONCAT:       "last_scan_concat",
    MTRK_MDH_LAST_LINE:              "last_line",
    MTRK_MDH_ICE_PARAMETER:          "ice_parameter",
    MTRK_MDH_RAWDATACORRECTION:      "rawdata_correction",
    MTRK_MDH_SWAPPED:                "swapped",
    MTRK_MDH_PAT_REF:                "patrefscan",
    MTRK_MDH_PAT_REFIMA:             "patrefimascan",

    MTRK_INFOS_FOV:                  "fov",
    MTRK_INFOS_SEQSTRING:            "seqstring",
    MTRK_INFOS_DESCRIPTION:          "description",
    MTRK_INFOS_RECONSTRUCTION:       "reconstruction",
    MTRK_INFOS_PELINES:              "pelines",

    MTRK_SETTINGS_READOUT_OS:        "readout_os",
    MTRK_SETTINGS_SLICES:            "slices"    

};
