"""
File for reading mgdraw-txt file results for photons and neutrons.
This is made so that the data collecting, which can be substantial (MB - GB), 
is only performed once. 

Relevant data entries are saved in lists. 
"""

import numpy as np

def collect_txt_data(file_adress, primaries_per_spawn=1e7, spawn_number=1, FLUKA_to_meas_coords=False, lattice_usage=False, mgdraw_version_8_plus=True) -> str:
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
    ncase = [] #0 NCASE values: What primary proton created the secondaries we are investigating?
    icode = [] #1 Interaction codes (ICODES): What kind of interaction happened?  
    particle_in = []   #2 JTRACK values: What particle initiated the interaction?
    particle_out = []  #3 KPART(IP) values: What secondary resulted from the interaction?
    fnpg_flag = [] #4 LLOUSE values: Does the interaction stem directly from target FN/PG-production?

    targetZ = []   #5 ICHTAR values: What is the Z-value of the target particle?
    targetA = []   #6 IBTAR values: What is the A-value of the target particle?
    energy_out = [] #7 Tki(IP) values: What is the kinetic energy of the secondary? [GeV -> MeV]
    energy_in = []  #8 ETRACK-AM(JTRACK) values: What was the kinetic energy of the incoming particle? [GeV -> MeV]

    crash_x = [] #9 XSCO values: What was the X-coordinate of the interaction?   [cm]
    crash_y = [] #10 YSCO values: What was the Y-coordinate of the interaction?   [cm]
    crash_z = [] #11 ZSCO values: What was the Z-coordinate of the interaction?   [cm]

    region = []    #12 MREG values: What scintillator bar did the interaction happen?
    particle_generation = []  #13 LTRACK values: What "generation" was the incoming particle?
    particle_age = []   #14 ATRACK * 1E6 values: At what time (since primary production) did the interaction happen? [µs]
    
    source_x = [] #15 SPAUSR(2) values: At what X-coordinate in the target was the FN/PG produced?    [cm]
    source_y = [] #16 SPAUSR(3) values: At what Y-coordinate in the target was the FN/PG produced?    [cm]
    source_z = [] #17 SPAUSR(4) values: At what Z-coordinate in the target was the FN/PG produced?    [cm]

    # Only for mgdraw versions 8+
    prod_energy = [] # SPAUSR(1) values: What energy did the produced photon/neutron have at the time of production [GeV -> MeV]

    def _coordinate_transform(coordinates):
        """
        Takes in coordinates [x, y, z] and translates them
        FROM FLUKA coordinates 
        TO measurement coordinates
        This is only meant for OncoRay-12-simulations
        """

        # Axel relabel/transform
        T = np.array([
            [0, 0, 1], 
            [0, 1, 0], 
            [1, 0, 0]])
        
        # Origin shift
        s = np.array([-54.2, 0, -20])   # cm

        # Numpify FLUKA coordinate
        u_FLUKA = np.array(coordinates)

        # Measurement coordinate
        u_meas = np.matmul(T, (u_FLUKA + s))

        return u_meas
    
    # Looping over all lines in the file
    for line in file:
        if "Spawn number:" in line:
            spawn_number = int(line.split(":")[1].strip().split(" ")[0]) # Spawn number in the FLUKA run. Used for altering NCASE values 
            continue    # Spawn number lines should be skipped, they don't contain other information than spawn number

        # If "***********" is in a line, it means that not enough space has been allocated to a feature value.
        # This has so far only happened for particle age for neutrons. I choose to skip these entries.
        if "***********" in line:
            line = line.replace("*", "0")
            #print(f"*********** found in file {file}")
            #print(f"Line: {line}")
    
        line = " ".join(line.split()) # Remove all spaces, while leaving one space between each value. Spaces in output file might not be universal
        n += 1  # Increment line counter

        # Collecting all data from the output.txt file
        ncase.append(int(line.split(" ")[0]) + (spawn_number - 1) * primaries_per_spawn) # Avoiding equal NCASEs in two different spawns. Example: NCASE 303 in spawn 4 for 2000 primaries is now NCASE 6303 [303 (4-1)*2000 = 6303]
        icode.append(int(line.split(" ")[1]))
        particle_in.append(int(line.split(" ")[2]))
        particle_out.append(int(line.split(" ")[3]))
        fnpg_flag.append(int(line.split(" ")[4]))

        # If there is no lattice, then simply append the 5th value here
        if not lattice_usage:
            targetZ.append(int(line.split(" ")[5]))

        targetA.append(int(line.split(" ")[6]))
        energy_out.append(round(float(line.split(" ")[7]) * 1000, 5)) # Multiplied by 1000 to get MeV from GeV
        energy_in.append(round(float(line.split(" ")[8]) * 1000, 5))  # Multiplied by 1000 for get MeV from Gev

        hit_x = float(line.split(" ")[9])
        hit_y = float(line.split(" ")[10])
        hit_z = float(line.split(" ")[11])
        
        # Transforming the lattice copies such that it matches the master detector model
        lattice_copy = 0
        if lattice_usage:
            if hit_x > 47:
                lattice_copy = 34
                lattice_transform = np.array([[1, 0], [0, 1]])  # Transform from 34 -> 34
            elif hit_x < -47:
                lattice_copy = 35
                lattice_transform = np.array([[-1, 0], [0, -1]])    # Transform from 35 -> 34
            elif hit_y > 47:
                lattice_copy = 36
                lattice_transform = np.array([[0, 1], [-1, 0]])     # Transform from 36 -> 34
            elif hit_y < -47:
                lattice_copy = 37
                lattice_transform = np.array([[0, -1], [1, 0]])     # Transform from 37 -> 34

            targetZ.append(lattice_copy)    # Use the fifth value as the lattice copy (MREG value from FLUKA)
            hit_x, hit_y = np.matmul(lattice_transform, np.array([hit_x, hit_y]))

        # Convert the hit coordinates from FLUKA coordinates to measurement coordinates
        if FLUKA_to_meas_coords:
            FLUKA_coords = [hit_x, hit_y, hit_z]
            meas_coords = _coordinate_transform(FLUKA_coords)
            
            crash_x.append(meas_coords[0])
            crash_y.append(meas_coords[1])
            crash_z.append(meas_coords[2])
        else:
            crash_x.append(hit_x)
            crash_y.append(hit_y)
            crash_z.append(hit_z)

        region.append(int(line.split(" ")[12]))
        particle_generation.append(int(line.split(" ")[13]))
        particle_age.append(float(line.split(" ")[14])) # Time in [µs]

        if FLUKA_to_meas_coords:
            FLUKA_coords = [float(line.split(" ")[15]), float(line.split(" ")[16]), float(line.split(" ")[17])]
            meas_coords = _coordinate_transform(FLUKA_coords)
            
            source_x.append(meas_coords[0])
            source_y.append(meas_coords[1])
            source_z.append(meas_coords[2])
        else:
            source_x.append(float(line.split(" ")[15]))
            source_y.append(float(line.split(" ")[16]))
            source_z.append(float(line.split(" ")[17]))

        if mgdraw_version_8_plus == True:
            prod_energy.append(float(line.split(" ")[18]) * 1000) # Multiplied by 1000 to get MeV from GeV  

    if mgdraw_version_8_plus == False:
        prod_energy = [0 for value in ncase]                      

    print(f"\rCollecting data: complete. {n} lines read. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)
    return [ncase, icode, particle_in, particle_out, fnpg_flag, \
        targetZ, targetA, energy_out, energy_in, \
        crash_x, crash_y, crash_z, \
        region, particle_generation, particle_age, \
        source_x, source_y, source_z, prod_energy]


# LATTICE TRANSFORMS AND COORDINATE TRANSFORMS
# Assignment of detector copy (which lattice copy did this occur in?)

#TODO

# Transformation from lattice copy coordinate to master copy coordinates
#TODO

# Convert FLUKA coordinates to measurement coordinates
#TODO
#coordinate_transform()