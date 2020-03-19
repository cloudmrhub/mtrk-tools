
import { MTRK_LOG, def } from './mtrk_common.mjs';


export function MTRK_TestSequence(mtrkJson) {      
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_FILE)) {
        return "File section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_SETTINGS)) {
        return "Settings section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_INFOS)) {
        return "Infos section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_INSTRUCTIONS)) {
        return "Instructions section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_OBJECTS)) {
        return "Objects section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_ARRAYS)) {
        return "Arrays section missing";
    }
    if (!mtrkJson.hasOwnProperty(def.MTRK_SECTIONS_EQUATIONS)) {
        return "Equations section missing";
    }
    return "";
};


var state = {
    counters: [],
    floats: [],
    clock: 0,
    tableStart: 0,
    tableDuration: 0,
    slices: 0,
    totalDuration: 0
};


var sequence={};
var render={};
var recursions=0;


function resetState() {       
    state.clock=0;
    state.tableStart=0;
    state.tableDuration=0;
    state.slices=0;
    state.totalDuration=0;
    state.counters=[];
    for (var i=0; i<def.MTRK_DEFS_COUNTERS; i++) {
        state.counters[i]=0;
    }
    state.floats=[];
    for (var i=0; i<def.MTRK_DEFS_FLOATS; i++) {
        state.floats[i]=0.;
    }
}


function getBlock(name) {
    if (!sequence.instructions.hasOwnProperty(name)) {
        MTRK_LOG("ERROR: Block not found "+name);
        return false;
    } else {
        return sequence.instructions[name];
    }
}


function runActionBlock(item) {
    var blockToRun=getBlock(item.block);
    if (blockToRun==false) {
        MTRK_LOG("ERROR: Missing block " + blockToRun);
        return false;
    }
    return runBlock(blockToRun);
}


function runActionLoop(item) {
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_RANGE)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_RANGE);
        return false;
    }
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
        return false;
    }

    var range=item[def.MTRK_PROPERTIES_RANGE];
    var counter=item[def.MTRK_PROPERTIES_COUNTER];

    for (state.counters[counter]=0; state.counters[counter] < range; state.counters[counter]++)
    {
        if (!runBlock(item)) 
        {
            return false;
        }
    }
    return true;
}


function runActionCondition(item) {
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
        return false;
    }
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_TARGET)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_TARGET);
        return false;
    }

    var counter_int=item[def.MTRK_PROPERTIES_COUNTER];
    if ((counter_int<0) || (counter_int>=def.MTRK_DEFS_COUNTERS)) {
        return false;
    }

    if (state.counters[counter_int]==item[def.MTRK_PROPERTIES_TARGET]) {
        if (!item.hasOwnProperty(def.MTRK_PROPERTIES_TRUE)) {
            MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_TRUE);
            return false;
        }
        return runBlock(item[def.MTRK_PROPERTIES_TRUE]);
    } else {
        if (!item.hasOwnProperty(def.MTRK_PROPERTIES_FALSE)) {
            MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_FALSE);
            return false;
        }
        return runBlock(item[def.MTRK_PROPERTIES_FALSE]);
    }
}


function runActionInit(item) {
    state.tableDuration = 0;
    state.tableStart = 0;
    return true;
}


function runActionSubmit(item) {
    state.clock += state.tableDuration;
    state.tableDuration = -1;
    state.tableStart = -1;
    return true;
}


function runActionRF(item) {
    return true;
}


function runActionADC(item) {
    return true;
}


function runActionGrad(item) {
    return true;
}


function runActionSync(item) {
    return true;
}


function runActionMark(item) {
    return true;
}


function runActionCalc(item) {
    return true;
}


function runActionDebug(item) {
    return true;
}


function runBlock(block) {
    if (!block.hasOwnProperty(def.MTRK_PROPERTIES_STEPS)) {
        MTRK_LOG("ERROR: Missing block steps ");
        return false;
    }

    recursions++;
    if (recursions > 1000) {
        MTRK_LOG("ERROR: Too many recursions.");
        return false;
    }
   
    var success=true;
    for (var step in block.steps) {
        switch (block.steps[step].action) {
            case def.MTRK_ACTIONS_LOOP: 
                success=runActionLoop(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_CONDITION: 
                success=runActionCondition(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_RUN_BLOCK: 
                success=runActionBlock(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_INIT:
                success=runActionInit(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_SUBMIT: 
                success=runActionSubmit(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_RF: 
                success=runActionRF(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_ADC: 
                success=runActionADC(block.steps[step]);
            break;
            case def.MTRK_ACTIONS_GRAD: 
                success=runActionGrad(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_SYNC: 
                success=runActionSync(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_MARK: 
                success=runActionMark(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_CALC: 
                success=runActionCalc(block.steps[step]);
                break;
            case def.MTRK_ACTIONS_DEBUG: 
                success=runActionDebug(block.steps[step]);
                break;
        }
        if (!success) {
            break;
        }
    }
    recursions--;
    return success;
}


export function MTRK_RenderSequence(mtrkJson) {    
    sequence=mtrkJson;

    render = {
        arrTime:  [],
        arrGradX: [],
        arrGradY: [],
        arrGradZ: [],
        arrADC:   [],
        arrRF:    [] 
    }

    for (var i = 0; i<9999; i++)
    {
        render.arrTime.push(i);
        render.arrGradX.push(0.);
        render.arrGradY.push(0.);
        render.arrGradZ.push(0.);
        render.arrADC.push(0.);
        render.arrRF.push(0.);    
    }

    resetState();

    var mainBlock=getBlock(def.MTRK_OPTIONS_MAIN);
    if (mainBlock==false) {
        MTRK_LOG("ERROR: Missing main block");
        return false;
    }
    runBlock(mainBlock);
    return render;
};
