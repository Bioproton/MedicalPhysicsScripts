''' 
This file contains helper functions to be used by the other scripts in this folder (Create_KDE.py, voxel_GT_composition.py). 
The functions are:


- read_scintillator_interactions (...)
- (Needs checking) read_scintillator_interactions_v02_ncase_only_adaptive_weekly(): reading scintillator interactions, code adapted for patient simulations (returns production region also) 
- read_composition(): reads the composition file and returns the composition as a dictionary
- find_HU_group_info(): provides the relevant information for a given HU group (density, elemental concentrations) 


'''

'''
Action: Reads the composition file and returns the composition as a dictionary. Works for both 3 and 6 labels. 
'''
def read_composition(filename):
    compositions = {}

    with open(filename, "r") as f:   # replace with your filename
        for line in f:
            if ":" in line:
                element, value = line.split(":")
                compositions[element.strip()] = float(value.strip())

    return compositions


'''
Action: Returns the density and elemental concentration of a specific HU group. For patient simulations. 
'''

def find_HU_group_info(lines, HU_group_elem, i_start, i_end):
    average_atomic_number = -1
    average_atomic_weight = -1
    average_density = -1

    nitrogen_atomic_content = 0
    oxygen_atomic_content = 0
    hydrogen_atomic_content = 0
    carbon_atomic_content = 0
    phospho_atomic_content = 0
    calcium_atomic_content = 0

    for i in range(i_start, i_end):
        elements = lines[i].split()
        if len(elements) > 0:
            if HU_group_elem == elements[1]:
                average_atomic_number = float(elements[2])
                average_atomic_weight = float(elements[3])
                average_density = float(elements[4])

                for j in range(i+4, i + 20):
                    elements_sub = lines[j].split()
                    if len(elements_sub) > 0:
                        if elements_sub[0] == "NITROGEN":
                            nitrogen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "OXYGEN":
                            oxygen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "HYDROGEN":
                            hydrogen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "CARBON":
                            carbon_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "CALCIUM":
                            calcium_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "PHOSPHO":
                            phospho_atomic_content = float(elements_sub[2])
                    else:
                        break

    return {"average_atomic_number" : average_atomic_number,
             "average_atomic_weight" : average_atomic_weight,
             "average_density" : average_density, 
             "nitrogen_atomic_content" : nitrogen_atomic_content, 
             "oxygen_atomic_content" : oxygen_atomic_content,
             "hydrogen_atomic_content" : hydrogen_atomic_content,
             "carbon_atomic_content" : carbon_atomic_content,
             "calcium_atomic_content" : calcium_atomic_content,
             "phospho_atomic_content" : phospho_atomic_content,}