################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from __future__ import annotations

from typing import List, Optional, Union
from typing_extensions import Literal, Any
from pydantic import BaseModel, SerializeAsAny

### file section
class File(BaseModel):
    format: str
    version: int
    measurement: str
    system: str


### settings section
class Settings(BaseModel):
    readout_os: int


### infos section
class Infos(BaseModel):
    description: str
    slices: int
    fov: int
    pelines: int
    seqstring: str
    reconstruction: str


### instructions section
step_subclass_registry = {}


class Step(BaseModel):
    action: str
    
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        step_subclass_registry[cls.__name__] = cls    

    class Config:
        extra = "allow" 


class HasSteps():
    def __init__(self, **kwargs):
        for index in range(len(kwargs['steps'])):
            current_step = kwargs['steps'][index]
            if isinstance(current_step, dict):
                item_step_keys = sorted(current_step.keys())
                for name, cls in step_subclass_registry.items():
                    registery_step_keys = sorted(cls.model_fields.keys())
                    if item_step_keys == registery_step_keys:
                        try:
                            current_step = cls(**current_step)
                        except: 
                            pass
                        break
                else:
                    raise Exception(f"Unknown step action \"{current_step['action']}\"")
                kwargs['steps'][index] = current_step
        super().__init__(**kwargs)

class Instruction(HasSteps,BaseModel):
    print_counter: Optional[str] = "off"
    print_message: str

    steps: List[SerializeAsAny[Step]]


class Loop(HasSteps,Step):
    action: Literal["loop"]
    counter: int
    range: int
    steps: List[Step]


class RunBlock(Step):
    action: Literal["run_block"]
    block: str


class Calc(Step):
    action: Literal["calc"]
    type: str
    float: int
    increment: int


class Init(Step):
    action: Literal["init"]
    gradients: str


class Sync(Step):
    action: Literal["sync"]
    object: str
    time: int


class Grad(Step):
    action: Literal["grad"]
    axis: str
    object: str
    time: int


class GradWithAmplitude(Grad):
    amplitude: Union[str, Amplitude]


class Amplitude(BaseModel):
    type: str
    equation: str


class Rf(Step):
    action: Literal["rf"]
    object: str
    time: int
    added_phase: AddedPhase


class AddedPhase(BaseModel):
    type: str
    float: int


class Adc(Step):
    action: Literal["adc"]
    object: str
    time: int
    frequency: int
    phase: int
    added_phase: AddedPhase  
    mdh: dict[str, MdhOption]


class MdhOption(BaseModel):
    type: str
    counter: int
    target: Optional[int] = None

class Mark(Step):
    action: Literal["mark"]
    time: int


class Submit(Step):
    action: Literal["submit"]


### objects section
object_subclass_registry = {}


class Object(BaseModel):
    type: str
    duration: int
    
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        object_subclass_registry[cls.__name__] = cls    

    class Config:
        extra = "allow" 


class HasObjects():
    def __init__(self, **kwargs):
        listed_objects = list(kwargs['objects'])
        for index in range(len(listed_objects)):
            current_object = listed_objects[index]
            if isinstance(current_object, dict):
                item_object_keys = sorted(current_object.keys())
                for name, cls in object_subclass_registry.items():
                    registery_step_keys = sorted(cls.model_fields.keys())
                    if item_object_keys == registery_step_keys:
                        try:
                            current_object = cls(**current_object)
                        except: 
                            pass
                        break
                else:
                    raise Exception(f"Unknown step action \"{current_object['objects']}\"")
                listed_objects[index] = current_object
        super().__init__(**kwargs)


class RfExcitation(Object):
    type: Literal["rf"]
    array: str
    duration: int
    initial_phase: int
    thickness: int
    flipangle: int
    purpose: str


class GradientObject(Object):
    type: Literal["grad"]
    array: str
    duration: int
    tail: int
    amplitude: float


class AdcReadout(Object):
    type: Literal["adc"]
    samples: int
    dwelltime: int


class Ttl(Object):
    type: Literal["sync"]
    duration: int
    event: str


### arrays section
class GradientTemplate(BaseModel):
    encoding: str
    type: str
    size: int
    data: List[float]


### equations section
class Equation(BaseModel):
    equation: str


### definition of entire SDL model
class PulseSequence(HasObjects, BaseModel):
    file: File
    settings: Settings
    infos: Infos
    instructions: dict[str, Instruction]
    objects: dict[str, SerializeAsAny[Object]]
    arrays: dict[str, GradientTemplate]
    equations: dict[str, Equation]
  