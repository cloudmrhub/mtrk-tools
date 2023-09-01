from __future__ import annotations

from typing import List, Optional, Union
from pydantic import BaseModel
import json

class File(BaseModel):
    format: str
    version: int
    measurement: str
    system: str


class Settings(BaseModel):
    readout_os: int


class Infos(BaseModel):
    description: str
    slices: int
    fov: int
    pelines: int
    seqstring: str
    reconstruction: str


class Step1(BaseModel):
    action: str
    block: str


class Step(BaseModel):
    action: str
    counter: int
    range: int
    steps: List[Step1]


class Main(BaseModel):
    print_message: str
    steps: List[Step]


class Step3(BaseModel):
    action: str
    block: str


class Step2(BaseModel):
    action: str
    counter: int
    range: int
    steps: List[Step3]


class BlockPhaseEncoding(BaseModel):
    print_counter: str
    print_message: str
    steps: List[Step2]


class AddedPhase(BaseModel):
    type: str
    float: int


class AmplitudeItem(BaseModel):
    type: str
    equation: str


class Line(BaseModel):
    type: str
    counter: int


class FirstScanSlice(BaseModel):
    type: str
    counter: int
    target: int


class LastScanSlice(BaseModel):
    type: str
    counter: int
    target: int


class CenterLine(BaseModel):
    type: str
    value: int


class CenterColumn(BaseModel):
    type: str
    value: int


class Mdh(BaseModel):
    line: Line
    first_scan_slice: FirstScanSlice
    last_scan_slice: LastScanSlice
    center_line: CenterLine
    center_column: CenterColumn


class Step4(BaseModel):
    action: str
    type: Optional[str] = None
    float: Optional[int] = None
    increment: Optional[int] = None
    gradients: Optional[str] = None
    object: Optional[str] = None
    time: Optional[int] = None
    axis: Optional[str] = None
    added_phase: Optional[AddedPhase] = None
    amplitude: Optional[Union[str, AmplitudeItem]] = None
    frequency: Optional[int] = None
    phase: Optional[int] = None
    mdh: Optional[Mdh] = None


class BlockTR(BaseModel):
    print_counter: str
    print_message: str
    steps: List[Step4]


class Instructions(BaseModel):
    main: Main
    block_phaseEncoding: BlockPhaseEncoding
    block_TR: BlockTR


class RfExcitation(BaseModel):
    type: str
    array: str
    duration: int
    initial_phase: int
    thickness: int
    flipangle: int
    purpose: str

class Object(BaseModel):
    type: str
    array: str
    duration: int
    tail: int
    amplitude: float

class GradSliceSelect(Object):
    type: Literal["slice_select"]

class GradSliceRefocus(BaseModel):
    type: Literal["refocus"]


class GradReadDephase(BaseModel):
    type: 'dephase'
    array: str
    duration: int
    tail: int
    amplitude: float


class GradReadReadout(BaseModel):
    type: str
    array: str
    duration: int
    tail: int
    amplitude: float


class GradPhaseEncode(BaseModel):
    type: str
    array: str
    duration: int
    tail: int
    amplitude: int


class AdcReadout(Object):
    type: str
    duration: int
    samples: int
    dwelltime: int


class Ttl(BaseModel):
    type: str
    duration: int
    event: str


class Objects(BaseModel):
    rf_excitation: RfExcitation
    grad_slice_select: GradSliceSelect
    grad_slice_refocus: GradSliceRefocus
    grad_read_dephase: GradReadDephase
    grad_read_readout: GradReadReadout
    grad_phase_encode: GradPhaseEncode
    adc_readout: AdcReadout
    ttl: Ttl


class Rfpulse(BaseModel):
    size: int
    type: str
    encoding: str
    data: List[float]


class Grad_100_2560_100(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]


class Grad_220_10_220(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]


class Grad_220_80_220(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]


class Grad_30_3840_30(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]


class Arrays(BaseModel):
    rfpulse: Rfpulse
    grad_100_2560_100: Grad_100_2560_100
    grad_220_10_220: Grad_220_10_220
    grad_220_80_220: Grad_220_80_220
    grad_30_3840_30: Grad_30_3840_30


class Phaseencoding(BaseModel):
    truc: str


class Equations(BaseModel):
    phaseencoding: Phaseencoding


class PulseSequence(BaseModel):
    file: File
    settings: Settings
    infos: Infos
    instructions: Instructions
    objects: dict[str, Object]
    arrays: Arrays
    equations: Equations

# Load sequence data
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\miniflash.mtrk') as sdlFile:
    sdlData = json.load(sdlFile)
    sequence_data = PulseSequence(**sdlData)
    print(sequence_data.file.format)

    # Modify a value
    sequence_data.file.format = "Custom!"
    print(sequence_data.file.format)

# Write json schema to SDL file
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\miniflash.mtrk', 'w') as sdlFileOut:
    sdlFileOut.write(sequence_data.model_dump_json(indent=4))

