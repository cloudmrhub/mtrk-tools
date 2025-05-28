import numpy as np
import matplotlib.pyplot as plt

## Adapted and extended from the Pulpy library by J.B. Martin (https://github.com/jonbmartin/pulpy/tree/master)

def trap_grad(ramp_up, ramp_down, plateau, dt):
    r"""Trapezoidal gradient designer. Design for specific ramp up, ramp down and 
    plateau times.

    Args:
        ramp_up (float): ramp up time in sec
        ramp_down (float): ramp down time in sec
        plateau (float): plateau time in sec
        dt (float): sample time in sec

    Returns:
        2-element tuple containing

        - **trap** (*array*): gradient waveform normalized between 0 an 1.

    """

    # make a flat portion of magnitude 1 and enough area for the swath
    pts = np.floor(plateau / dt)
    flat = np.ones((1, int(pts)))

    # make attack and decay ramps
    ramp_up_pts = int(np.ceil(ramp_up / dt))
    ramp_up = np.linspace(0, ramp_up_pts, num=ramp_up_pts + 1) / ramp_up_pts * np.max(flat)
    ramp_down_pts = int(np.ceil(ramp_down / dt))
    ramp_down = np.linspace(ramp_down_pts, 0, num=ramp_down_pts + 1) / ramp_down_pts * np.max(flat)

    trap = np.concatenate((ramp_up, np.squeeze(flat), ramp_down))

    return np.expand_dims(trap, axis=0)

def min_trap_grad(area, gmax, slew, dt):
    r"""Minimal duration trapezoidal gradient designer. Design for target area
    under the flat portion (for non-ramp-sampled pulses)

    Args:
        area (float): pulse area in mT/m/s
        gmax (float): maximum gradient in mT/m
        slew (float): max slew rate in T/m/s
        dt (float): sample time in sec

    Returns:
        2-element tuple containing

        - **normalized_trap** (*array*): normalize gradient waveform between 0 an 1.
        - **amplitude** (*int*): gradient amplitude in mT/m.

    """
    slew = slew * 1e3  # convert slew rate to mT/m/s

    if np.abs(area) > 0:
        # we get the solution for plateau amp by setting derivative of
        # duration as a function of amplitude to zero and solving
        a = np.sqrt(slew * area / 2)

        # finish design with discretization
        # make a flat portion of magnitude a and enough area for the swath
        pts = np.floor(area / a / dt)
        flat = np.ones((1, int(pts)))
        flat = flat / np.sum(flat) * area / dt
        if np.max(flat) > gmax:
            flat = np.ones((1, int(np.ceil(area / gmax / dt))))
            flat = flat / np.sum(flat) * area / dt

        # make attack and decay ramps
        ramppts = int(np.ceil(np.max(flat) / slew / dt))
        ramp_up = np.linspace(0, ramppts, num=ramppts + 1) / ramppts * np.max(flat)
        ramp_dn = np.linspace(ramppts, 0, num=ramppts + 1) / ramppts * np.max(flat)

        trap = np.concatenate((ramp_up, np.squeeze(flat), ramp_dn))

    else:
        # negative-area trap requested?
        trap, ramppts = 0, 0

    amplitude = np.max(np.abs(trap))
    normalized_trap = trap / amplitude

    return np.expand_dims(normalized_trap, axis=0), amplitude


def ramp_sampled_trap_grad(area, gmax, slew, dt, *args):
    r"""General trapezoidal gradient designer for total target area
    (for rewinders)

    Args:
        area (float): pulse area in mT/m/s
        gmax (float): maximum gradient in mT/m
        slew (float): max slew rate in T/m/s
        dt (float): sample time in sec

    Returns:
        2-element tuple containing

        - **normalized_trap** (*array*): normalize gradient waveform between 0 an 1.
        - **amplitude** (*int*): gradient amplitude in mT/m.

    """

    slew = slew * 1e3  # convert slew rate to mT/m/s

    if len(args) < 5:
        # in case we are making a rewinder
        rampsamp = 1

    if np.abs(area) > 0:
        if rampsamp:
            ramppts = int(np.ceil(gmax / slew / dt))
            triareamax = ramppts * dt * gmax
            sign = 1
            if area<0:
                area = -area
                sign = -1
            if triareamax > np.abs(area):
                # triangle pulse
                newgmax = np.sqrt(np.abs(area) * slew)
                ramppts = int(np.ceil(newgmax / slew / dt))
                ramp_up = np.linspace(0, ramppts, num=ramppts + 1) / ramppts
                ramp_dn = np.linspace(ramppts, 0, num=ramppts + 1) / ramppts
                pulse = sign * np.concatenate((ramp_up, ramp_dn))
            else:
                # trapezoid pulse
                nflat = int(np.ceil((area - triareamax) / gmax / dt / 2) * 2)
                # nflat = np.abs(nflat) # this is a test
                ramp_up = np.linspace(0, ramppts, num=ramppts + 1) / ramppts
                ramp_dn = np.linspace(ramppts, 0, num=ramppts + 1) / ramppts
                pulse = sign * np.concatenate((ramp_up, np.ones(nflat), ramp_dn))

            trap = pulse * (area / (sum(pulse) * dt))

        else:
            # make a flat portion of magnitude gmax
            # and enough area for the entire swath
            flat = np.ones(1, np.ceil(area / gmax / dt))
            flat = flat / sum(flat) * area / dt
            flat_top = np.max(flat)

            # make attack and decay ramps
            ramppts = int(np.ceil(np.max(flat) / slew / dt))
            ramp_up = np.linspace(0, ramppts, num=ramppts + 1) / ramppts * flat_top
            ramp_dn = np.linspace(ramppts, 0, num=ramppts + 1) / ramppts * flat_top
            trap = np.concatenate((ramp_up, flat, ramp_dn))

    else:
        trap, ramppts = 0, 0

    amplitude = np.max(np.abs(trap))
    normalized_trap = trap / amplitude

    return np.expand_dims(normalized_trap, axis=0), amplitude

print("Tests for simpleWaveformGenerator.py")
def test_trap_grad():
    trap = trap_grad(30e-5, 60e-5, 200e-5, 1e-5)
    plt.plot(trap[0])
    plt.title("Trapezoidal Gradient Waveform")
    plt.xlabel("Time (us)")
    plt.ylabel("Gradient (mT/m)")
    plt.show()

def test_min_trap_grad():   
    morm_trap, ampl = min_trap_grad(200e-5, 20, 200, 1e-5)
    plt.plot(morm_trap[0]*ampl)
    plt.title("Minimal Duration Trapezoidal Gradient Waveform")
    plt.xlabel("Time (us)")
    plt.ylabel("Gradient (mT/m)")
    plt.show()

def test_ramp_sampled_trap_grad():      
    morm_trap, ampl = ramp_sampled_trap_grad(200e-5, 20, 200, 1e-5)
    plt.plot(morm_trap[0]*ampl)
    plt.title("Ramp Sampled Trapezoidal Gradient Waveform")
    plt.xlabel("Time (us)")
    plt.ylabel("Gradient (mT/m)")
    plt.show()

# Run tests
# test_trap_grad()
# test_min_trap_grad()
# test_ramp_sampled_trap_grad()