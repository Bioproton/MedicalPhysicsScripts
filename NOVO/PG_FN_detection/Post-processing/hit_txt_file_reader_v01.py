"""
Script for reading gamma_hits.txt, neutron_hits.txt and all_hits.txt files
from post-processed (read + merge) files
"""

def collect_txt_data(file_adress) -> str:
    # Function that will collect all data from a usdraw txt output file from mgdraw_v05_detection.f 
    # Input is the adress for the file (where it is stored). Only _detected.txt-files as of 23.04.2025 works correctly
    # Optional input of the number primaries set in the FLUKA input. This is to ensure unique NCASE identifiers per proton, which might be the same across different spawns

    file_adress = file_adress.replace("\\", "/")

    import time
    print("Collecting data: ", end="")
    time_stamp = time.time()

    file = open(file_adress, "r")

    n = 0   # Line counter
    
    # Structure of detector output file, as of 06.08.2025
    ncase = [] # NCASE values: What primary proton created the secondaries we are investigating?
    icode = [] # Interaction codes (ICODES): What kind of interaction happened?  
    particle_in = []   # JTRACK values: What particle initiated the interaction?
    particle_out = []  # KPART(IP) values: What secondary resulted from the interaction?
    fnpg_flag = [] # LLOUSE values: Does the interaction stem directly from target FN/PG-production?

    targetZ = []   # ICHTAR values: What is the Z-value of the target particle?
    targetA = []   # IBTAR values: What is the A-value of the target particle?
    energy_out = [] # Tki(IP) values: What is the kinetic energy of the secondary? [GeV -> MeV]
    energy_in = []  # ETRACK-AM(JTRACK) values: What was the kinetic energy of the incoming particle? [GeV -> MeV]

    crash_x = [] # XSCO values: What was the X-coordinate of the interaction?   [cm]
    crash_y = [] # YSCO values: What was the Y-coordinate of the interaction?   [cm]
    crash_z = [] # ZSCO values: What was the Z-coordinate of the interaction?   [cm]

    region = []    # MREG values: What scintillator bar did the interaction happen?
    particle_generation = []  # LTRACK values: What "generation" was the incoming particle?
    particle_age = []   # ATRACK * 1E6 values: At what time (since primary production) did the interaction happen? [µs]
    
    source_x = [] # SPAUSR(2) values: At what X-coordinate in the target was the FN/PG produced?    [cm]
    source_y = [] # SPAUSR(3) values: At what Y-coordinate in the target was the FN/PG produced?    [cm]
    source_z = [] # SPAUSR(4) values: At what Z-coordinate in the target was the FN/PG produced?    [cm]

    
    # Looping over all lines in the file
    for line in file:

        line = " ".join(line.split()) # Remove all spaces, while leaving one space between each value. Spaces in output file might not be universal
        n += 1  # Increment line counter

        # Collecting all data from the output.txt file
        ncase.append(int(float(line.split(" ")[0])))
        icode.append(int(float(line.split(" ")[1])))
        particle_in.append(int(float(line.split(" ")[2])))
        particle_out.append(int(float(line.split(" ")[3])))
        fnpg_flag.append(int(float(line.split(" ")[4])))

        targetZ.append(int(float(line.split(" ")[5])))
        targetA.append(int(float(line.split(" ")[6])))
        energy_out.append(float(line.split(" ")[7]))    # [MeV]
        energy_in.append(float(line.split(" ")[8])) # [MeV]

        crash_x.append(float(line.split(" ")[9]))   # [cm]
        crash_y.append(float(line.split(" ")[10]))  # [cm]
        crash_z.append(float(line.split(" ")[11]))  # [cm]

        region.append(int(float(line.split(" ")[12])))
        particle_generation.append(int(float(line.split(" ")[13])))
        particle_age.append(float(line.split(" ")[14])) # Time in [µs]

        source_x.append(float(line.split(" ")[15])) # [cm]
        source_y.append(float(line.split(" ")[16])) # [cm]
        source_z.append(float(line.split(" ")[17])) # [cm]                  

    print(f"\rCollecting data: complete. {n} lines read. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)
    return [ncase, icode, particle_in, particle_out, fnpg_flag, \
        targetZ, targetA, energy_out, energy_in, \
        crash_x, crash_y, crash_z, \
        region, particle_generation, particle_age, \
        source_x, source_y, source_z]