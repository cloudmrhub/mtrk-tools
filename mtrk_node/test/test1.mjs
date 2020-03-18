import fs from 'fs';

import { MTRK_TestSequence, MTRK_RenderSequence } from '../public/mtrk/mtrk_parser.mjs';
import { MTRK_LOG } from '../public/mtrk/mtrk_common.mjs';

var sequence = {};
var file = './seq/miniflash.mtrk';

MTRK_LOG("");
MTRK_LOG("Test 1: Testing reading and validating sequences");
MTRK_LOG("");

try {
    const data = fs.readFileSync(file, 'utf8');
    sequence = JSON.parse(data);
} catch (err) {
    console.error(err)
}

var testResult=MTRK_TestSequence(sequence);
MTRK_RenderSequence(sequence);

if (testResult=="") {
    testResult="OK";
}
MTRK_LOG("Result: " + testResult); 
MTRK_LOG("");
