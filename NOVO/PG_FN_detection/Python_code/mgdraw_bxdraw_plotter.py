'''
mgdraw plotter for ***_detected.txt files
The implemented version of mgdraw is "mgdraw_v02_production.f" dated to 23.04.2025

Although simulations will be ran in several spawns (_aa, _ab, _ac...),
    this code assumes only one input file to be plotted.
To be able to plot all spawns at the same time, one should run the Python-script:
    "...py", which will merge all the "_detected.txt" into one file.
'''
import time
import math
import matplotlib.pyplot as plt
#import matplotlib.animation as animation
#from mpl_toolkits.mplot3d.art3d import Poly3DCollection
#from mpl_toolkits.mplot3d import Axes3D
from bxdraw_txt_file_reader import collect_bxdraw_data
from mgdraw_output_merger_v2 import output_merger

#------------------------------------------INPUT FOR USE------------------------------------------------
# ADD ONE FOLDER DIRECTORY

# Solid aluminium boxes
#folder_directory = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\FLUKA\\Delt mappe\\NOVCoDA_bxdraw_massive_boxes"

# Void aluminium boxes
#folder_directory = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\FLUKA\\Delt mappe\\NOVCoDA_bxdraw_void_boxes"

# Hollow aluminium boxes
folder_directory = r"C:\\Users\sathu8821\\OneDrive - University of Bergen\\NOVO\\FLUKA\\Delt mappe\\NOVCoDA_bxdraw_hollow_boxes"

# ADD NUMBER OF PRIMARIES USED
primaries_per_spawn = 2000000

# ADD FLUKA RUN NAME
fluka_run_name = None
#fluka_run_name = "NOVO_detector"

# ADD MGDRAW OUTPUT NAME
mgdraw_output_name = None

#------------------------------------------END OF INPUTS--------------------------------------------------
#------------------------------------------DATA COLLECTION-----------------------------------------------
# Merging all relevant files if merged file does not exist
merged_file_name = output_merger(
    folder_directory, fluka_run_name=fluka_run_name, 
    mgdraw_output_name=mgdraw_output_name
)

file_adress = folder_directory + r"\\" + merged_file_name

# Collecting data from the merged file
mother_ncase, incoming_particle, previous_region, new_region, \
    particle_ltrack, particle_energy, Xs, Ys, Zs, particle_age = \
    collect_bxdraw_data(file_adress, primaries_per_spawn=primaries_per_spawn)


time_stamp = time.time()
#--------------------------------------DATA HANDLING AND REWORKING--------------------------------------

# Filtering information based on interaction codes, whether it has scattered, and if it is a unique mother photon
# NB! This code is currently not nice, and this will need to be split up in such a way that
    # multiple plots can be performed without having to commment stuff out in this section!


# Maths for counting what detector layers the particles are entering
photon_layer_counts = [0 for i in range(12)]
neutron_layer_counts = [0 for i in range(12)]

for j, new_reg in enumerate(new_region):
    layer = math.floor((new_reg - 1) / 4)
    if incoming_particle[j] == 7:
        photon_layer_counts[layer] += 1
    elif incoming_particle[j] == 8:
        neutron_layer_counts[layer] += 1

# Neutron to photon count ratio per detector layer
neutron_to_photon_ratio = [neutron_layer_counts[i]/photon_layer_counts[i] for i in range(len(photon_layer_counts))]

# Sorting particle counts per scintillator(/region)
photon_scintillator_counts = [0 for i in range(48)]
neutron_scintillator_counts = [0 for i in range(48)]

for j, new_reg in enumerate(new_region):
    if incoming_particle[j] == 7:
        photon_scintillator_counts[new_reg - 1] += 1
    if incoming_particle[j] == 8:
        neutron_scintillator_counts[new_reg - 1] += 1

photon_scintillator_regions = [j for i, j in enumerate(new_region) if incoming_particle[i] == 7]
neutron_scintillator_regions = [j for i, j in enumerate(new_region) if incoming_particle[i] == 8]

# Neutron to photon count ratio per scintillator
neutron_to_photon_ratio_scintillator = [neutron_scintillator_counts[i]/photon_scintillator_counts[i] \
        for i in range(len(photon_scintillator_counts))]

# Sorting energies for neutrons and photons
photon_energies = [particle_energy[i] for i in range(len(mother_ncase)) if incoming_particle[i] == 7]
neutron_energies = [particle_energy[i] for i in range(len(mother_ncase)) if incoming_particle[i] == 8]

