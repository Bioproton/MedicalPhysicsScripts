'''
mgdraw plotter for ***_detected.txt files
The implemented version of mgdraw is "mgdraw_v02_production.f" dated to 23.04.2025

Although simulations will be ran in several spawns (_aa, _ab, _ac...),
    this code assumes only one input file to be plotted.
To be able to plot all spawns at the same time, one should run the Python-script:
    "...py", which will merge all the "_detected.txt" into one file.
'''
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
from mgdraw_txt_file_reader import collect_detection_data
from mgdraw_output_merger import output_merger

#------------------------------------------INPUT FOR USE------------------------------------------------
#   ADD ONE FOLDER DIRECTORY
#folder_directory = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\\FLUKA\\Delt mappe\\mgdraw_detection_results_11_04_25"
folder_directory = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\\FLUKA\\Delt mappe\\mgdraw_detection_results_28_04_25"

# ADD NUMBER OF PRIMARIES USED
primaries_per_spawn = 200000

# ADD WHAT PARTICLE TO BE SPOTTED
particle = "gamma"

# ADD FLUKA RUN NAME
fluka_run_name = None
#fluka_run_name = "prompt_gamma_detecc"
#fluka_run_name = "prompt_gamma_280425"
#fluka_run_name = "prompt_gamma_plascint"
#fluka_run_name = "prompt_gamma_M600"
fluka_run_name = "prompt_gamma_300425"
#------------------------------------------END OF INPUTS--------------------------------------------------
#------------------------------------------DATA COLLECTION-----------------------------------------------
# Merging all relevant files if merged file does not exist
merged_file_name = output_merger(folder_directory, particle=particle, fluka_run_name=fluka_run_name)

file_adress = folder_directory + r"\\" + merged_file_name
# Collecting data from the merged file
n, mother_ncase, current_icode, previous_icode, incoming_particle, outgoing_particle, scatter_avoided, secondary_particle_energy, mother_particle_energy, Xs, Ys, Zs, Xs_source, Ys_source, Zs_source, energy_in_bins = collect_detection_data(file_adress, primaries_per_spawn=primaries_per_spawn)

#print(f"Number of Compton scatters per primary proton: {n / (2 * primaries_per_spawn * 5)}")
time_stamp = time.time()
#--------------------------------------DATA HANDLING AND REWORKING--------------------------------------

# Collection of all electron and photon energies
electron_energies = [secondary_particle_energy[i] for i in range(len(secondary_particle_energy)) if outgoing_particle[i] == 3]
photon_energies = [secondary_particle_energy[i] for i in range(len(secondary_particle_energy)) if outgoing_particle[i] == 7]

# Collection of all Compton interaction coordinates. 
    # outgoing_particle[i] == 7 (photon) is assured to skip identical coordinates from outgoing electrons
interaction_xs = [Xs[i] for i in range(len(Xs)) if outgoing_particle[i] == 7]
interaction_ys = [Ys[i] for i in range(len(Ys)) if outgoing_particle[i] == 7]
interaction_zs = [round(Zs[i], 3) for i in range(len(Zs)) if outgoing_particle[i] == 7]

# Filtering information based on interaction codes, whether it has scattered, and if it is a unique mother photon
# NB! This code is currently not nice, and this will need to be split up in such a way that
    # multiple plots can be performed without having to commment stuff out in this section!

# Lists of source coordinates for unscattered PGs, i.e original production coordinates
PG_source_x = []    # X-coordinates
PG_source_y = []    # Y-coordinates
PG_source_z = []    # Z-coordinates

PG_interaction_x = [Xs[i] for i in range(len(outgoing_particle)) if outgoing_particle[i] == 7 and scatter_avoided[i] == 1]    # X-coordinates
PG_interaction_y = [Ys[i] for i in range(len(outgoing_particle)) if outgoing_particle[i] == 7 and scatter_avoided[i] == 1]    # Y-coordinates
PG_interaction_z = [Zs[i] for i in range(len(outgoing_particle)) if outgoing_particle[i] == 7 and scatter_avoided[i] == 1]    # Z-coordinates

