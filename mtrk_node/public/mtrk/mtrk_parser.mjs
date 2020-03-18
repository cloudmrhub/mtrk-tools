
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


export function MTRK_RenderSequence(mtrkJson) {

    var arrTime  = [];
    var arrGradX = [];
    var arrGradY = [];
    var arrGradZ = [];
    var arrADC   = [];
    var arrRF    = [];

    for (var i = 0; i<9999; i++)
    {
        arrTime.push(i);
        arrGradX.push(0.);
        arrGradY.push(0.);
        arrGradZ.push(0.);
        arrADC.push(0.);
        arrRF.push(0.);    
    }

    MTRK_LOG("Call from RenderSequence");

    return {
        arrTime:  arrTime,
        arrGradX: arrGradX,
        arrGradY: arrGradY,
        arrGradZ: arrGradZ,
        arrADC:   arrADC,
        arrRF:   arrRF  
    };
};
