'''
This file reads a given FLUKA output file and a scintillator interactions folder. 
Goal: to assign a compositional ground truth to each mreg where a gamma/neutron was produced. 

1) Assign each mreg to a HU group
2) Read scintillator interactions folder
3) For each HU group, find the composition (density, elemental concentrations)
'''
import numpy as np
from helper_functions import find_HU_group_info

def find_voxel_GT_composition(output_file_path, regions_all, voxel_start_line, voxel_end_line, HU_start_line, HU_end_line):
    f = open(output_file_path, "r")
    lines = f.readlines()

    region_number = []
    HU_group = []

    ''' 1) Assign each mreg to a HU-group'''
    for i in range(voxel_start_line,voxel_end_line,2):
        elements = lines[i].split()
        region_number.append(int(elements[0]))
        HU_group.append(elements[3])

    ''' 2) For each HU group, find the composition (density, elemental concentrations)'''
    oxygen_contents = []
    carbon_contents = []
    nitrogen_contents = []
    calcium_contents = []
    hydrogen_contents = []
    phosphor_contents = []
    densities = []
    rests = []

    regions = np.unique(regions_all)
    print("length of regions:", len(regions))
    print("length of regions (all):", len(regions_all))

    for region in regions:
        HU_group_element = HU_group[int(region)-1]
        info = find_HU_group_info(lines, HU_group_element,HU_start_line, HU_end_line)
        densities.append(info["average_density"])
        oxygen_contents.append(info["oxygen_atomic_content"])
        carbon_contents.append(info["carbon_atomic_content"])
        nitrogen_contents.append(info["nitrogen_atomic_content"])
        calcium_contents.append(info["calcium_atomic_content"])
        hydrogen_contents.append(info["hydrogen_atomic_content"])
        phosphor_contents.append(info["phospho_atomic_content"])

        rest = 1 - info["oxygen_atomic_content"] - info["carbon_atomic_content"] - info["nitrogen_atomic_content"] - info["hydrogen_atomic_content"] - info["calcium_atomic_content"] - info["phospho_atomic_content"]
        rests.append(rest)

    return {"density" : np.mean(densities), "oxygen": np.mean(oxygen_contents), "carbon": np.mean(carbon_contents), "nitrogen": np.mean(nitrogen_contents), "calcium": np.mean(calcium_contents),"hydrogen": np.mean(hydrogen_contents),"phosphor": np.mean(phosphor_contents), "rests" : rests}

'''

# Give output file path
output_file_path = "/scratch/Anna/spectroscopy/adaptive_weekly/FLUKA_cagr_HN_weekly_2_01_IMPT_Anna/get_output_file/sim_0_0/sim_0_0_aa001.out"
# Give the scintillator interactions folder (Here given for sim_1_0)
scintillator_int_folder = r"/scratch/Anna/spectroscopy/adaptive_weekly/FLUKA_cagr_HN_weekly_2_01_IMPT_Anna/04_180/dat_files/sim_1_0/scintillator_interactions"

f = open(output_file_path, "r")
lines = f.readlines()
print(len(lines))

region_number = []
voxel_number = []
HU_group = []

# Find the HU group for each mreg
voxel_start_line = 124540 #79721 # In the section === Regions: materials and fields ===, choose the line above the first region
voxel_end_line = 132486 #84675 # Choose the line after the last voxel, obs: not the empty line but the one before. 

# Search up the composition and density of each HU group. 
HU_start_line = 123558#78766 # In the section === Material compositions: ===, choose the line before the first HU-group. 
HU_end_line = 124152#79343 #choose the line after the last element of the last HU group


# 1) Assign each mreg to a HU-group
for i in range(voxel_start_line,voxel_end_line,2):#,84676,2):
    elements = lines[i].split()
    region_number.append(int(elements[0]))
    HU_group.append(elements[3])

# 2) Read scintillator interactions folder
# Read scintillator interactions for gammas and neutrons
#LLOUSE, ICHTAR,IBTAR, tki_ip, etrack, regs = read_scintillator_interactions_v02_ncase_only_adaptive_weekly(scintillator_int_folder, num_files = 100)
#LLOUSE_nøy , ICHTAR_nøy ,IBTAR_nøy , tki_ip_nøy , etrack_nøy , regs_nøy = read_scintillator_interactions_v02_ncase_only_neutrons_adaptive_weekly(scintillator_int_folder, num_files = 100)

# 3) For each HU group, find the composition (density, elemental concentrations)
oxygen_contents = []
carbon_contents = []
nitrogen_contents = []
calcium_contents = []
hydrogen_contents = []
phosphor_contents = []
densities = []
rests = []

# iterate through regs (from reading scintillator interactions)
for region in regs:
    HU_group_element = HU_group[int(region)-1]
    info = find_HU_group_info(lines, HU_group_element,HU_start_line, HU_end_line)
    densities.append(info["average_density"])
    oxygen_contents.append(info["oxygen_atomic_content"])
    carbon_contents.append(info["carbon_atomic_content"])
    nitrogen_contents.append(info["nitrogen_atomic_content"])
    calcium_contents.append(info["calcium_atomic_content"])
    hydrogen_contents.append(info["hydrogen_atomic_content"])
    phosphor_contents.append(info["phospho_atomic_content"])

    rest = 1 - info["oxygen_atomic_content"] - info["carbon_atomic_content"] - info["nitrogen_atomic_content"] - info["hydrogen_atomic_content"] - info["calcium_atomic_content"] - info["phospho_atomic_content"]
    rests.append(rest)


print("Average density:", np.mean(densities))
print("Mean oxygen content:", np.mean(oxygen_contents))
print("Mean carbon content:", np.mean(carbon_contents))
print("Mean nitrogen content:", np.mean(nitrogen_contents))
print("Mean calcium content:", np.mean(calcium_contents))
print("Mean hydrogen content:", np.mean(hydrogen_contents))
print("Mean phosphorus content:", np.mean(phosphor_contents))
print("Mean rest content:", np.mean(rests))'''
