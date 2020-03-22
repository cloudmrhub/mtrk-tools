
import { MTRK_LOG, def } from './mtrk_common.mjs';
import expr_eval from './expr-eval.mjs';


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
var equations={};
var objects={};
var arrays={};


var parser = new expr_eval.Parser();

parser.functions.ctr = function(index) {
    if ((index<0) || (index>=def.MTRK_DEFS_COUNTERS)) {
        return -1;
    }
    return state.counters[index];
};    

parser.functions.flt = function(index) {
    if ((index<0) || (index>=def.MTRK_DEFS_FLOATS)) {
        return -1;
    }
    return state.floats[index];
};    


function stateUpdateDuration(startTime, duration) {
    var endTime = startTime + duration;        
    if (endTime > state.tableDuration)
    {
        state.tableDuration = endTime;
    }    
}


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
    // TODO: Render objects

    state.clock += state.tableDuration;
    state.tableDuration = -1;
    state.tableStart = -1;
    return true;
}


function runActionRF(item) {
    // TODO
    return true;
}


function runActionADC(item) {
    // TODO    
    return true;
}


function runActionGrad(item) {
    // TODO    
    return true;
}


function runActionSync(item) {
    // TODO
    return true;
}


function runActionMark(item) {
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_TIME)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_TIME);
        return false;
    }
    stateUpdateDuration(item.time, 0);
    return true;
}


function runActionCalc(item) {
    if (!item.hasOwnProperty(def.MTRK_PROPERTIES_TYPE)) {
        MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_TYPE);
        return false;
    }

    switch (item[def.MTRK_PROPERTIES_TYPE]) {
        case def.MTRK_OPTIONS_COUNTER_INC:         
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
                return false;
            }

            var counter_int=item[def.MTRK_PROPERTIES_COUNTER]
            if ((counter_int<0) || (counter_int>=def.MTRK_DEFS_COUNTERS)) {
                return false;
            }
            state.counters[counter_int]++;                
            break;        

        case def.MTRK_OPTIONS_COUNTER_SET:
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
                return false;
            }    
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_VALUE)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_VALUE);
                return false;
            }

            var counter_int=item[def.MTRK_PROPERTIES_COUNTER]
            if ((counter_int<0) || (counter_int>=def.MTRK_DEFS_COUNTERS)) {
                return false;
            }
            state.counters[counter_int]=item[def.MTRK_PROPERTIES_VALUE];
            break;        

        case def.MTRK_OPTIONS_FLOAT_INC:
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_FLOAT)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_FLOAT);
                return false;
            }    

            var index_int=item[def.MTRK_PROPERTIES_FLOAT]
            if ((index_int<0) || (index_int>=def.MTRK_DEFS_FLOATS)) {
                return false;
            }
            state.floats[index_int]+=1.;
            break;     

        case def.MTRK_OPTIONS_FLOAT_SET:
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_FLOAT)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_FLOAT);
                return false;
            }    
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_VALUE)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_VALUE);
                return false;
            }

            var index_int=item[def.MTRK_PROPERTIES_FLOAT]
            if ((index_int<0) || (index_int>=def.MTRK_DEFS_FLOATS)) {
                return false;
            }
            state.floats[index_int]=item[def.MTRK_PROPERTIES_VALUE];            
            break;        

        case def.MTRK_OPTIONS_EQUATION:         
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_EQUATION)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_EQUATION);
                return false;
            }    

            var index=0;
            var targetIsFloat=true;

            if (item.hasOwnProperty(def.MTRK_PROPERTIES_FLOAT)) {
                targetIsFloat=true;
                index=item[def.MTRK_PROPERTIES_FLOAT];
            } else {
                if (item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
                    MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
                    return false;
                }
                targetIsFloat=false;
                index=item[def.MTRK_PROPERTIES_COUNTER];
            }

            var equationValue=equations[item[def.MTRK_PROPERTIES_EQUATION]].expression.evaluate({});

            if (targetIsFloat) {
                state.floats[index]=equationValue;
            } else {
                state.counters[index]=int(equationValue);
            }
            break;    

        case def.MTRK_OPTIONS_RFSPOIL:      
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_FLOAT)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_FLOAT);
                return false;
            }    
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_INCREMENT)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_INCREMENT);
                return false;
            }                            

            var index_int=item[def.MTRK_PROPERTIES_FLOAT]
            if ((index_int<0) || (index_int>=def.MTRK_DEFS_FLOATS-1)) {
                return false;
            }
            // Increase the increment
            state.floats[index_int+1]+=item[def.MTRK_PROPERTIES_INCREMENT];

            // Increase the actual RF phase with the increment
            state.floats[index_int]+=state.floats[index_int+1];

            // Make sure that the phase stays in a valid range
            state.floats[index_int]=state.floats[index_int] % 360000.;
            state.floats[index_int+1]=state.floats[index_int+1] % 360000.;       
            break;    

        case def.MTRK_OPTIONS_FLOAT_GET:         
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_ARRAY)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_ARRAY);
                return false;
            }    
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_FLOAT)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_FLOAT);
                return false;
            }    
            if (!item.hasOwnProperty(def.MTRK_PROPERTIES_COUNTER)) {
                MTRK_LOG("ERROR: Missing property "+def.MTRK_PROPERTIES_COUNTER);
                return false;
            }    

            if (!arrays.hasOwnProperty(item[def.MTRK_PROPERTIES_ARRAY])) {
                MTRK_LOG("ERROR: Missing array "+item[def.MTRK_PROPERTIES_ARRAY]);
                return false;
            }    

            var index=item[def.MTRK_PROPERTIES_COUNTER];
            var target=item[def.MTRK_PROPERTIES_FLOAT];

            // TODO: Check bounds

            var value=arrayGetDouble(item[def.MTRK_PROPERTIES_ARRAY],index);
            state.floats[target]=value;
            break;        
    }

    return true;

