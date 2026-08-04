''' 
This file contains helper functions to be used by the other scripts in this folder (Create_KDE.py, voxel_GT_composition.py). 
The functions are:


- read_scintillator_interactions (...)
- (Needs checking) read_scintillator_interactions_v02_ncase_only_adaptive_weekly(): reading scintillator interactions, code adapted for patient simulations (returns production region also) 
- read_composition(): reads the composition file and returns the composition as a dictionary
- find_HU_group_info(): provides the relevant information for a given HU group (density, elemental concentrations) 


'''
