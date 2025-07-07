"""
File for reading mgdraw-txt file results for photons and neutrons.
This is made so that the data collecting, which can be substantial (200 MB+), is only performed once.

Relevant data is saved in lists. This could probably have been done with a class as well.
"""

def collect_bxdraw_data(file_adress, primaries_per_spawn = 200000) -> str:
    # Function that will collect all data from a self-defined mgdraw output file
    # Input is the adress for the file (where it is stored). Only _detected.txt-files as of 23.04.2025 works correctly
    # Optional input of the number primaries set in the FLUKA input. This is to ensure unique NCASE identifiers per proton, which might be the same across different spawns

    file_adress = file_adress.replace("\\", "/")

    import time
    print("Collecting data: ", end="")
    time_stamp = time.time()

    file = open(file_adress, "r")

    n = 0   # Line counter 

    # Structure of detector output file, as of 23.04.2025
    mother_ncase = []    # NCASE values, i.e. what primary proton created the secondary we are investigating
    incoming_particle = []  # What particle crossed between regions? [7:photon, 8:neutron, 1:proton, 3:electron]
    previous_region = [] # What region did the particle leave? [1-48: Scintillators, 49: Target, 50-55: Voids, 57-152: Electronic readout boxes]
    new_region = [] # What region did the particle enter? [1-48: Scintillators, 49: Target, 50-55: Voids, 57-152: Electronic readout boxes]
    particle_ltrack = [] # What is the LTRACK of the particle (i.e. what generation does it belong to?)
    particle_energy = [] # What energy does the particle have? [MeV]
    Xs = [] # X-coordinate of the region crossing [cm]
    Ys = [] # Y-coordinate of the region crossing [cm]
    Zs = [] # Z-coordinate of the region crossing [cm]
    particle_age = [] # At what time (since the primary production) did the particle cross the regions? [µs]


    # Looping over all lines in the file
    for line in file:
        if "Spawn number:" in line:
            spawn_number = int(line.split(":")[1].strip().split(" ")[0]) # Spawn number in the FLUKA run. Used for altering NCASE values 
            continue    # Spawn number lines should be skipped, they don't contain other information than spawn number
        else:
            line = " ".join(line.split()) # Remove all spaces, while leaving one space between each value. Spaces in output file might not be universal
            n += 1  # Increment line counter

            # Collecting all data from the detection output.txt file
            mother_ncase.append(int(line.split(" ")[0]) + (spawn_number - 1) * primaries_per_spawn) # Spawns have NCASEs from 1 to the number of primaries. To individualize them, the number of primaries is added to the NCASE. I.e. NCASE 303 in spawn 4 for 2000 primaries is now NCASE 6303
            incoming_particle.append(int(line.split(" ")[1]))
            previous_region.append(int(line.split(" ")[2]))
            new_region.append(int(line.split(" ")[3]))
            particle_ltrack.append(int(line.split(" ")[4]))
            particle_energy.append(float(line.split(" ")[5]) * 1000)    # Multiplied by 1000 to get MeV from GeV
            Xs.append(float(line.split(" ")[6]))
            Ys.append(float(line.split(" ")[7]))
            Zs.append(float(line.split(" ")[8]))
            particle_age.append(float(line.split(" ")[9]))
            
    print(f"\rCollecting data: complete. {n} lines read. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)
    return mother_ncase, incoming_particle, previous_region, new_region, particle_ltrack, particle_energy, Xs, Ys, Zs, particle_age

