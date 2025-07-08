# Testing of the ***_produced.txt files from mgdraw_test_tagging-script

import matplotlib.pyplot as plt
import matplotlib
import math
import statistics
import time
from mpl_toolkits.mplot3d import Axes3D
from mgdraw_txt_file_reader import collect_data

#-----------------------------------------------------------INSERT ONE FILE ADRESS HERE---------------------------------------------------------
"""Files that should be used:"""
# Neutron files:
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_Neutrons_produced.txt"   # Big file (200 MB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_FN_produced.txt"      # Medium file (15 MB)

# Photon files:
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_pg_produced.txt"  # Medium file (21 MB)
file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_gamma_produced.txt" # Medium file (18 MB)


"""Other files which are not really suited for this script, but that can be ran:"""
# Neutrons
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_Neutrons_scattered.txt" # Medium file (14 MB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_Neutrons_scatt_dv.txt" # Small file (23 kB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_FN_unscattered.txt" # Medium file (7 MB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_FN_unscatt_dv.txt" # Small file (7 kB)

# Photons
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_gamma_scattered.txt" # Medium file (12 MB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_gamma_scatt_dv.txt" # Small file (20 kB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_pg_unscattered.txt" # Medium file (21 MB)
#file_adress = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\FLUKA\Delt mappe\mgdraw_31_03_25\prompt_gamma_2e6x5_`z001_pg_unscatt_dv.txt" # Small file (33 kB)

print(f"File: {file_adress}")
N, Es, Xs, Ys, Zs, Xs_cosine, Ys_cosine, Zs_cosine, bins, energy_in_bins = collect_data(file_adress)

# ---------------------------------------------------------------END OF IMPORT-------------------------------------------------------------------
print("Reworking data: ", end="")
time_stamp = time.time()

# Little function for averaging items in a list
def average(list) -> float:
    if len(list) != 0:
        return round(sum(list)/len(list), 6)
    else:
        return 0

# Alteration of max()-function to avoid max([]) -> error
def user_max(list) -> float:
    if len(list) != 0:
        return max(list)
    else:
        return 0.0
    
# Alteration of min()-function to avoid min([]) -> error
def user_min(list) -> float:
    if len(list) != 0:
        return min(list)
    else:
        return 0.0
    
# Bortfelt empirical proton range and energy relation (Bortfelt 1997) 
def depth_to_energy_calc(depth) -> float:
    R0 = 6.484  # cm, expected range of 100 MeV protons in PMMA
    z = depth - 100.0   # cm, Range values starts at 100 cm, I need it from 0 cm
    alpha = 0.0022 * 0.85   # 0.0022 value from ICRU 49 decreased by 15% due to PMMA having higher stopping power than water: ProBeam360 range shifter measurements: 1cm PMMA -> 1.15 cm WET
    p = 1.77    # Exponential value from ICRU 49

    if z > R0:
        return 0    # Avoid returning complex numbers due to (1/p)-exponenent
    else:   
        return ((R0 - z) / alpha) ** (1/p) # Bortfelt 1997 equation 5

# Estimating remaining proton energy per bin (=depth)
remaining_energy = [depth_to_energy_calc(i) for i in bins]

# Calculating minimum, maximum, average and stand deviation in energy per energy bin
energy_maximums = [user_max(i) for i in energy_in_bins]
energy_minimums = [user_min(i) for i in energy_in_bins]
average_energy_in_bins = []

# Calculating average secondary energy and standard deviation per depth:
energy_std = []  # Create skeleton for standard deviation entries
for energy_list in energy_in_bins:
    if len(energy_list) > 1:   
        energy_std.append(statistics.stdev(energy_list))
    else:   # If N=0, the std will be 0/0, which maths does not like. By L'Hopital, I think the std goes to 0 (?)
        energy_std.append(0)
    average_energy_in_bins.append(average(energy_list))    # Replace the energy lists with average values

energy_mean_plus_std = [sum(i) for i in zip(average_energy_in_bins, energy_std)]
energy_mean_minus_std = [sum(i) for i in zip(average_energy_in_bins, [-i for i in energy_std])]

Rs = [] # Distance/radius from beam central axis (0, 0, z)
# Calculation of production distance from central axis => sqrt(X**2 + Y**2)
for i in range(0, len(Xs)):
    Rs.append(math.sqrt(Xs[i] ** 2 + Ys[i] ** 2))

# Calculations for the polar histogram plot (fig10 and fig11), values from 0 to 180 degrees
angle_bins = [0]
angle_bin_step = 1
while angle_bins[-1] < 180.0:
    angle_bins.append(round(angle_bins[-1] + angle_bin_step, 0))

