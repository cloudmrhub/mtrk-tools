from __future__ import annotations

from typing import List, Optional, Union
from typing_extensions import Literal, TypedDict
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

class Main(BaseModel):
    print_message: str
    steps: List[Step]

class Step(BaseModel):
    action: str

class Loop(Step):
    action: Literal["loop"]
    counter: int
    range: int
    steps: List[Step]

class RunBlock(Step):
    action: Literal["run_block"]
    block: str

class Calc(BaseModel):
    action: Literal["calc", "init", "sync", "grad", "rf", "adc", "mark", "submit"]
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

class BlockPhaseEncoding(BaseModel):
    print_counter: str
    print_message: str
    steps: List[Step]

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

class BlockTR(BaseModel):
    print_counter: str
    print_message: str
    steps: List[Step]

class Instruction(BaseModel):
    print_counter: Optional[str] = None
    print_message: str
    steps: dict[str, Step]

class RealTimeEvent(BaseModel):
    type: str
    duration: int

class RfExcitation(BaseModel):
    type: Literal["rf"]
    array: str
    duration: int
    initial_phase: int
    thickness: int
    flipangle: int
    purpose: str

class Gradient(RealTimeEvent):
    type: Literal["grad"]
    array: str
    duration: int
    tail: int
    amplitude: float

class AdcReadout(RealTimeEvent):
    type: Literal["adc"]
    samples: int
    dwelltime: int

class Ttl(RealTimeEvent):
    type: Literal["sync"]
    duration: int
    event: str

class GradientTemplate(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]

class Equation(BaseModel):
    equation: str

class PulseSequence(BaseModel):
    file: File
    settings: Settings
    infos: Infos
    instructions: dict[str, Instruction]
    objects: dict[str, RealTimeEvent]
    arrays: dict[str, GradientTemplate]
    equations: dict[str, Equation]

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

