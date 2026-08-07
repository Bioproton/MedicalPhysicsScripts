"""
Uses NCASE and ATRACK times recorded in FLUKA MC simulations and 
beam current plus cyclotron frequencies to translate relative time 
stamps in FLUKA to global time stamps.
"""
import math

def convert_time(NCASE, ATRACK, beam_current=2, cyclotron_frequency=106.3, time_structure="pulsed"):
    """
    Input:
    NCASE: FLUKA parameter. If simulating 1000 protons, NCASE will vary from 1 to 1000 (or 0 to 999, not sure)
    ATRACK [µs]: FLUKA parameter. Relative time between primary proton generation and current interaction
    beam_current [nA]: Current from beam nozzle. Default 2 nA
    cylcotron frequency [MHz]: RF frequency from cylotron. Decides how often proton bunches arrive. Default 106.3 MHz (IBA). Varian ProBeam 360: 72.8 MHz
    time_structure ["pulsed", "continuous"]: Approximates protons as continuous in arrival or as proton bunches. Default "pulsed"

    Output: 
    Global time [µs]
    """

    proton_charge = 1.6e-19 # Coloumbs
    cyclotron_frequency = cyclotron_frequency * 1e6 # Convertion from MHz to Hz.

    cyclotron_period = 1 / cyclotron_frequency  # Gives cycle length per cycle. 9.41 ns for 106.3 MHz
    proton_rate = (beam_current * 1e-9)/(proton_charge)   # Converts nA to protons/sec (1.25e10 protons/sec for 2nA)
    protons_per_cycle = proton_rate * cyclotron_period  # Number of protons from beam nozzle per cyclotron period (117.582 for 2 nA, 106.3 MHz)

    if time_structure == "continuous":
        return ATRACK + NCASE * (cyclotron_period/protons_per_cycle) * 1e6 # Multiplied by 1e6 to go from s to µs
    elif time_structure == "pulsed":
        return ATRACK + cyclotron_period * math.floor(NCASE/protons_per_cycle) * 1e6   # Multiplied by 1e6 to go from s to µs
    else:
        print(f"WARNING: Invalid time structure parameter : {time_structure}")
    

if __name__ == "__main__":
    print(convert_time(117, 0.001))
    print(convert_time(117, 0.001, continuous=False))


    import matplotlib.pyplot as plt
    ncases = [i for i in range(10000)]
    times_cont = [convert_time(ncase, 0.001) for ncase in ncases]
    times_quant = [convert_time(ncase, 0.001, continuous=False) for ncase in ncases]

    plt.scatter(ncases, times_cont, color="red", alpha=1, marker="x", s=1, label="continous")
    plt.scatter(ncases, times_quant, color="blue", alpha=1, marker="o", s=1, label="quantized")

    plt.xlabel("NCASE")
    plt.ylabel("Global time [µs]")
    plt.title(f"Time conversions between relative time 1 ns to global time \n Frequency: 106.3 MHz, beam current: 2 nA")
    plt.legend()
    plt.show()


        