PG_all_interactions = []

NCASE = 0   # Variable used only for logic. Number of proton currently tracked, between 1 and total number of primaries (i.e. 1e6)
PG_mother_photon_energies = []  # Energies for PGs going directly from production to Compton scattering in the detector
not_PG_mother_photon_energies = []  # NB: INCORRECT, gives all energies that are not mother PGs! Energies for all photons going from target to detector, and that are either not PGs or scattered PGs
original_source_coordinates = []    # List of original x, y, z-coordinates ([X1, Y1, Z1], [X2, Y2, Z2]). (Possibility of error if two different particles are produced at the same coordinate)

for i in range(len(outgoing_particle)):         
    if previous_icode[i] in [101, 106] and outgoing_particle[i] == 7 and scatter_avoided[i] == 1: # Proper unscattered PG. Save information about the PG
        #assert scatter_avoided[i] == 1, f"Warning: PG from NCASE {mother_ncase[i]} has scattered on its way. ICODE: {previous_icode[i]}"
        NCASE = mother_ncase[i]

        PG_source_x.append(Xs_source[i])
        PG_source_y.append(Ys_source[i])
        PG_source_z.append(round(Zs_source[i], 3))

        PG_mother_photon_energies.append(mother_particle_energy[i])
    elif outgoing_particle[i] == 7 and scatter_avoided[i] == 0: # Either not produced from PG (101, 106), or it is a PG that has scattered on its way to the detector
        if [Xs_source[i], Ys_source[i], Zs_source[i]] not in original_source_coordinates:
            not_PG_mother_photon_energies.append(mother_particle_energy[i]) # Original source coordinate => Not a mother photon   
            original_source_coordinates.append([Xs_source[i], Ys_source[i], Zs_source[i]])

# Lists of original source coordinates for scattered photons in the target, i.e. scattering coordinates or original production coordinates
source_x = []    # X-coordinates
source_y = []    # Y-coordinates
source_z = []    # Z-coordinates

for i in range(len(outgoing_particle)):
    if outgoing_particle[i] == 7:
        if i == 1:
            source_x.append(Xs_source[i])
            source_y.append(Ys_source[i])
            source_z.append(Zs_source[i])
        elif Xs_source[i] not in source_x and Ys_source[i] not in source_y and Zs_source[i] not in source_z:
            source_x.append(Xs_source[i])
            source_y.append(Ys_source[i])
            source_z.append(Zs_source[i])

photon_source = [-100.0, -100.0, -100.0] # Unique ID for each mother particle Compton-scattering in the detector. (Two photons can be produced and "detected" for each unique NCASE)
NCASE = 0   # Variable used to track the NCASE for particles in the loop
n_comptons = -1  # Variable used to count number of consecutive Compton interactions. Default -1 to trigger AssertionError if something weird happens
consecutive_comptons = []   # List containing how many consecutive Compton interactions happen for each mother photon (Compton chain length)
pg_consecutive_comptons = [] # List containing how many consecutive Compton interactions happen for each mother PG photon (PG Compton chain length)
doppelgangers = [] # List with NCASES for cases where there multiple photons produced by the same proton (NCASE) are Compton scattering in the detector
pgs = [0, 0]

