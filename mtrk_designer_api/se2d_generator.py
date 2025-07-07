################################################################################
### mtrk project - SDL file generator designing a spin echo 2D sequence      ###
### Version 0.1.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 06/24/2025              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *
from simpleWaveformGenerator import *
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
        fov=300,
        pelines=128,
        seqstring="YARRA",
        reconstruction="%SiemensIceProgs%\\IceProgram2D")
    
    ### Generating waveforms

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
    grad_100_2560_100_amplitude = round(G_slice * 1e3, 2)  # convert to mT/m

    dt = 10  # 10 µs
    ramp = 90
    plateau = 256 * dt
    grad_100_2560_100_waveform, amp, ru_us, rd_us, pt_us = trap_grad(ramp, ramp, plateau, dt)

    # Generating slice refocusing gradient
    slice_selection_half_area = (((ramp + plateau))/2)*grad_100_2560_100_amplitude
    grad_220_80_220_waveform, grad_220_80_220_amplitude, ru_us, rd_us, pt_us = min_trap_grad(slice_selection_half_area, 22, 200, dt)

    # Generating crusher gradients
    dephasing = 10 * np.pi
    crusher_gradient_area = (dephasing*1e3) / (2*np.pi*gamma*1e-6 * 5e-3)  # in mT/m/s
    grad_220_860_220_waveform, grad_220_860_220_amplitude, ru_us, rd_us, pt_us = min_trap_grad(crusher_gradient_area, 22, 200, dt)
    
    ### Generating sequence instructions

    ## Sequence real-time events
    
    # Synchronizing with system
    sync_event = Sync(
        object="ttl",
        time=0)
    
    # Defining the repetition time (TR) event
    tr_event = Mark(time=500000)
    
    # Defining the RF excitation pulse
    rf_event = Rf(
        object="rf_excitation",
        time=100,
        added_phase= AddedPhase(
            type="float",
            float=0))

    # Defining the RF refocusing pulse
    rf_ref_event = Rf(
        object="rf_refocusing",
        time=5100,
        added_phase= AddedPhase(
            type="float",
            float=0))
    
    # Defining the gradient for slice selection excitation
    slice_gradient_event = Grad(
        axis="slice",
        object="grad_slice_select",
        time=0)
    
    # Defining the gradient for slice selection refocusing
    slice_ref_gradient_event = Grad(
        axis="slice",
        object="grad_slice_select_refocus",
        time=5000)
    
    # Defining the crusher gradients
    crusher_gradient_event_s1 = Grad(
        axis="slice",
        object="grad_crusher",
        time=3700)
    crusher_gradient_event_s2 = Grad(
        axis="slice",
        object="grad_crusher",
        time=7760)
    crusher_gradient_event_r1 = Grad(   
        axis="read",
        object="grad_crusher",
        time=3700)
    crusher_gradient_event_r2 = Grad(
        axis="read",
        object="grad_crusher",
        time=7760)   
    crusher_gradient_event_p1 = Grad(   
        axis="phase",
        object="grad_crusher",
        time=3700)
    crusher_gradient_event_p2 = Grad(
        axis="phase",
        object="grad_crusher",
        time=7760)
    
    # Defining the readout pre-encoding gradient
    readout_preenc_gradient_event = Grad(
        axis="read",
        object="grad_read_dephase",
        time=2760)
    
    # Defining the phase encoding gradient
    phase_gradient_event = Grad(
        axis="phase",
        object="grad_phase_encode",
        time=2760,
        amplitude=Amplitude(
            type="equation",
            equation="phaseencoding"))
    
    # Defining the slice selection excitation refocus gradient
    slice_refocus_gradient_event = Grad(
        axis="slice",
        object="grad_slice_refocus",
        time=2760)
    
    # Defining the readout gradient
    readout_gradient_event = Grad(
        axis="read",
        object="grad_read_readout",
        time=9430)
    
    # Defining the phase _spoiler gradient
    phase_spoiler_gradient_event = Grad(
        axis="phase",
        object="grad_phase_encode",
        time=13330,
        amplitude=Amplitude(
            type="equation",
            equation="phaseencoding"))
    
    # Defining the slice spoiler gradient
    slice_spoiler_gradient_event = Grad(    
        axis="slice",
        object="grad_slice_refocus",
        time=13330)
    
    # Defining the readout spoiler gradient
    readout_spoiler_gradient_event = Grad(
        axis="read",
        object="grad_xSpoil",
        time=13330)
    
    
    # Defining the ADC event
    adc_event = Adc(
        object="adc_readout",
        time=9460,
        frequency=0,
        phase=0,
        added_phase=AddedPhase(
            type="float",
            float=0),
        mdh={"line": {
                 "type": "counter",
                 "counter": 1
             },
             "first_scan_slice": {
                 "type": "counter",
                 "counter": 1,
                 "target": 0
             },
             "first_scan_slice": {
                 "type": "counter",
                 "counter": 1,
                 "target": 0
             },
             "last_scan_slice": {
                 "type": "counter",
                 "counter": 1,
                 "target": 127
             }}) 
    
    
    ## Corresponding objects 
    rfpulse = RfExcitation(
        array="rfpulse",
        duration=len(interleaved_magnitude_and_phase)/2 * 20,
        initial_phase=0,
        thickness=5,
        flipangle=90,
        purpose="excitation")
    
    rfpulse_refocusing = RfExcitation(
        array="rfpulse_refocusing",
        duration=len(interleaved_magnitude_and_phase)/2 * 20, 
        initial_phase=0,
        thickness=5,
        flipangle=180,
        purpose="refocusing")
    
    grad_slice_select = GradientObject(
        array="grad_100_2560_100",
        duration=len(grad_100_2560_100_waveform[0]) * 10,  
        tail=0,
        amplitude=grad_100_2560_100_amplitude)
    
    grad_slice_select_refocus = GradientObject(
        array="grad_100_2560_100",  
        duration=len(grad_100_2560_100_waveform[0]) * 10, 
        tail=0,
        amplitude=grad_100_2560_100_amplitude)
    
    grad_slice_refocus = GradientObject(
        array="grad_220_80_220",
        duration=len(grad_220_80_220_waveform[0]) * 10,  
        tail=0,
        amplitude=-grad_220_80_220_amplitude)
    
    grad_crusher = GradientObject(
        array="grad_220_860_220",
        duration=len(grad_220_860_220_waveform[0]) * 10, 
        tail=0,
        amplitude=grad_220_860_220_amplitude)
    
    grad_xSpoil = GradientObject(
        array="grad_220_860_220",
        duration=1300,
        tail=0,
        amplitude=-21.85)
    
    grad_read_dephase = GradientObject(
        array="grad_220_10_220",
        duration=230,
        tail=0,
        amplitude=-21.96)
    
    grad_read_readout = GradientObject(
        array="grad_30_3840_30",
        duration=3870,
        tail=0,
        amplitude=-2.61)
    
    grad_phase_encode = GradientObject(
        array="grad_220_10_220",
        duration=230,
        tail=0,
        amplitude=10)
    
    adc_readout = AdcReadout(
        duration=3840,
        samples=128,
        dwelltime=30000)
    
    ttl_sync = Ttl(
        duration=10,
        event="osc0")
    
    # Corresponding arrays
    rfpulse_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=len(interleaved_magnitude_and_phase)/2,
        data=interleaved_magnitude_and_phase)  
    rfpulse_refocusing_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=len(interleaved_magnitude_and_phase)/2,
        data=interleaved_magnitude_and_phase)
    grad_100_2560_100 = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_100_2560_100_waveform[0]),
        data=grad_100_2560_100_waveform[0])
    grad_220_10_220 = GradientTemplate(
        encoding="text",
        type="float",
        size=45,
        data=[0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
    grad_220_80_220 = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_220_80_220_waveform[0]),
        data=grad_220_80_220_waveform[0])
    grad_220_210_220 = GradientTemplate(
        encoding="text",
        type="float",
        size=65,
        data=[0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
    grad_220_860_220 = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_220_860_220_waveform[0]),
        data=grad_220_860_220_waveform[0])
    grad_30_3840_30 = GradientTemplate(
        encoding="text",
        type="float",
        size=389,
        data=[0.0, 0.3333, 0.6667, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6667, 0.3333, 0.0])
    
    # Corresponding equations
    phaseencoding = Equation(equation="0.3555*(ctr(2)-64.5)")
          

    ## Adding objects to the sequence data
    sequence_data.objects.update({
        "rf_excitation": rfpulse,
        "rf_refocusing": rfpulse_refocusing,
        "grad_slice_select": grad_slice_select,
        "grad_slice_select_refocus": grad_slice_select_refocus,
        "grad_slice_refocus": grad_slice_refocus,
        "grad_crusher": grad_crusher,
        "grad_xSpoil": grad_xSpoil,
        "grad_read_dephase": grad_read_dephase,
        "grad_read_readout": grad_read_readout,
        "grad_phase_encode": grad_phase_encode,
        "adc_readout": adc_readout,
        "ttl": ttl_sync
    })

    ## Adding arrays to the sequence data
    sequence_data.arrays.update({
        "rfpulse":rfpulse_array,
        "rfpulse_refocusing":rfpulse_refocusing_array,
        "grad_100_2560_100": grad_100_2560_100,
        "grad_220_10_220": grad_220_10_220,
        "grad_220_80_220": grad_220_80_220,
        "grad_220_210_220": grad_220_210_220,
        "grad_220_860_220": grad_220_860_220,
        "grad_30_3840_30": grad_30_3840_30
    })

    ## Adding equations to the sequence data
    sequence_data.equations.update({
        "phaseencoding": phaseencoding
    })
    
    ## Building the sequence structure

    # Adding the main block (looping over slices) and the core blocks: 
    # block_phaseEncoding (looping over lines), and block_TR (defining the core 
    # part of the sequence)
    sequence_data.instructions.update({
        "main":{}, 
        "block_phaseEncoding":{}, 
        "block_TR":{}})
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
        steps=[RunBlock(
            action="run_block",
            block="block_TR")])
    sequence_data.instructions["block_phaseEncoding"].steps.append(phase_encoding_loop)

    # Adding events to the TR block
    # List of events in the order they should be added to block_TR, this list
    # madatorily starts and ends with Init and Submit events
    tr_events = [
        Init(gradients="logical"),
        sync_event,
        rf_event,
        rf_ref_event,
        slice_gradient_event,
        slice_ref_gradient_event,
        crusher_gradient_event_s1,
        crusher_gradient_event_s2,
        crusher_gradient_event_r1,
        crusher_gradient_event_r2,
        crusher_gradient_event_p1,
        crusher_gradient_event_p2,
        readout_preenc_gradient_event,
        phase_gradient_event,
        slice_refocus_gradient_event,
        readout_gradient_event,
        phase_spoiler_gradient_event,
        slice_spoiler_gradient_event,
        readout_spoiler_gradient_event,
        adc_event,
        tr_event,
        Submit()
    ]
    sequence_data.instructions["block_TR"].steps.extend(tr_events)

    return sequence_data

se2d = se2d_generator()
### writing of json schema to SDL file with formatting options
## WARNING - The path needs to be adapted to your local implementation. 
with open('se2d.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(se2d.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 