# Calculating detected coordinates into old coordinates for plotting purposes 
old_Xs = [Zs[i] + 7.0 for i in range(len(Xs))]
old_Ys = [(math.sqrt(3)/2) * Xs[i] + 0.5 * Ys[i] + 7.0 for i in range(len(Xs))]
old_Zs = [-0.5 * Xs[i] + math.sqrt(3)/2 * Ys[i] - 15.0 for i in range(len(Xs))]

#----------------------------------------------PLOTTING-----------------------------------------------
# FIGURE 1: 
# 2D histogram / energy spectrum of all neutrons and photons
fig1 = plt.figure("Figure 1")
plt.hist(photon_energies, color="red", bins=200, alpha=0.5)
plt.hist(neutron_energies, color="blue", bins=200, alpha=0.5)

plt.xlabel("Energy [MeV]")
plt.ylabel("Counts [#]")
plt.legend(["Photons", "Neutrons"])
plt.title("Energy spectra of particles crossing selected boundaries")
plt.yscale("log")

# FIGURE 2:
# Line plot of how many particles are entering each layer (=scintillators in that layer)
fig2 = plt.figure("Figure 2")
plt.bar([i for i in range(1, 13)], photon_layer_counts, color="red", alpha=0.5)
plt.bar([i for i in range(1, 13)], neutron_layer_counts, color="blue", alpha=0.5)

plt.xlabel("Scintillator layer")
plt.ylabel("Counts [#]")
plt.xticks([i for i in range(1, 13)])
plt.legend(["Photons", "Neutrons"])
plt.title("Number of particles entering each NOVCoDA layer")

# FIGURE 3
# Line plot of the relative amount of neutron to photon counts per detector layer
fig3 = plt.figure("Figure 3")
plt.bar([i for i in range(1, 13)], neutron_to_photon_ratio, color="green")
plt.plot([0.5] + [i for i in range(1, 13)] + [12.5], [1 for i in range(14)], color="black", linestyle="--")

plt.xlabel("Scintillator layer")
plt.ylabel("Neutron to photon count ratio")
plt.xticks([i for i in range(1, 13)])
plt.legend(["Ratio = 1", "Neutron to photon count ratio"])
plt.title("Relative number of neutron to photon counts per layer")

# FIGURE 4
# Histogram/line plot of the number of neutron to photon counts per scintillator
fig4 = plt.figure("Figure 4")

# Line plot
#plt.plot([i for i in range(1, 49)], photon_scintillator_counts, color="red")
#plt.plot([i for i in range(1, 49)], neutron_scintillator_counts, color="blue")

# Plotting bars
plt.bar([i - 0.2 for i in range(1, 49)], photon_scintillator_counts, width=0.4, color="red")
plt.bar([i + 0.2 for i in range(1, 49)], neutron_scintillator_counts, width=0.4, color="blue")
maximum_y=max(max(photon_scintillator_counts), max(neutron_scintillator_counts))

# Plotting vertical lines to make is easier to visually differentiate scintillator layers
plt.vlines(
    [4 * i + 0.5 for i in range(13)], 
    ymax=maximum_y, ymin=0, 
    color="black", linestyle="--", linewidth=0.8
)

# Writing labels to enumerate the scintillator layers
for i in range(12):
    plt.text(
        x=(2.5 + 4*i), y=maximum_y, s=str(i + 1), 
        horizontalalignment="center"
    )

plt.xlabel("Scintillator number")
plt.ylabel("Counts [#]")
plt.legend(["Detector layer marker", "Photons", "Neutrons"])
plt.title("Number of particles entering each scintillator")

# FIGURE 5
# Line plot of the neutron to photon count ratio per scintillator
fig5 = plt.figure("Figure 5")
plt.plot([i for i in range(1, 49)], neutron_to_photon_ratio_scintillator, color="green")
plt.plot([i for i in range(1, 49)], [1 for i in range(1, 49)], color="black", linestyle="--")

plt.xlabel("Scintillator number")
plt.ylabel("Neutron to photon count ratio")
plt.legend(["Neutron to photon count ratio", "Ratio = 1"])
plt.title("Neutron to photon ratio per scintillator layer")

# FIGURE 6
# Histograms of photon counts in the different layers (scooped from figure 4, photon equivalent to figure 7)
fig6 = plt.figure("Figure 6")
fig6_7_bar_placements = []
for i in range(1, 13):
    fig6_7_bar_placements += [round(i + 0.2 * j, 1) for j in range(1, 5)]
plt.bar(fig6_7_bar_placements, photon_scintillator_counts,
        color="red", width=0.2, edgecolor="black")

