################################################################################
### mtrk project - SDL file generator designing a 3D T1 MPRAGE sequence      ###
### Version 0.1.0                                                            ###
### UltraVioletAI plan-based implementation - 10/09/2026                     ###
################################################################################

from SDL_read_write.pydanticSDLHandler import *
from simpleWaveformGenerator import *
from ReadoutBlocks.mtrkReadoutBlockGenerator import add_cartesian_readout
import json
import jsbeautifier
import re
import numpy as np


def mprage_generator(
    n_x: int = 256,
    n_y: int = 256,
    n_z: int = 32,
    fov_mm: int | tuple[int, int, int] = [256, 256, 32],
    te_us: int = 4000,
    ti_us: int = 140000,
    tri_us: int = 10000,
    tr_us: int = 300000,
    flip_exc_deg: int = 12,
    exc_duration_us: int = 300,
    flip_prep_deg: int = 90,
    prep_duration_us: int = 500,
    readout_os: int = 2,
    gmax_mTm: int = 28,
    slew_mTm_ms: int = 200,
    insert_readout: bool = True,
) -> PulseSequence:
    """
    Generates a 3D T1-weighted MPRAGE sequence data object with a 90 deg preparation pulse
    and non-selective small flip GRE readout. Cartesian readout is inserted via the
    add_cartesian_readout helper.

    Returns:
        PulseSequence: The created sequence data object.
    """
    fov_x, fov_y, fov_z = tuple(float(x)*1e-3 for x in (fov_mm, fov_mm, fov_mm)) if isinstance(fov_mm, (int)) else tuple(float(x)*1e-3 for x in fov_mm)

    # Root sequence object
    sequence_data = PulseSequence()

    # Header: File and Settings
    sequence_data.file = File(
        format="Custom!",
        version=1,
        measurement="mprage_3d",
        system="Skyra-XQ",
    )

    # Settings allow extra integer values (TE/TR/TI/TREC)
    sequence_data.settings = Settings(
        readout_os=readout_os,
        TE=te_us,
        TRi=tri_us,
        TR=tr_us,
        TI=ti_us,
    )

    # Info for reconstruction and scan description
    dz = max(1, int(round(fov_z*1e3 / max(1, n_z))))
    sequence_data.infos = Info(
        description="3D T1 MPRAGE Sequence",
        slices=n_z,
        fov=int(fov_x*1e3),
        dz=dz,
        is3D=True,
        pelines=n_y,
        seqstring="MPRAGE",
        reconstruction="%SiemensIceProgs%\\IceProgram3D",
    )

    # Waveform design constants
    dt_us = 10  # 10 us time base for arrays and event durations
    gamma = 42.577e6  # Hz/T

    # RF waveforms (simple sinc placeholder)
    # Preparation RF (90 deg)
    prep_mag, prep_phase = pulse_designer("block", [int(prep_duration_us/20)])
    prep_interleaved = []
    for i in range(len(prep_mag)):
        prep_interleaved.append(prep_mag[i])
        prep_interleaved.append(prep_phase[i])
    # Excitation RF (small flip, non-selective)
    exc_mag, exc_phase = pulse_designer("block", [int(exc_duration_us/20)])
    exc_interleaved = []
    for i in range(len(exc_mag)):
        exc_interleaved.append(exc_mag[i])
        exc_interleaved.append(exc_phase[i])

    # Spoiler gradients (use ramp-sampled trapezoids on x/y/z)
    # Use modest dephasing area similar to SE sample
    dephasing = 4 * np.pi
    # Using 5 mm reference length for area derivation, consistent with se3d style placeholder
    spoil_gradient_area_x = dephasing / (2 * np.pi * gamma * 1e-6 * (fov_x / n_x)) * 1e3  # mT/m*s
    spoil_gradient_area_y = dephasing / (2 * np.pi * gamma * 1e-6 * (fov_y / n_y)) * 1e3  # mT/m*s
    spoil_gradient_area_z = dephasing / (2 * np.pi * gamma * 1e-6 * (fov_z / n_z)) * 1e3  # mT/m*s
    grad_spoil_x_wf, grad_spoil_x_amp, _, _, _ = ramp_sampled_trap_grad(
        spoil_gradient_area_x, gmax_mTm, slew_mTm_ms, dt_us
    )
    grad_spoil_y_wf, grad_spoil_y_amp, _, _, _ = ramp_sampled_trap_grad(
        spoil_gradient_area_y, gmax_mTm, slew_mTm_ms, dt_us
    )
    grad_spoil_z_wf, grad_spoil_z_amp, _, _, _ = ramp_sampled_trap_grad(
        spoil_gradient_area_z, gmax_mTm, slew_mTm_ms, dt_us
    )

    # Arrays section population
    rf_prep_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=int(len(prep_interleaved) / 2),
        data=prep_interleaved,
    )
    rf_exc_array = GradientTemplate(
        encoding="text",
        type="complex_float",
        size=int(len(exc_interleaved) / 2),
        data=exc_interleaved,
    )

    grad_spoil_x = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_spoil_x_wf[0]),
        data=grad_spoil_x_wf[0])
    grad_spoil_y = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_spoil_y_wf[0]),
        data=grad_spoil_y_wf[0])
    grad_spoil_z = GradientTemplate(
        encoding="text",
        type="float",
        size=len(grad_spoil_z_wf[0]),
        data=grad_spoil_z_wf[0])

    sequence_data.arrays.update(
        {
            "rf_prep": rf_prep_array,
            "rf_exc": rf_exc_array,
            "grad_spoil_x": grad_spoil_x,
            "grad_spoil_y": grad_spoil_y,
            "grad_spoil_z": grad_spoil_z,
        }
    )

    # Objects section population
    rf_prep_obj = RfExcitation(
        array="rf_prep",
        duration=len(prep_interleaved)/2 * 20,
        initial_phase=0,
        thickness=int(fov_z*1e3),
        flipangle=flip_prep_deg,
        purpose="preparation",
    )

    rf_excitation = RfExcitation(
        array="rf_exc",
        duration=len(exc_interleaved)/2 * 20,
        initial_phase=0,
        thickness=int(fov_z*1e3),
        flipangle=flip_exc_deg,
        purpose="excitation",
    )

    # Object    
    grad_spoil_x_obj = GradientObject(
        array="grad_spoil_x",
        duration=len(grad_spoil_x_wf[0]) * dt_us,
        tail=0,
        amplitude=grad_spoil_x_amp,
    )
    grad_spoil_y_obj = GradientObject(
        array="grad_spoil_y",
        duration=len(grad_spoil_y_wf[0]) * dt_us,
        tail=0,
        amplitude=grad_spoil_y_amp,
    )
    grad_spoil_z_obj = GradientObject(
        array="grad_spoil_z",
        duration=len(grad_spoil_z_wf[0]) * dt_us,
        tail=0,
        amplitude=grad_spoil_z_amp,
    )

    sequence_data.objects.update(
        {
            "rf_prep_obj": rf_prep_obj,
            "rf_excitation": rf_excitation,
            "grad_spoil_x_obj": grad_spoil_x_obj,
            "grad_spoil_y_obj": grad_spoil_y_obj,
            "grad_spoil_z_obj": grad_spoil_z_obj,
        }
    )

    # Instruction blocks
    sequence_data.instructions.update(
        {
            "main": {},
            "block_pe1_loop": {},
            "block_pe1": {},
            "block_TI": {},
            "block_pe2_loop": {},
            "block_pe2": {},
            "block_GRE": {},
            "block_spoiler": {},
        }
    )

    # main
    #   block_pe1_loop - loop, one loop per phase encode (pe1, y-encoding)
    #       block_pe1
    #           block_TI
    #           block_pe2_loop - loop, one loop per partition (pe2, z-encoding)
    #               block_pe2
    #                   block_GRE
    #                   add-in block cartesian-readout
    #                   block_spoiler
    #           block_recovery

    sequence_data.instructions["main"] = Instruction(
        print_counter="on", 
        print_message="Running main loop", 
        steps=[])
    sequence_data.instructions["block_pe1_loop"] = Instruction(
        print_counter="on", 
        print_message="Looping over TI-events (pe1)", 
        steps=[])
    sequence_data.instructions["block_pe1"] = Instruction(
        print_counter="on", 
        print_message="Phase Encoding", 
        steps=[])
    sequence_data.instructions["block_TI"] = Instruction(
        print_counter="on", 
        print_message="Inversion pulse, spoilers and TI", 
        steps=[])
    sequence_data.instructions["block_pe2_loop"] = Instruction(
        print_counter="on", 
        print_message="Looping over pe2-lines", 
        steps=[])
    sequence_data.instructions["block_pe2"] = Instruction(
        print_counter="on", 
        print_message="Running inner TR, slice encoding", 
        steps=[])
    sequence_data.instructions["block_GRE"] = Instruction(
        print_counter="on",
        print_message="GRE block (RF + TE)",
        steps=[])
    sequence_data.instructions["block_spoiler"] = Instruction(
        print_counter="on", 
        print_message="Spoiler and inner TR block", 
        steps=[])
    sequence_data.instructions["block_recovery"] = Instruction(
        print_counter="on", 
        print_message="Recovery delay block", 
        steps=[])

    # Loops
    main_loop = Loop(
        counter=1, 
        range=1, 
        steps=[RunBlock(
            action="run_block",
            block="block_pe1_loop")])
    sequence_data.instructions["main"].steps.append(main_loop)
    pe1_encoding_loop = Loop(
        counter=3,
        range=sequence_data.infos.pelines,
        steps=[RunBlock(block="block_pe1")])
    pe1_loop_events = [
        Init(gradients="logical"),
        pe1_encoding_loop,
        Submit()]
    sequence_data.instructions["block_pe1_loop"].steps.extend(pe1_loop_events)
    pe2_encoding_loop = Loop(
        counter=2,
        range=sequence_data.infos.slices,
        steps=[RunBlock(block="block_pe2")])
    pe2_loop_events = [
        Init(gradients="logical"),
        pe2_encoding_loop,
        Submit()]
    sequence_data.instructions["block_pe2_loop"].steps.extend(pe2_loop_events)

    # super-blocks
    pe1_events = [
        Init(gradients="logical"),
        RunBlock(block="block_TI"),
        RunBlock(block="block_pe2_loop"),
        RunBlock(block="block_recovery"),
        Submit()]
    sequence_data.instructions["block_pe1"].steps.extend(pe1_events)

    pe2_events = [
        Init(gradients="logical"),
        RunBlock(block="block_GRE"),
        RunBlock(block="block_spoiler"),
        Submit()]
    sequence_data.instructions["block_pe2"].steps.extend(pe2_events)

    # event blocks
    # block_TI
    rf_prep_event = Rf(
        object="rf_prep_obj",
        time=0,
        added_phase=AddedPhase(type="float", float=0),
    )
    # Place spoilers after prep RF (time 0 and subsequent times are absolute per block)
    spoil_x_event = Grad(axis="read", object="grad_spoil_x_obj", time=rf_prep_obj.duration + 10)
    spoil_y_event = Grad(axis="phase", object="grad_spoil_y_obj", time=rf_prep_obj.duration + 10)
    spoil_z_event = Grad(axis="slice", object="grad_spoil_z_obj", time=rf_prep_obj.duration + 10)

    equation_ref_ti = EquationRef(type="equation", equation="equation_ti_event")
    equation_ti_event = Equation(equation="set(TI)" + \
                                 " - set(TE)" + \
                                 " + " + str(rf_prep_obj.duration/2) + \
                                 " - " + str(rf_excitation.duration/2))
    ti_mark = Mark(time=equation_ref_ti)

    ti_events = [
        Init(gradients="logical"), 
        rf_prep_event, 
        spoil_x_event, 
        spoil_y_event, 
        spoil_z_event, 
        ti_mark, 
        Submit()]
    sequence_data.instructions["block_TI"].steps.extend(ti_events)

    # GRE block events (non-selective excitation)
    rf_exc_event = Rf(
        object="rf_excitation",
        time=0,
        added_phase=AddedPhase(type="float", float=0),
    )
    equation_ref_te = EquationRef(type="equation", equation="equation_te_event")
    equation_te_event = Equation(equation="set(TE) " + \
                                 " + " + str(rf_excitation.duration/2))
    te_mark = Mark(time=equation_ref_te)

    gre_events = [
        Init(gradients="logical"), 
        rf_exc_event, 
        te_mark, 
        Submit()]
    sequence_data.instructions["block_GRE"].steps.extend(gre_events)

    # Spoiler block (post readout) + TR mark
    post_spoil_x_event = Grad(axis="read", object="grad_spoil_x_obj", time=0)
    post_spoil_y_event = Grad(axis="phase", object="grad_spoil_y_obj", time=0)
    post_spoil_z_event = Grad(axis="slice", object="grad_spoil_z_obj", time=0)

    equation_ref_tri = EquationRef(type="equation", equation="equation_tri_event")
    equation_tri_event = Equation(equation="set(TRi) - set(TE) " + \
                                 " - " + str(rf_excitation.duration/2))
    tri_mark = Mark(time=equation_ref_tri)

    spoiler_events = [
        Init(gradients="logical"), 
        post_spoil_x_event, 
        post_spoil_y_event, 
        post_spoil_z_event, 
        tri_mark, 
        Submit()]
    sequence_data.instructions["block_spoiler"].steps.extend(spoiler_events)

    # Recovery block (between ky lines)
    equation_ref_tr = EquationRef(type="equation", equation="equation_tr_event")
    equation_tr_event = Equation(equation="set(TR) +set(TE) - set(TI) " + \
                                          " - " + str(n_z) + "*set(TRi)" + \
                                          " - " + str(rf_prep_obj.duration/2) + \
                                          " + " + str(rf_excitation.duration/2) )
    tr_mark = Mark(time=equation_ref_tr)

    recovery_events = [
        Init(gradients="logical"), 
        tr_mark, 
        Submit()
    ]
    sequence_data.instructions["block_recovery"].steps.extend(recovery_events)

    # Equations table
    sequence_data.equations.update(
        {
            "equation_ti_event": equation_ti_event,
            "equation_te_event": equation_te_event,
            "equation_tri_event": equation_tri_event,
            "equation_tr_event": equation_tr_event,
        }
    )

    # Insert cartesian readout into the TR pipeline and align TE/TR marks
    if insert_readout:
        add_cartesian_readout(
            sequence_data,
            "block_pe2",
            "block_GRE",
            "block_spoiler",
            sequence_data.infos.fov,
            n_x,
            dt = dt_us * 1e-6,
            gamp = gmax_mTm,
            gslew = slew_mTm_ms,
        )

    return sequence_data


mprage = mprage_generator(n_x=64, n_y=32, n_z=8, fov_mm=(256, 256, 32))
with open("mprage.mtrk", "w") as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(mprage.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 