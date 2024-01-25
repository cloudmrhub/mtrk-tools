import numpy as np
import sys
import math 
import pypulseq
from types import SimpleNamespace
import matplotlib.pyplot as plt

def pulseqConverter(sequence_data):
    fillSequence(sequence_data, plot=True, write_seq=True)

def fillSequence(sequence_data, plot: bool, write_seq: bool, seq_filename: str = "sdl_pypulseq.seq"):
    # ======
    # SETUP
    # ======
    # Create a new sequence object
    seq = pypulseq.Sequence()
    fov = sequence_data.infos.fov*1e-3  # Define FOV and resolution
    Nx = sequence_data.objects["adc_readout"].samples
    Ny = sequence_data.infos.pelines
    # Nx = 2
    # Ny = 2
    alpha = sequence_data.objects["rf_excitation"].flipangle  # flip angle
    slice_thickness = sequence_data.objects["rf_excitation"].thickness*1e-3  # slice
    TR = 10e-3  # Repetition time # !!! TO DO add to SDL format
    TE = 20e-3  # Echo time # !!! TO DO add to SDL format

    for step in sequence_data.instructions["block_TR"].steps:
        if step.action == "calc" and step.type == "float_rfspoil":
            increment = step.increment
    rf_spoiling_inc = increment  # RF spoiling increment

    # !!! TO DO add these info to SDL
    system = pypulseq.Opts(
        max_grad=28,
        grad_unit="mT/m",
        max_slew=150,
        slew_unit="T/m/s",
        rf_ringdown_time=20e-6,
        rf_dead_time=100e-6,
        adc_dead_time=10e-6,
    )

    # ======
    # CREATE EVENTS
    # ======

    rf_signal_array=[]
    # rf_amplitude = 10 # !!! TO DO evaluate actual RF amplitude according to flip angle
    for value_counter in range(0, len(sequence_data.arrays[sequence_data.objects["rf_excitation"].array].data)):
        if value_counter%2 == 0:
            rf_signal_array.append(sequence_data.arrays[sequence_data.objects["rf_excitation"].array].data[value_counter])
        else:
            pass
    
    rf_dwell_time = sequence_data.objects["rf_excitation"].duration/sequence_data.arrays[sequence_data.objects["rf_excitation"].array].size
    rf_bandwidth = 2.7/sequence_data.objects["rf_excitation"].duration*1e6
    rf = pypulseq.make_arbitrary_rf(
        signal=np.array(rf_signal_array),
        flip_angle=alpha * math.pi / 180,
        bandwidth=rf_bandwidth, # !!! TO DO verify is this value is okay, see if BW*time=2.7
        delay=0,
        dwell=rf_dwell_time*1e-6, 
        freq_offset=0,
        no_signal_scaling=False,
        max_grad=0,
        max_slew=0,
        phase_offset=0,
        return_delay=False,
        return_gz=False,
        slice_thickness=slice_thickness,
        system=system,
        time_bw_product=2.7,
        use="excitation"     
    )

    # Plot RF
    # np.set_printoptions(threshold=sys.maxsize)
    # plt.plot(np.arange(len(rf.signal)), rf.signal)
    # # plt.plot(np.arange(len(rf_signal_array)), rf_signal_array)
    # plt.show()
    # print(sequence_data.arrays[sequence_data.objects["rf_excitation"].array].data)

    # Define other gradients and ADC events
    # print(sequence_data.arrays[sequence_data.objects["grad_read_readout"].array].data)
    # sequence_data.objects["grad_read_readout"].amplitude

    # !!! TO DO automate with the sdl file readout of gradient type objects
    gx_grad_read_readout = pypulseq.make_arbitrary_grad(
        channel='x',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_read_readout"].array].data),
        delay=0,
        system=system
    )

    gx_grad_read_dephase = pypulseq.make_arbitrary_grad(
        channel='x',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_read_dephase"].array].data),
        delay=0,
        system=system
    )

    gy_grad_phase_encode = pypulseq.make_arbitrary_grad(
        channel='y',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_phase_encode"].array].data),
        delay=0,
        system=system
    )

    gy_grad_phase_spoil = pypulseq.make_arbitrary_grad(
        channel='y',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_phase_encode"].array].data)*-1,
        delay=0,
        system=system
    )

    gz_grad_slice_select = pypulseq.make_arbitrary_grad(
        channel='z',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_slice_select"].array].data)*-1,
        delay=0,
        system=system
    )

    gz_grad_slice_refocus = pypulseq.make_arbitrary_grad(
        channel='z',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_slice_refocus"].array].data),
        delay=0,
        system=system
    )

    gz_grad_slice_spoil = pypulseq.make_arbitrary_grad(
        channel='z',
        waveform=np.array(sequence_data.arrays[sequence_data.objects["grad_slice_refocus"].array].data)*-1,
        delay=0,
        system=system
    )

    # !!! TO DO generalize ramp time calculation
    adc_delay = sequence_data.objects["grad_read_readout"].duration - sequence_data.objects["adc_readout"].duration
    adc = pypulseq.make_adc(
        num_samples=Nx, duration=sequence_data.objects["adc_readout"].duration*1e-6, delay=adc_delay*1e-6, system=system
    )
    delta_k = 1 / fov
    phase_areas = (np.arange(Ny) - Ny / 2) * delta_k

    # delta_k = 1 / fov
    # gx = pypulseq.make_trapezoid(
    #     channel="x", flat_area=Nx * delta_k, flat_time=3.2e-3, system=system
    # )
    # adc = pypulseq.make_adc(
    #     num_samples=Nx, duration=gx.flat_time, delay=gx.rise_time, system=system
    # )
    # gx_pre = pypulseq.make_trapezoid(
    #     channel="x", area=-gx.area / 2, duration=1e-3, system=system
    # )
    # gz_reph = pypulseq.make_trapezoid(
    #     channel="z", area=-gz.area / 2, duration=1e-3, system=system
    # )
    # phase_areas = (np.arange(Ny) - Ny / 2) * delta_k

    # # gradient spoiling
    # gx_spoil = pypulseq.make_trapezoid(channel="x", area=2 * Nx * delta_k, system=system)
    # gz_spoil = pypulseq.make_trapezoid(channel="z", area=4 / slice_thickness, system=system)

    # Calculate timing
    # !!! TO DO understand what is happening and correct
    delay_TE = (
        np.ceil(
            (
                TE
                - pypulseq.calc_duration(gx_grad_read_dephase)
                - pypulseq.calc_duration(gz_grad_slice_select) / 2
                - pypulseq.calc_duration(gx_grad_read_readout) / 2
            )
            / seq.grad_raster_time
        )
        * seq.grad_raster_time
    )

    delay_TR = (
        np.ceil(
            (
                TR
                - pypulseq.calc_duration(gz_grad_slice_select)
                - pypulseq.calc_duration(gx_grad_read_dephase)
                - pypulseq.calc_duration(gx_grad_read_readout)
                - delay_TE
            )
            / seq.grad_raster_time
        )
        * seq.grad_raster_time
    )

    # assert np.all(delay_TE >= 0)
    # assert np.all(delay_TR >= pypulseq.calc_duration(gx_grad_read_dephase, gz_grad_slice_refocus))

    rf_phase = 0
    rf_inc = 0

    # ======
    # CONSTRUCT SEQUENCE
    # ======
    # Loop over phase encodes and define sequence blocks
    for i in range(Ny):
        rf.phase_offset = rf_phase / 180 * np.pi
        adc.phase_offset = rf_phase / 180 * np.pi
        rf_inc = divmod(rf_inc + rf_spoiling_inc, 360.0)[1]
        rf_phase = divmod(rf_phase + rf_inc, 360.0)[1]

        seq.add_block(rf, gz_grad_slice_select)
        gy_pre = pypulseq.make_trapezoid(
            channel="y",
            area=phase_areas[i],
            duration=pypulseq.calc_duration(gx_grad_read_dephase),
            system=system,
        )
        seq.add_block(gx_grad_read_dephase, gy_grad_phase_encode, gz_grad_slice_refocus)
        seq.add_block(pypulseq.make_delay(delay_TE))
        seq.add_block(gx_grad_read_readout, adc)
        
        # !!! TO DO handle spoiling
        # gy_grad_phase_encode.amplitude = -gy_grad_phase_encode.amplitude
        # gx_grad_read_dephase.amplitude = -gy_grad_phase_encode.amplitude
        # gz_grad_slice_refocus.amplitude = -gy_grad_phase_encode.amplitude
        seq.add_block(pypulseq.make_delay(TR), gy_grad_phase_spoil, gz_grad_slice_spoil)

    # Check whether the timing of the sequence is correct
    ok, error_report = seq.check_timing()
    if ok:
        print("Timing check passed successfully")
    else:
        print("Timing check failed. Error listing follows:")
        [print(e) for e in error_report]

    # ======
    # VISUALIZATION
    # ======
    if plot:
        seq.plot()

    seq.calculate_kspace()

    # Very optional slow step, but useful for testing during development e.g. for the real TE, TR or for staying within
    # slew-rate limits
    rep = seq.test_report()
    print(rep)

    # =========
    # WRITE .SEQ
    # =========
    if write_seq:
        # Prepare the sequence output for the scanner
        seq.set_definition(key="FOV", value=[fov, fov, slice_thickness])
        seq.set_definition(key="Name", value="gre")

        seq.write(seq_filename)