def create_histogram_data(direction_cosines, bins, directional_cosine=True) -> list:
    # Takes direction cosine list to be sorted into a bins and recalculates and returns a bin frequency list
    angles_in_bins = [[] for i in bins]
    frequency_per_bin = []
    if directional_cosine:
        angles = [(180/math.pi) * math.acos(i) for i in direction_cosines]
    else:
        angles = direction_cosines
    for angle in angles:
        angles_in_bins[bins.index(round(angle, 0))].append(angle)
    for bin in angles_in_bins:
        frequency_per_bin.append(len(bin))
    return frequency_per_bin

# Calculation of azimuthal angle (polar coordinate)
thetas = [(180/math.pi) * math.atan(Ys[i]/Xs[i]) + 90.0 for i, value in enumerate(Zs)]

X_angle_frequency = create_histogram_data(Xs_cosine, angle_bins)
Y_angle_frequency = create_histogram_data(Ys_cosine, angle_bins)
Z_angle_frequency = create_histogram_data(Zs_cosine, angle_bins)
theta_frequency = create_histogram_data(thetas, angle_bins, directional_cosine=False)
origo = [0 for i in Xs]

max_Es = max(Es)
Es_colormap = [(0.0, round(i / max_Es, 3), 0.0, 1.0) for i in Es]

# Calculations for polar histogram plots (fig10 and fig11), but copying/mirroring data to have data from 0 to 360 degrees
#angle_bins = angle_bins + [i + 180.0 for i in angle_bins]
#X_angle_frequency = X_angle_frequency + X_angle_frequency[::-1]
#Y_angle_frequency = Y_angle_frequency + Y_angle_frequency[::-1]
#Z_angle_frequency = Z_angle_frequency + Z_angle_frequency[::-1]

