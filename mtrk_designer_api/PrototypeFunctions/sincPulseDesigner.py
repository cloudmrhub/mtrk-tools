import numpy as np
import matplotlib.pyplot as plt

# bandwidth = 1053 # in Hz
bandwidth = 2107.7 # in Hz
to = (1/bandwidth)*1e6 # half-width of the central lobe in micro seconds
alpha = 0.46 # 0.46 for Hamming, 0.5 for Hanning
Nl = 3 # number of lobes
rf_raster_time = 20 # in micro seconds
rf_duration = 2560 # in micro seconds

# Generating raw waveform for magnitude
t = np.linspace(-Nl*to, Nl*to, rf_duration)
raw_waveform = (to*((1-alpha)+alpha*np.cos((np.pi*t)/(Nl*to))))*(np.sin((np.pi*t)/to)/(np.pi*t))

plt.plot(t, raw_waveform)
plt.show()

# Generating raw waveform for phase
raw_waveform_phase = np.zeros(rf_duration)

# Adjusting the waveforms to raster time and rf pulse format (mag, phase, mag, phase, ...)
number_of_points = int(rf_duration/rf_raster_time)
waveform = []
for i in range(0, len(raw_waveform)):
    if i%rf_raster_time == 0:
        waveform.append(abs(raw_waveform[i]))
        waveform.append(raw_waveform_phase[i])

plt.plot(waveform)
plt.show()

print(waveform)

    