for i in range(n):
    if i + 1 == n: # Final particle, add length of final Compton chain
        consecutive_comptons.append(n_comptons)
        if scatter_avoided[i] == 1:
            pg_consecutive_comptons.append(n_comptons)
    elif outgoing_particle[i] == 7:   # If secondary particle is a photon then the interaction is a new Compton scattering
        if photon_source == [Xs_source[i], Ys_source[i], Zs_source[i]]:  # Checks for the same production coordinate, i.e. the same mother photon source
            n_comptons += 1
        else:   # A new photon source means a new mother photon starting a different Compton scattering chain
            pgs[0] += scatter_avoided[i]
            pgs[1] += 1
            if NCASE == mother_ncase[i]:
                doppelgangers.append(NCASE)
            NCASE = mother_ncase[i]
            photon_source = [Xs_source[i], Ys_source[i], Zs_source[i]]

            if i == 0:  # At the first Compton interaction no previous Compton chain length has been saved
                n_comptons = 1 # Initialize Compton chain length counter
                continue
            consecutive_comptons.append(n_comptons) # New Compton chain -> add previous Compton chain length to list
            if scatter_avoided[i] == 1:
                pg_consecutive_comptons.append(n_comptons)
            n_comptons = 1  # Reset Compton chain length counter
if sum(consecutive_comptons) != n/2:
    print(f"Not all particles are taken into account \n Half of lines: {n/2} verus Comptons: {sum(consecutive_comptons)}")

# Collection of all source and interaction coordinates in order for figure 10 (animation)
photon_source = [-100.0, -100.0, -100.0] # Unique ID for each mother particle Compton-scattering in the detector. (Two photons can be produced and "detected" for each unique NCASE)
NCASE = 0   # Variable used to track the NCASE for particles in the loop
PG_all_interactions = [] # Only PGs
for i in range(len(outgoing_particle)):
    if photon_source != [Xs_source[i], Ys_source[i], Zs_source[i]] and outgoing_particle[i] == 3: # New mother photon, new interaction chain
        photon_source = [Xs_source[i], Ys_source[i], Zs_source[i]]
        if scatter_avoided[i] == 1 and previous_icode[i] in [101, 106]:
            PG_all_interactions.append([Xs_source[i], Ys_source[i], Zs_source[i]])
            PG_all_interactions.append([Xs[i], Ys[i], Zs[i]])
            NCASE = mother_ncase[i]
    elif photon_source == [Xs_source[i], Ys_source[i], Zs_source[i]] and outgoing_particle[i] == 3: # Another step in the Compton interaction chain
        if mother_ncase[i] == NCASE:
            PG_all_interactions.append([Xs[i], Ys[i], Zs[i]])

#print(PG_all_interactions)
print(f"Data reworking complete. Time used: {round(time.time() - time_stamp, 3)} s")
time_stamp = time.time()

#------------------------------------------------PLOTTING---------------------------------------------

# Copilot generated code that replicate simuatlion setup
# Target cube corners
target_vertices = [
    [-7.5, -7.5, 100.0],
    [7.5, -7.5, 100.0],
    [7.5, 7.5, 100.0],
    [-7.5, 7.5, 100.0],
    [-7.5, -7.5, 115.0],
    [7.5, -7.5, 115.0],
    [7.5, 7.5, 115.0],
    [-7.5, 7.5, 115.0]
]

# Target cube faces
target_faces = [
    [target_vertices[0], target_vertices[1], target_vertices[2], target_vertices[3]], # bottom face
    [target_vertices[4], target_vertices[5], target_vertices[6], target_vertices[7]], # top face
    [target_vertices[0], target_vertices[1], target_vertices[5], target_vertices[4]], # front face
    [target_vertices[2], target_vertices[3], target_vertices[7], target_vertices[6]], # back face
    [target_vertices[1], target_vertices[2], target_vertices[6], target_vertices[5]], # right face
    [target_vertices[4], target_vertices[7], target_vertices[3], target_vertices[0]]  # left face
]

# Detector cube corners
detector_vertices = [
    [15.0, -7.5, 100.0],
    [22.5, -7.5, 100.0],
    [22.5, 7.5, 100.0],
    [15.0, 7.5, 100.0],
    [15.0, -7.5, 115.0],
    [22.5, -7.5, 115.0],
    [22.5, 7.5, 115.0],
    [15.0, 7.5, 115.0]
]