plt.vlines(
    x=[i for i in range(1, 14)], ymax=max(photon_scintillator_counts), ymin=0,
    color="black", linestyle="--", linewidth=0.8
)
for i in range(1, 13):
    plt.text(
        x =0.5 + i, y=max(photon_scintillator_counts), s=str(i),
        horizontalalignment="center"
    )

plt.xlabel("Layer number")
plt.xticks([])
plt.ylabel("Counts [#]")
plt.legend(["Layer seperator", "Photons"])
plt.title("Number of particles entering each scintillator")

# FIGURE 7
# Histograms of neutron counts in the different layers (scooped from figure 4, neutron equivalent to figure 6)
fig7 = plt.figure("Figure 7")
plt.bar(fig6_7_bar_placements, neutron_scintillator_counts,
        color="blue", width=0.2, edgecolor="black")

plt.vlines(
    x=[i for i in range(1, 14)], ymax=max(neutron_scintillator_counts), ymin=0,
    color="black", linestyle="--", linewidth=0.8
)
for i in range(1, 13):
    plt.text(
        x =0.5 + i, y=max(neutron_scintillator_counts), s=str(i),
        horizontalalignment="center"
    )

plt.xlabel("Layer number")
plt.xticks([])
plt.yticks([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000])
plt.ylabel("Counts [#]")
plt.legend(["Layer seperator", "Neutrons"])
plt.title("Number of particles entering each scintillator")

# FIGURE 8
# Histogram of layer-normalized photon counts per scintillator (same as figure 6, but normalized per layer)
fig8 = plt.figure("Figure 8")

norm_photon_scintillator_counts = []
# Normalizing counts in each layer by the first scintillator count
for i in range(1, 13):
    norm_photon_scintillator_counts += \
        [j/photon_scintillator_counts[4 * (i - 1)] for j in photon_scintillator_counts[4 * (i - 1):4 * i]]
    
# Sorting the counts so that odd layers go first, then even layers
sorted_norm_photon_scintillator_counts = [0 for i in range(48)]
layer = 0
for i in range(1, 49):
    # If scintillator number is 1, 5, 9, ..., 45, then it is part of a new energy layer
    if (i - 1) % 4 == 0:
        layer += 1
    # For odd layers
    if layer % 2 != 0:
        sorted_norm_photon_scintillator_counts[i - 2 * (layer - 1) - 1] += norm_photon_scintillator_counts[i - 1]
    # For even layers
    elif layer % 2 == 0:
        sorted_norm_photon_scintillator_counts[i + 24 - 2*layer - 1] += norm_photon_scintillator_counts[i - 1]

# Histogram
plt.bar(fig6_7_bar_placements, sorted_norm_photon_scintillator_counts,
        color = "red", width = 0.2, edgecolor="black", label="Photons")

# Vertical lines to visually seperate each scintillator layer
plt.vlines(
    x=[i for i in range(1, 14)], ymax=max(norm_photon_scintillator_counts), ymin=0,
    color="black", linestyle="--", linewidth=0.8, label="Layer seperator"
)

# Bold vertical line to differentiate odd and even layers
plt.vlines(x=7,ymax=max(norm_photon_scintillator_counts) + 0.05, ymin=0,
    color="black", linestyle="-", linewidth=1.2
)

def sorted_text(layer_nmb):
    if layer_nmb < 7:
        return layer_nmb + (layer_nmb - 1)
    elif layer_nmb >= 7:
        return 2 * layer_nmb - 12

# Text to enumerate the different scintillator layers
for i in range(1, 13):
    plt.text(
        x = 0.5 + i, y=max(norm_photon_scintillator_counts), s=str(sorted_text(i)),
        horizontalalignment="center"
    )
plt.xlabel("Layer number")
plt.xticks([])
plt.ylabel("Normalized counts")
plt.legend(loc="lower right")
plt.title("Relative number of particles entering each scintillator")

# FIGURE 9
# Histogram of layer-normalized neutron counts per scintillator (same as figure 7, but normalized per layer)
fig9 = plt.figure("Figure 9")

norm_neutron_scintillator_counts = []
# Normalizing counts in each layer by the first scintillator count
for i in range(1, 13):
    norm_neutron_scintillator_counts += \
        [j/neutron_scintillator_counts[4 * (i - 1)] for j in neutron_scintillator_counts[4 * (i - 1):4 * i]]
    
