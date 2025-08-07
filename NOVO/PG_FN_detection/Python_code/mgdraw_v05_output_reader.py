"""
File for reading mgdraw-txt file results for photons and neutrons.
This is made so that the data collecting, which can be substantial (MB - GB), 
is only performed once. 

Relevant data entries are saved in lists. 
"""

def collect_txt_data(file_adress, primaries_per_spawn=2e6) -> str:
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
    energy_out = [] # Tki(IP) values: What is the kinetic energy of the secondary? [GeV]
    energy_in = []  # ETRACK-AM(JTRACK) values: What was the kinetic energy of the incoming particle? [GeV]

    crash_x = [] # XSCO values: What was the X-coordinate of the interaction?
    crash_y = [] # YSCO values: What was the Y-coordinate of the interaction?
    crash_z = [] # ZSCO values: What was the Z-coordinate of the interaction?

    region = []    # MREG values: What scintillator bar did the interaction happen?
    particle_generation = []  # LTRACK values: What "generation" was the incoming particle?
    particle_age = []   # ATRACK * 1E6 values: At what time (since primary production) did the interaction happen? [µs]
    
    source_x = [] # SPAUSR(2) values: At what X-coordinate in the target was the FN/PG produced?
    source_y = [] # SPAUSR(3) values: At what Y-coordinate in the target was the FN/PG produced?
    source_z = [] # SPAUSR(4) values: At what Z-coordinate in the target was the FN/PG produced?

    
    # Looping over all lines in the file
    for line in file:
        if "Spawn number:" in line:
            spawn_number = int(line.split(":")[1].strip().split(" ")[0]) # Spawn number in the FLUKA run. Used for altering NCASE values 
            continue    # Spawn number lines should be skipped, they don't contain other information than spawn number
        else:
            line = " ".join(line.split()) # Remove all spaces, while leaving one space between each value. Spaces in output file might not be universal
            n += 1  # Increment line counter

            # Collecting all data from the output.txt file
            ncase.append(int(line.split(" ")[0]) + (spawn_number - 1) * primaries_per_spawn) # Avoiding equal NCASEs in two different spawns: NCASE 303 in spawn 4 for 2000 primaries is now NCASE 6303
            icode.append(int(line.split(" ")[1]))
            particle_in.append(int(line.split(" ")[2]))
            particle_out.append(int(line.split(" ")[3]))
            fnpg_flag.append(int(line.split(" ")[4]))

            targetZ.append(int(line.split(" ")[5]))
            targetA.append(int(line.split(" ")[6]))
            energy_out.append(float(line.split(" ")[7]))
            energy_in.append(float(line.split(" ")[8]))

            crash_x.append(float(line.split(" ")[9]))
            crash_y.append(float(line.split(" ")[10]))
            crash_z.append(float(line.split(" ")[11]))

            region.append(int(line.split(" ")[12]))
            particle_generation.append(int(line.split(" ")[13]))
            particle_age.append(float(line.split(" ")[14]))

            source_x.append(float(line.split(" ")[15]))
            source_y.append(float(line.split(" ")[16]))
            source_z.append(float(line.split(" ")[17]))                         

    print(f"\rCollecting data: complete. {n} lines read. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)
    return ncase, icode, particle_in, particle_out, fnpg_flag, \
        targetZ, targetA, energy_out, energy_in, \
        crash_x, crash_y, crash_z, \
        region, particle_generation, particle_age, \
        source_x, source_y, source_z