# Detector cube faces
detector_faces = [
    [detector_vertices[0], detector_vertices[1], detector_vertices[2], detector_vertices[3]], # bottom face
    [detector_vertices[4], detector_vertices[5], detector_vertices[6], detector_vertices[7]], # top face
    [detector_vertices[0], detector_vertices[1], detector_vertices[5], detector_vertices[4]], # front face
    [detector_vertices[2], detector_vertices[3], detector_vertices[7], detector_vertices[6]], # back face
    [detector_vertices[1], detector_vertices[2], detector_vertices[6], detector_vertices[5]], # right face
    [detector_vertices[4], detector_vertices[7], detector_vertices[3], detector_vertices[0]]  # left face
]

# 2D histogram / energy spectrum of all electrons and photons going out of a Compton interaction
fig1 = plt.figure("Particle energy histogram")
plt.hist(electron_energies, bins=200, color="blue", alpha=0.3, log=True)
plt.hist(photon_energies, bins=200, color="red", alpha=0.3, log=True)
plt.title("Energy distribution of Compton secondaries")
plt.xlabel("MeV")
plt.ylabel("Counts")
plt.legend(["Electrons", "Photons"])
#plt.ylim([0, 50])
#plt.xscale("log")
#plt.yscale("log")

# 2D histogram with Compton interaction coordinates. Z-coordinates are shifted by -100 cm compared to FLUKA solely for plotting purposes
fig2 = plt.figure("Compton interaction coordinates")
plt.hist(interaction_xs, bins=50, color="blue", alpha=0.3)
plt.hist(interaction_ys, bins=50, color="red", alpha=0.3)
plt.hist(interaction_zs, bins=50, color="green", alpha=0.3)
plt.title("Coordinates of Compton interactions")
plt.xlabel("Coordinate [cm]")
plt.ylabel("Counts")
plt.legend(["X-position", "Y-position", "Z-position"])

# 2D histogram with coordinates of where the mother photons were produced in the target. Z-coordinates are shifted by -100 cm compared to FLUKA solely for plotting purposes
fig3 = plt.figure("Source coordinates")
plt.hist(PG_source_x, bins=50, color="blue", alpha=0.3)
plt.hist(PG_source_y, bins=50, color="red", alpha=0.3)
plt.hist(PG_source_z, bins=50, color="green", alpha=0.3)
plt.title("Mother photon source coordinates")
plt.xlabel("Coordinate [cm]")
plt.ylabel("Counts")
plt.legend(["X-position", "Y-position", "Z-position"])

# Energy spectrum for PGs that have not scattered in the target and that have started a Compton interaction in the detector
fig4 = plt.figure("Incoming unscattered PGs in the detector")
plt.hist(PG_mother_photon_energies, bins=500)
plt.xlabel("Energy [MeV]")
plt.ylabel("Counts")
plt.title("Energy spectrum for unscattered PGs interacting in detector")
plt.xlim([0, 15])
#plt.yscale("log")

# Energy spectrum for non-PGs or PGs that have scattered in the target and that have started a Compton interaction the detector
fig5 = plt.figure("Incoming non-PGs or scattered PGs")
plt.hist(not_PG_mother_photon_energies, bins=500)
plt.xlabel("Energy [MeV]")
plt.ylabel("Counts")
plt.title("Energy spectrum for non-PGs interacting in detector")
plt.xlim([0, 15])
plt.yscale("log")

# Distribution of Compton chain length
fig6 = plt.figure("Compton chain length")
plt.hist(consecutive_comptons, bins=[(i + 0.5) for i in range(max(consecutive_comptons) + 1)], align="mid", rwidth=0.8)
plt.xlabel("Compton chain length")
plt.ylabel("Counts")
plt.title("Distribution of Compton chain lengths")
#plt.yscale("log")