# Sorting the counts so that odd layers go first, then even layers
sorted_norm_neutron_scintillator_counts = [0 for i in range(48)]
layer = 0
for i in range(1, 49):
    # If scintillator number is 1, 5, 9, ..., 45, then it is part of a new energy layer
    if (i - 1) % 4 == 0:
        layer += 1
    # For odd layers
    if layer % 2 != 0:
        sorted_norm_neutron_scintillator_counts[i - 2 * (layer - 1) - 1] += norm_neutron_scintillator_counts[i - 1]
    # For even layers
    elif layer % 2 == 0:
        sorted_norm_neutron_scintillator_counts[i + 24 - 2*layer - 1] += norm_neutron_scintillator_counts[i - 1]

# Histogram
plt.bar(fig6_7_bar_placements, sorted_norm_neutron_scintillator_counts,
        color="blue", width=0.2, edgecolor="black")

# Vertical lines to visually seperate each scintillator layer
plt.vlines(
    x=[i for i in range(1, 14)], ymax=max(norm_neutron_scintillator_counts), ymin=0,
    color="black", linestyle="--", linewidth=0.8
)

# Add one old vertical line to differentiate odd and even layers
plt.vlines(x=7,ymax=max(norm_neutron_scintillator_counts) + 0.05, ymin=0,
    color="black", linestyle="-", linewidth=1.2
)

# Text to enumerate the different scintillator layers
for i in range(1, 13):
    plt.text(
        x=0.5 + i, y=max(norm_neutron_scintillator_counts), s=str(sorted_text(i)),
        horizontalalignment="center"
    )

plt.xlabel("Layer number")
plt.xticks([])
plt.ylabel("Normalized counts")
plt.legend(["Layer seperator", "Neutrons"], loc="lower left")
plt.title("Relative number of particles entering each scintillator")

# FIGURE 10
# Scatterplot of the coordinates where particles are entering the scintillator
fig10 = plt.figure("Figure 10")
ax10 = fig10.add_subplot(111, projection="3d")
ax10.scatter(Xs, Ys, Zs, s=0.1, alpha=0.1, color="blue")
ax10.set_xlabel("X [mm]")
ax10.set_ylabel("Y [mm]")
ax10.set_zlabel("Z [mm]")
ax10.set_title("Particle crossing coordinates")
ax10.view_init(elev = 25, azim=45, roll=0)

# FIGURE 11
fig11 = plt.figure("Figure 11")
ax11 = fig11.add_subplot(111, projection="3d")
ax11.scatter(old_Xs, old_Ys, old_Zs, s=0.1, alpha=0.1, color="green")
ax11.set_xlabel("X [mm]")
ax11.set_ylabel("Y [mm]")
ax11.set_zlabel("Z [mm]")
ax11.set_title("Particle crossing coordinates")

# FIGURE 12
# 1D histogram of where on the X-axis particles enter the first four scintillators
fig12 = plt.figure("Figure 12")
bar1_Xs = [old_Xs[i] for i in range(len(Xs)) if new_region[i] == 1]
bar2_Xs = [old_Xs[i] for i in range(len(Xs)) if new_region[i] == 2]
bar3_Xs = [old_Xs[i] for i in range(len(Xs)) if new_region[i] == 3]
bar4_Xs = [old_Xs[i] for i in range(len(Xs)) if new_region[i] == 4]

plt.hist(bar1_Xs, bins=100, color="green", alpha=0.5)
plt.hist(bar2_Xs, bins=100, color="blue", alpha=0.5)
plt.hist(bar3_Xs, bins=100, color="purple", alpha=0.5)
plt.hist(bar4_Xs, bins=100, color="red", alpha=0.5)
plt.legend(["Bar 1", "Bar 2", "Bar 3", "Bar 4"])
plt.xlabel("X-value [mm]")
plt.ylabel("Counts [#]")
plt.title("X-value crosses for scintillator bars")

# FIGURE 13
# Violin plot of when (ATRACK) particles enter scintillators (PER LAYER)
fig13 = plt.figure("Figure 13")

# Sorting data per layer
violindata_layer = [[] for i in range(12)]
for i in range(len(particle_age)):
    violindata_layer[int((new_region[i] - 1) / 4)].append(particle_age[i])

#plt.violinplot(violindata_layer, showextrema=False, showmeans=True, showmedians=True)
plt.boxplot(violindata_layer, showfliers=False)

plt.xticks([i for i in range(1, 13)])
plt.xlabel("Detector layer")
plt.ylabel("Time [µs]")
#plt.yscale("log")

# FIGURE 14
# Violin plot of when (ATRACK) particles enter scintillators (PER SCINTILLATOR)


#plt.show(block=False)
fig13.show()
print(f"Plotting complete. Time used: {round(time.time() - time_stamp, 3)} s")
input("Press enter to close plots")
plt.close("all")