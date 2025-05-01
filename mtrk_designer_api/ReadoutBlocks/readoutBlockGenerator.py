from mtrkReadoutBlockGenerator import *
import json
import jsbeautifier
import re


inputFilename = 'C:/Users/artiga02/mtrk_designer_gui/app/mtrk_designer_api/raw_seq_pulpy.mtrk'

readoutList = ["cartesian", "radial", "spiral", "epi"]
readoutType = readoutList[0] # type of readout to add
outputFilename = 'C:/Users/artiga02/Downloads/se2d_' + str(readoutType) + '.mtrk'
insertion_block = "block_spinEcho" # block name to insert 
previous_block = "block_refocusing" # previous step name

## Generating a readout block and inserting it in the base sequence
## Getting fov and resolution from base sequence
def automaticReadoutBlockGenerator(readoutType = readoutType, inputFilename = inputFilename, 
                          insertion_block = insertion_block, previous_block = previous_block):
    ## Opening the base sequence file and loading it into a PulseSequence object
    with open(inputFilename) as sdlFile:
        sdlData = json.load(sdlFile)
        base_sequence = PulseSequence(**sdlData)

    ## Setting the fov and resolution according to the base sequence object
    fov = base_sequence.infos.fov * 1e-2 # imaging field of view
    resolution = base_sequence.infos.pelines # resolution

    ## Adding the readout block to the base sequence
    if readoutType == "cartesian":
        output_sequence = add_cartesian_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "radial":
        output_sequence = add_radial_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "spiral":
        output_sequence = add_spiral_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "epi":
        output_sequence = add_epi_readout(base_sequence, insertion_block, previous_block, fov, resolution)

    ## Generating the output sequence file
    with open(outputFilename, 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(json.dumps(output_sequence.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 

## Generating a readout block and inserting it in the base sequence
## Force setting fov and resolution
def manualReadoutBlockGenerator(readoutType = readoutType, inputFilename = inputFilename, 
                          insertion_block = insertion_block, previous_block = previous_block,
                          fov = 260, resolution = 128):
    ## Opening the base sequence file and loading it into a PulseSequence object
    with open(inputFilename) as sdlFile:
        sdlData = json.load(sdlFile)
        base_sequence = PulseSequence(**sdlData)

    ## Setting the base sequence fov and resolution according to the provided values
    base_sequence.infos.fov = fov # imaging field of view
    fov = fov * 1e-2
    base_sequence.infos.pelines = resolution # resolution (warning, this is not changing the iteration number for now)
    
    ## Adding the readout block to the base sequence
    if readoutType == "cartesian":
        output_sequence = add_cartesian_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "radial":
        output_sequence = add_radial_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "spiral":
        output_sequence = add_spiral_readout(base_sequence, insertion_block, previous_block, fov, resolution)
    elif readoutType == "epi":
        output_sequence = add_epi_readout(base_sequence, insertion_block, previous_block, fov, resolution)

    ## Generating the output sequence file
    with open(outputFilename, 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(json.dumps(output_sequence.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic

## Testing functions
# automaticReadoutBlockGenerator(readoutType = readoutType, inputFilename = inputFilename,
#                          insertion_block = insertion_block, previous_block = previous_block)
# manualReadoutBlockGenerator(readoutType = readoutType, inputFilename = inputFilename,
#                          insertion_block = insertion_block, previous_block = previous_block,
#                          fov = 260, resolution = 128)































# max_gx = np.max(np.abs(gx))
# max_gy = np.max(np.abs(gy))

# normalized_gx = gx / max_gx
# normalized_gy = gy / max_gy






# counts = Counter(normalized_gx)
# max_occurrence_count = max(counts.values())
# max_occurrence_nums = [num for num, count in counts.items() if count == max_occurrence_count]

# adc = np.zeros(len(normalized_gx))
# for index in range(0,len(normalized_gx)-1):
#     for value in max_occurrence_nums:
#         if normalized_gx[index] == value:
#             adc[index] = 1

# def count_consecutive_number(arr, number):
#     max_count = 0
#     current_count = 0
    
#     for num in arr:
#         if num == number:
#             current_count += 1  # Increment count for consecutive number's
#             max_count = max(max_count, current_count)  # Update the maximum streak
#         else:
#             current_count = 0  # Reset count when encountering 0 or another number
    
#     return max_count

# consecutive_ones = count_consecutive_number(adc, 1)
# consecutive_zeros = count_consecutive_number(adc, 0)

# def count_pattern(arr, pattern):
#     # Convert the list into a numpy array
#     arr = np.array(arr)
#     pattern_len = len(pattern)
    
#     # Create a sliding window and compare with the pattern
#     count = 0
#     for i in range(len(arr) - pattern_len + 1):
#         if np.array_equal(arr[i:i + pattern_len], pattern):
#             count += 1
            
#     return count

# arr = adc
# pattern_ones = np.ones(consecutive_ones)
# number_of_patterns_ones = count_pattern(arr, pattern_ones)
# print(f"The pattern {pattern_ones} appears {number_of_patterns_ones} times.")
# pattern_zeros = np.zeros(consecutive_zeros)
# number_of_patterns_zeros = count_pattern(arr, pattern_zeros)
# print(f"The pattern {pattern_zeros} appears {number_of_patterns_zeros} times.")

# subplot, axis = plt.subplots(3, sharex=True)
# subplot.suptitle("normalized EPI trajectory")
# axis[0].set_title("normalized_gy, amplitude = " + str(max_gy))
# axis[0].plot(normalized_gy, label='gy')
# axis[1].set_title("normalized_gx, amplitude = " + str(max_gx))
# axis[1].plot(normalized_gx, label='gx')
# axis[2].set_title("adc")
# axis[2].plot(adc, label='adc')
# plt.show()






# full_duration = t[np.shape(t)[0]-1] / dt
# file = open("test_pulpy.txt", "w")
# np.set_printoptions(threshold=np.inf)
# np.set_printoptions(linewidth=np.inf)
# file.write(np.array2string(normalized_gx, precision=4, separator=', ') + "\n\n" + np.array2string(normalized_gy, precision=4, separator=', ') + "\n\n" + str(full_duration) + "\n" + str(max_gx) + "\n" + str(max_gy))







# k = np.array([[0, 0], [1, 1], [2,2],[3,3]]) # spokes locations, [Nspokes, 2]
# print(k[0])
# tbw = 4 # time bandwidth product.
# sl_thick = 4 # slice thickness (mm).
# gmax = 20 # max gradient amplitude (g/cm).
# dgdtmax = 200 # max gradient slew (g/cm/s).
# gts = 1e-5 # hardware sampling dwell time (s).
# gx_rad, gy_rad, gz_rad = mpp.spokes_grad(k, tbw, sl_thick, gmax, dgdtmax, gts)

# subplot, axis = plt.subplots(3, sharex=True)
# subplot.suptitle("Radial trajectory")
# axis[0].set_title("gx_rad")
# axis[0].plot(gx_rad, label='gx')
# axis[1].set_title("gy_rad")
# axis[1].plot(gy_rad, label='gy')
# axis[2].set_title("gz_rad")
# axis[2].plot(gz_rad, label='gz')
# plt.show()