# Distribution of PG Compton chain length
fig7 = plt.figure("PG Compton chain length")
plt.hist(pg_consecutive_comptons, bins=[(i + 0.5) for i in range(max(consecutive_comptons) + 1)], align="mid", rwidth=0.8)
plt.xlabel("Compton chain length")
plt.ylabel("Counts")
plt.title("Distribution of PG Compton chain lengths")
#plt.yscale("log")

# 3D production and detection plot for all photons
fig8 = plt.figure("3D photon production coordinate plot")
ax8 = fig8.add_subplot(111, projection="3d")
ax8.add_collection3d(Poly3DCollection(target_faces, color="blue", edgecolor="k", alpha=0.1))
ax8.add_collection3d(Poly3DCollection(detector_faces, color="grey", edgecolor="k", alpha=0.4))
ax8.scatter(source_x, source_y, source_z, color="brown")
ax8.scatter(interaction_xs, interaction_ys, interaction_zs, color="red")
ax8.set_xlabel("X-coordinate [cm]")
ax8.set_ylabel("Y-coordinate [cm]")
ax8.set_zlabel("Z-coordinate [cm]")
ax8.set_title("Photon production and Compton interaction coordinates")

# 3D production and detection plot for PG only
fig9 = plt.figure("3D PG production coordinate plot")
ax9 = fig9.add_subplot(111, projection="3d")
ax9.add_collection3d(Poly3DCollection(target_faces, color="blue", edgecolor="k", alpha=0.1))
ax9.add_collection3d(Poly3DCollection(detector_faces, color="grey", edgecolor="k", alpha=0.4))
ax9.scatter(PG_source_x, PG_source_y, PG_source_z, color="brown")
ax9.scatter(PG_interaction_x, PG_interaction_y, PG_interaction_z, color="red")
ax9.set_xlabel("X-coordinate [cm]")
ax9.set_ylabel("Y-coordinate [cm]")
ax9.set_zlabel("Z-coordinate [cm]")
ax9.set_title("PG production and Compton interaction coordinates")

# Animation of scatter plot of production and detection
fig10 = plt.figure("3D PG production coordinates animation")
ax10 = fig10.add_subplot(111, projection="3d")
ax10.add_collection3d(Poly3DCollection(target_faces, color="blue", edgecolor="k", alpha=0.1))
ax10.add_collection3d(Poly3DCollection(detector_faces, color="grey", edgecolor="k", alpha=0.4))
ax10.set_xlim([-8, 25])
ax10.set_ylim([-8, 8])
ax10.set_zlim([99, 115])
ax10.set_xlabel("X-coordinate [cm]")
ax10.set_ylabel("Y-coordinate [cm]")
ax10.set_zlabel("Z-coordinate [cm]")
ax10.set_title("PG production and Compton interaction coordinates")

def ani_func(j, interaction_list=PG_all_interactions, ax=ax10):
    #X_coords = [i[0] for i in interaction_list[:j]]
    #Y_coords = [i[1] for i in interaction_list[:j]]
    #Z_coords = [i[2] for i in interaction_list[:j]]
    X_coords = interaction_list[j][0]
    Y_coords = interaction_list[j][1]
    Z_coords = interaction_list[j][2]
    if X_coords > 10.0:
        return ax.scatter(X_coords, Y_coords, Z_coords, color="red")
    elif X_coords < 10.0:
        return ax.scatter(X_coords, Y_coords, Z_coords, color="brown")
#ani10 = animation.FuncAnimation(fig=fig10, func=ani_func, frames=len(PG_all_interactions), interval=50)
#ani10.save(r"C://Users//sathu8821//OneDrive - University of Bergen//Pictures//Real animation test2.gif")

plt.show(block=False)
print(pgs)
#fig9.show()
print(f"{round(100 * pgs[0]/pgs[1], 2)} % of interacting photons are PGs")
print(f"Plotting complete. Time used: {round(time.time() - time_stamp, 3)} s")
input("Press enter to close plots")
plt.close("all")