print(f"\rReworking data complete. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)
print("Plotting data: ", end="")
time_stamp = time.time()

#------------------------------------------PLOTTING----------------------------------------------------
# 2D histogram of secondary particle energy, energy spectrum
fig1 = plt.figure("Energy spectrum")
plt.hist(Es, bins=1000)
plt.yscale("log")
plt.xlabel("Energy [MeV]")
plt.ylabel("Counts")
plt.title("Secondary particle energy spectrum")


# 3D scatterplot of X, Y, Z-coordinates of secondaries production. Colourized based on secondary particle energy
fig2 = plt.figure("Production coordinates")
ax = fig2.add_subplot(projection="3d")
p = ax.scatter(Xs, Ys, Zs, marker="o", c=Es)
fig2.colorbar(p).set_label("Energy [MeV]")
ax.set_title("Secondaries production coordinates")
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")


# 2D scatterplot of X, Y-coordinates of secondaries production (Z-axis collapsed). Colourized based on secondary particle energy
fig3 = plt.figure("2D-production of secondaries")
plt.scatter(Xs, Ys, c=Es)
plt.colorbar().set_label("Energy [MeV]")
plt.title("2D-production of secondariess")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")


# 2D scatterplot of secondary particle energy versus production depth
fig4 = plt.figure("Energy versus depth")
plt.scatter(Zs, Es, c=Rs)
plt.colorbar().set_label("Distance from central axis [cm]")
plt.title("Secondary energy versus production depth")
plt.xlabel("Production depth [cm]")
plt.ylabel("Secodary energy [MeV]")


# 2D scatterplot of production depth versus distance from central axis
fig5 = plt.figure("Production depth versus distance from central axis")
plt.scatter(Zs, Rs, c=Es)
plt.colorbar().set_label("Energy [MeV]")
plt.title("Production depth versus distance from central axis")
plt.xlabel("Production depth [cm]")
plt.ylabel("Distance from central axis [cm]")


# [HEDGEHOG PLOT] 2D plot of average energy per depth versus depth (z-axis, binning method)
fig6 = plt.figure("Secondary energy versus production depth / hedgehog")
plt.plot(bins, average_energy_in_bins, color="blue")    # Average
plt.fill_between(bins, energy_mean_plus_std, energy_mean_minus_std, color="blue", alpha=0.4)
plt.fill_between(bins, energy_maximums, energy_minimums, color="blue", alpha=0.2)
#plt.plot(bins, remaining_energy, color="red")  # Only used when plotting the analytic Bortfeld fit energy-range relationship
plt.title("Secondary energy versus production depth")
plt.xlabel("Production depth [cm]")
plt.ylabel("Secondary energy [MeV]")
plt.legend(["Average", "1 std", "Max/min", "Remaining proton energy"])


# 2D heatmap plot/2D scatter plot of energy versus depth, but translated into a 2D histogram.
fig7 = plt.figure("Scatter energy versus depth / heatmap")
plt.hist2d(Zs, Es, bins=100, norm=matplotlib.colors.LogNorm())  # Logarithimic heatmap
#plt.hist2d(Zs, Es, bins=100)  # Linear heatmap
plt.colorbar().set_label("Counts")
#plt.plot(bins, remaining_energy, color="red")  # Only used when plotting the analytic Bortfeld fit energy-range relationship
plt.title("Secondary energy versus producton depth")
plt.xlabel("Production depth [cm]")
plt.ylabel("Energy [MeV]")
#plt.legend(["Remaining proton energy"])    # Only used when plotting the analytic Bortfeld fit energy-range relationship

# Depth production histogram (equivalent to Figure 1a in Ytre-Hauge 2019 Neutron feasability article)
fig8 = plt.figure("Neutron depth production histogram")
plt.hist(Zs, bins=100, histtype="step", color="blue", linewidth=2)
plt.title("Particle production per depth")
plt.xlabel("Depth [cm]")
plt.ylabel("Counts")
plt.legend(["100 MeV protons"])

# Direction cosines plot (equivalent to Figure 1c in Ytre-Hauge 2019 Neutron feasability article)
fig9 = plt.figure("Direction cosines histogram")
plt.hist(Xs_cosine, bins=100, histtype="step", color="blue")
plt.hist(Ys_cosine, bins=100, histtype="step", color="red")
plt.hist(Zs_cosine, bins=100, histtype="step", color="green")
plt.title("Particle direction cosines histogram")
plt.xlabel("Direction cosines")
plt.ylabel("Counts")
plt.legend(["X-cosine", "Y-cosine", "Z-cosine"])

# Polar histogram plot of angles calculated from direction cosines
fig10 = plt.figure("Direction polar histogram")
plt.polar([(math.pi/180) * i for i in angle_bins], X_angle_frequency, color="blue")
plt.polar([(math.pi/180) * i for i in angle_bins], Y_angle_frequency, color="red")
plt.polar([(math.pi/180) * i for i in angle_bins], Z_angle_frequency, color="green")
plt.title("Secondary particle direction angle polar histogram")
plt.legend(["X-angles", "Y-angles", "Z-angles"])

# 2D histogram plot of angle direction
fig11 = plt.figure("Secondary particle angle distribution")
plt.plot(angle_bins, X_angle_frequency, color="blue")
plt.plot(angle_bins, Y_angle_frequency, color="red")
plt.plot(angle_bins, Z_angle_frequency, color="green")
plt.title("Secondary particle direction angle distribution")
plt.xlabel("Angle [°]")
plt.ylabel("Counts")
plt.legend(["X-angles", "Y-angles", "Z-angles"])

# [Hedge Plot] 3D vector coordinate and vector plot
fig12 = plt.figure("3D coordinate plus vector plot")
ax12 = fig12.add_subplot(111, projection="3d")
ax12.quiver(Xs, Ys, Zs, Xs_cosine, Ys_cosine, Zs_cosine, colors=Es_colormap)
ax12.set_title("3D vector and coordinate for secondaries")
ax12.set_xlabel("X")
ax12.set_ylabel("Y")
ax12.set_zlabel("Z")

# Similar to fig11 but with polar coordinates (theta and phi angles)
fig13 = plt.figure("Polar coordinate plot")
plt.plot(angle_bins, Z_angle_frequency, color="green")
plt.plot(angle_bins, theta_frequency, color="orange")
plt.title("Polar coordinate angles distributions")
plt.xlabel("Angle [°]")
plt.ylabel("Counts")
plt.legend(["Polar angle (phi)", "Azimuthal angle (theta)"])

# BAD PLOT! [Second Hedge Plot] 3D vector plot, but all coordinates are set to origo (0, 0, 0)
#fig14 = plt.figure("3D origo vector plot")
#ax14 = fig14.add_subplot(111, projection="3d")
#ax14.quiver(origo, origo, origo, Xs_cosine, Ys_cosine, Zs_cosine, colors=Es_colormap)
#ax14.set_xlim([-1, 1])
#ax14.set_ylim([-1, 1])
#ax14.set_zlim([-1, 1])
#ax14.set_title("3D direction vectors for secondaries")
#ax14.set_xlabel("X")
#ax14.set_ylabel("Y")
#ax14.set_zlabel("Z")

# Either only show a single plot or show all
fig1.show()
#plt.show(block=False)

print(f"\rPlotting data: complete. Time used: {round(time.time() - time_stamp, 3)} s", flush=True)

input("Press enter to close plots")
plt.close("all")
