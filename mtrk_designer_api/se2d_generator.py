################################################################################
### mtrk project - SDL file generator designing a spin echo 2D sequence      ###
### Version 0.1.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 06/24/2025              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *
from simpleWaveformGenerator import *
from ReadoutBlocks.mtrkReadoutBlockGenerator import add_cartesian_readout
import json
import jsbeautifier
import re

def se2d_generator():
    """
    Generates a spin echo 2D sequence data object.

    Args:

    Returns:
        SequenceData: The created sequence data object.
    """

    ### Creating the sequence data object
    sequence_data = PulseSequence()
    
    ### Filling the header part of the SDL file

    ## Sequence file and system technical specifications
    sequence_data.file = File(
        format="Custom!",
        version=1,
        measurement="abc",
        system="Skyra-XQ")

    ## Sequence-related general settings
    sequence_data.settings = Settings(
        readout_os=2)
    
    ## Information for reconstruction
    sequence_data.infos = Info(
        description="Spin Echo 2D Sequence",
        slices=1,
        fov=260,
        pelines=128,
        seqstring="YARRA",
        reconstruction="%SiemensIceProgs%\\IceProgram2D")
    
    ### Calculating waveforms

    ## RF excitation and refocusing pulse

    # Generating the RF pulse
    magnitude, phase = pulse_designer("sinc", [128, 1])
    # preparing the interleaved format for SDL
    interleaved_magnitude_and_phase = [] 
    for i in range(len(magnitude)):
        interleaved_magnitude_and_phase.append(magnitude[i])
        interleaved_magnitude_and_phase.append(phase[i])

    # Generating slice selection gradient
    gamma = 42.576e6  # Hz/T
    time_bw_product = 2.7
    BW = time_bw_product/(2560e-6)  # RF bandwidth in Hz
    dz = 0.005  # slice thickness in meters
    G_slice = BW / (gamma * dz)  # in T/m
    grad_slisel_amplitude = round(G_slice * 1e3, 2)  # convert to mT/m

    dt = 10  # 10 µs
    ramp = 90
    plateau = 256 * dt
    grad_slisel_waveform, amp, grad_slisel_ru_us, rd_us, pt_us = trap_grad(ramp, ramp, plateau, dt)

    # Generating slice refocusing gradient
    slice_selection_half_area = (((ramp + plateau))/2)*grad_slisel_amplitude
    grad_sliref_waveform, grad_sliref_amplitude, ru_us, rd_us, pt_us = min_trap_grad(slice_selection_half_area, 22, 200, dt)

    # Generating crusher gradients
    dephasing = 10 * np.pi
    crusher_gradient_area = (dephasing*1e3) / (2*np.pi*gamma*1e-6 * 5e-3)  # in mT/m/s
    grad_crush_waveform, grad_crush_amplitude, ru_us, rd_us, pt_us = min_trap_grad(crusher_gradient_area, 22, 150, dt)
    for i, value in enumerate(grad_crush_waveform[0]):
        grad_crush_waveform[0][i] = np.round(value, 4)  # rounding to 4 decimal places for mT/m

    ### Generating sequence instructions

    ## Sequence real-time events
    TE = 20000  # Echo time in us
    TR = 5000000  # Repetition time in us
    
    # Synchronizing with system
    # Object
    ttl_sync = Ttl(
        duration=10,
        event="osc0")
    
    # Event
    sync_event = Sync(
        object="ttl",
        time=0)

    # Defining the gradient for slice selection excitation
    # Array
    grad_slisel = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_slisel_waveform[0]),
        data=grad_slisel_waveform[0])

    # Object
    grad_slice_select = GradientObject(
        array="grad_slisel",
        duration=len(grad_slisel_waveform[0]) * 10,  
        tail=0,
        amplitude=grad_slisel_amplitude)
    
    # Event
    slice_gradient_event = Grad(
        axis="slice",
        object="grad_slice_select",
        time=0)
    
    # Defining the RF excitation pulse
    # Array
    rfpulse_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=len(interleaved_magnitude_and_phase)/2,
        data=interleaved_magnitude_and_phase)  
    
    # Object
    rfpulse = RfExcitation(
        array="rfpulse",
        duration=len(interleaved_magnitude_and_phase)/2 * 20,
        initial_phase=0,
        thickness=5,
        flipangle=90,
        purpose="excitation")
    
    # Event
    rf_event = Rf(
        object="rf_excitation",
        time=grad_slisel_ru_us * 1e-6,
        added_phase= AddedPhase(
            type="float",
            float=0))
    
    # Defining the gradient for slice selection refocusing
    # Array
    grad_sliref = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_sliref_waveform[0]),
        data=grad_sliref_waveform[0])
    
    # Object
    grad_slice_select_refocusing = GradientObject(
        array="grad_sliref",  
        duration=len(grad_sliref_waveform[0]) * 10, 
        tail=0,
        amplitude=-grad_sliref_amplitude)

    # Event
    slice_refocus_gradient_event = Grad(
        axis="slice",
        object="grad_slice_select_refocusing",
        time=grad_slice_select.duration + 10)
    
    # Defining the gradient for slice selection refocus of se
    # Object
    grad_slice_select_refocus = GradientObject(
        array="grad_slisel",  
        duration=len(grad_slisel_waveform[0]) * 10, 
        tail=0,
        amplitude=grad_slisel_amplitude)
    
    # Event
    slice_ref_gradient_event = Grad(
        axis="slice",
        object="grad_slice_select_refocus",
        time=TE/2 - grad_slice_select_refocus.duration/2)
    
    # Defining the crusher gradients
    # Array
    grad_crush = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_crush_waveform[0]),
        data=grad_crush_waveform[0])
    
    # Object
    grad_crusher = GradientObject(
        array="grad_crush",
        duration=len(grad_crush_waveform[0]) * 10, 
        tail=0,
        amplitude=grad_crush_amplitude)
    
    # Events
    crusher_gradient_event_s1 = Grad(
        axis="slice",
        object="grad_crusher",
        time=TE/2 - grad_slice_select_refocus.duration/2 - grad_crusher.duration - 20)
    crusher_gradient_event_r1 = Grad(   
        axis="read",
        object="grad_crusher",
        time=TE/2 - grad_slice_select_refocus.duration/2 - grad_crusher.duration - 20)
    crusher_gradient_event_p1 = Grad(   
        axis="phase",
        object="grad_crusher",
        time=TE/2 - grad_slice_select_refocus.duration/2 - grad_crusher.duration - 20)

    # Defining the RF refocusing pulse for se
    # Array
    rfpulse_refocusing_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=len(interleaved_magnitude_and_phase)/2,
        data=interleaved_magnitude_and_phase)
    
    # Object
    rfpulse_refocusing = RfExcitation(
        array="rfpulse_refocusing",
        duration=len(interleaved_magnitude_and_phase)/2 * 20, 
        initial_phase=0,
        thickness=5,
        flipangle=180,
        purpose="refocusing")

    # Event    
    rf_ref_event = Rf(
        object="rf_refocusing",
        time=TE/2 - rfpulse_refocusing.duration/2 + 20,
        added_phase= AddedPhase(
            type="float",
            float=0))
    
    # Defining the crusher gradients
    # Events
    crusher_gradient_event_s2 = Grad(
        axis="slice",
        object="grad_crusher",
        time=TE/2 + grad_slice_select_refocus.duration/2 + 20)
    crusher_gradient_event_r2 = Grad(
        axis="read",
        object="grad_crusher",
        time=TE/2 + grad_slice_select_refocus.duration/2 + 20)   
    crusher_gradient_event_p2 = Grad(
        axis="phase",
        object="grad_crusher",
        time=TE/2 + grad_slice_select_refocus.duration/2 + 20)

    # Defining the echo time (TE) event
    te_event = Mark(time=TE + grad_slice_select.duration/2 )
    
    
    # Defining the spoiler gradient
    # Object
    grad_spoiler = GradientObject(
        array="grad_crush",
        duration=len(grad_crush_waveform[0]) * 10, 
        tail=0,
        amplitude=grad_crush_amplitude)
    
    # Event
    # Note: the spoiler will be in a different block, the timing starts at 0.
    slice_spoiler_gradient_event = Grad(    
        axis="slice",
        object="grad_spoiler",
        time=0)

    
    # Defining the repetition time (TR) event
    tr_event = Mark(time=TR - crusher_gradient_event_s1.time - grad_crusher.duration)
    

    ## Adding objects to the sequence data
    sequence_data.objects.update({
        "rf_excitation": rfpulse,
        "rf_refocusing": rfpulse_refocusing,
        "grad_slice_select": grad_slice_select,
        "grad_slice_select_refocus": grad_slice_select_refocus,
        "grad_slice_select_refocusing": grad_slice_select_refocusing,
        "grad_crusher": grad_crusher,
        "grad_spoiler": grad_spoiler,
        "ttl": ttl_sync
    })

    ## Adding arrays to the sequence data
    sequence_data.arrays.update({
        "rfpulse":rfpulse_array,
        "rfpulse_refocusing":rfpulse_refocusing_array,
        "grad_slisel": grad_slisel,
        "grad_sliref": grad_sliref,
        "grad_crush": grad_crush
    })
    
    ## Building the sequence structure

    # Adding the main block (looping over slices) and the core blocks: 
    # block_phaseEncoding (looping over lines), and block_TR (defining the core 
    # part of the sequence)
    sequence_data.instructions.update({
        "main":{}, 
        "block_phaseEncoding":{}, 
        "block_TR":{},
        "block_SE":{},
        "block_spoiler":{}
    })
    sequence_data.instructions["main"] = Instruction(
        print_counter="on",
        print_message="Running main loop",
        steps=[])
    sequence_data.instructions["block_phaseEncoding"] = Instruction(
        print_counter="on",
        print_message="Looping over lines",
        steps=[])
    sequence_data.instructions["block_TR"] = Instruction(
        print_counter="on",
        print_message="Running TR Loop",
        steps=[])
    sequence_data.instructions["block_SE"] = Instruction(
        print_counter="on",
        print_message="Performing SE excitation and refocusing",
        steps=[])
    sequence_data.instructions["block_spoiler"] = Instruction(
        print_counter="on",
        print_message="Applying spoilers and delay to TR",
        steps=[])
    
    # Creating loop structures
    main_loop = Loop(
        counter=1,
        range=1,
        steps=[RunBlock(
            action="run_block",
            block="block_phaseEncoding")])
    sequence_data.instructions["main"].steps.append(main_loop)
    phase_encoding_loop = Loop(
        counter=2,
        range=128,
        steps=[RunBlock(block="block_TR")])
    pe_events = [
        Init(gradients="logical"),
        phase_encoding_loop,
        Submit()]
    sequence_data.instructions["block_phaseEncoding"].steps.extend(pe_events)
    spinech_events = [
        Init(gradients="logical"),
        RunBlock(block="block_SE"),
        RunBlock(block="block_spoiler"),
        Submit()]
    sequence_data.instructions["block_TR"].steps.extend(spinech_events)
   

    # Adding events to the TR block
    # List of events in the order they should be added to block_TR, this list
    # madatorily starts and ends with Init and Submit events
    se_events = [
        Init(gradients="logical"),
        sync_event,
        rf_event,
        rf_ref_event,
        slice_gradient_event,
        slice_refocus_gradient_event,
        slice_ref_gradient_event,
        crusher_gradient_event_s1,
        crusher_gradient_event_s2,
        crusher_gradient_event_r1,
        crusher_gradient_event_r2,
        crusher_gradient_event_p1,
        crusher_gradient_event_p2,
        te_event,
        Submit()
    ]
    sequence_data.instructions["block_SE"].steps.extend(se_events)

    spoiler_events = [
        Init(gradients="logical"),
        # phase_spoiler_gradient_event,
        slice_spoiler_gradient_event,
        # readout_spoiler_gradient_event,
        tr_event,
        Submit()
    ]
    sequence_data.instructions["block_spoiler"].steps.extend(spoiler_events)

    ## Adding the cartesian readout to the prepared sequence
    add_cartesian_readout(sequence_data, 
                          "block_TR", 
                          "block_SE", 
                          sequence_data.infos.fov * 1e-2,
                          sequence_data.infos.pelines)

    return sequence_data

se2d = se2d_generator()
### writing of json schema to SDL file with formatting options
## WARNING - The path needs to be adapted to your local implementation. 
with open('se2d.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(se2d.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 