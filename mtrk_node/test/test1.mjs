import { MTRK_TestSequence, MTRK_RenderSequence } from '../public/mtrk/mtrk_parser.mjs';
import { MTRK_LOG } from '../public/mtrk/mtrk_common.mjs';

var sequence = {};
MTRK_TestSequence(sequence);
MTRK_RenderSequence(sequence);

MTRK_LOG("WORKS!");