/*
    if (strcmp(type->valuestring, MTRK_OPTIONS_FLOAT_GET)==0)
    {
        MTRK_GETITEM(item, MTRK_PROPERTIES_ARRAY, arrayName)
        MTRK_GETITEM(item, MTRK_PROPERTIES_FLOAT, target)
        MTRK_GETITEM(item, MTRK_PROPERTIES_COUNTER, counter)

        MTRK_CHECKRANGE(target->valueint, 0, MTRK_DEFS_FLOATS, "Float target index")
        MTRK_CHECKRANGE(counter->valueint, 0, MTRK_DEFS_COUNTERS, "Counter index")

        mtrk_array* array=arrays.getArray(arrayName->valuestring);

        if (array==0)
        {
            MTRK_LOG("ERROR: Array not found " << arrayName->valuestring)
            return false;
        }

        state.floats[target->valueint]=array->getDouble(counter->valueint);
    }
    */    
}


function runActionDebug(item) {
    // TODO

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


function prepareArrays(mtrkJson) {
    for (var item in mtrkJson.arrays) {
        var newArray = {
            "type": mtrkJson.arrays[item][def.MTRK_PROPERTIES_TYPE],
            "data": [],
            "size": mtrkJson.arrays[item][def.MTRK_PROPERTIES_SIZE]
        }
        if (mtrkJson.arrays[item][def.MTRK_PROPERTIES_ENCODING]==def.MTRK_OPTIONS_TEXT) {
            newArray["data"]=mtrkJson.arrays[item][def.MTRK_PROPERTIES_DATA];
        } else {
            // TODO
        }
        arrays[item]=newArray;
    }
    console.log(arrays);
    return true;
}


function arrayGetDouble(array, index) {
    if (!arrays.hasOwnProperty(array)) {
        MTRK_LOG("ERROR: Missing array "+array);
        return false;
    }
    
    if ((index<0) || (index>=arrays[array].size)) {
        return false;
    }
    var memIndex=index;
    if ((arrays[array].type==def.MTRK_OPTIONS_COMPLEX_FLOAT) || 
        (arrays[array].type==def.MTRK_OPTIONS_COMPLEX_DOUBLE)) {
        memIndex=2*index;
    }
    return arrays[array][memIndex];
}


function prepareObjects(mtrkJson) {
    return true;
}


function prepareEquations(mtrkJson) {
    // Generate secondary object containing the compiled expressions
    for (var item in mtrkJson.equations) {
        var newEquation = {
            "equation": mtrkJson.equations[item].equation,
            "expression": parser.parse(mtrkJson.equations[item].equation)
        }
        equations[item]=newEquation;
    }
    return true;
}


export function MTRK_RenderSequence(mtrkJson) {    
    render = {
        arrTime:  [],
        arrGradX: [],
        arrGradY: [],
        arrGradZ: [],
        arrADC:   [],
        arrRF:    [] 
    }

    sequence=mtrkJson;
    equations={};
    objects={};
    arrays={};
    resetState();

    if (!prepareArrays(mtrkJson)) {
        MTRK_LOG("ERROR: Unable to prepare arrays");
        return false;
    }
    if (!prepareObjects(mtrkJson)) {
        MTRK_LOG("ERROR: Unable to prepare objects");
        return false;        
    }
    if (!prepareEquations(mtrkJson)) {
        MTRK_LOG("ERROR: Unable to prepare equations");
        return false;
    }

    var mainBlock=getBlock(def.MTRK_OPTIONS_MAIN);
    if (mainBlock==false) {
        MTRK_LOG("ERROR: Missing main block");
        return false;
    }
    if (!runBlock(mainBlock)) {
        MTRK_LOG("ERROR: Problems running sequence");
        return false;
    }
    
    return render;
};
