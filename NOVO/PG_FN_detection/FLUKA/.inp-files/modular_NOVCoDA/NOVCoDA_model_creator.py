"""
Two-step script that creates a FLUKA input with the NOVCoDA (48 bar) model
The first step is to calculate all the needed coordinates and geometries required 
"""


import numpy as np
import os
import random
from NOVO_to_FLUKA_coordinates import NOVO_to_FLUKA_coordinate_transform

# First initialize script, point to where the information is located


def list_to_str_vals(a_list):
    # Simple function to convert list of floats to string

    # If there is only one element in the list, return the string
    if len(a_list) == 1:
        return str(round(0.1 * a_list[0], 3))
    
    output = ""
    for value in a_list:
        output += " " + str(round(0.1 * value, 3))

    return output[1:]

def list_to_str(a_list):
    """Will simply create a single string from all elements in a list (one dimension)"""
    output = ""
    for value in a_list:
        output += "" + str(value)

    return output


def _calculate_RPP_coordinates(layer_N, layer_N_orientation, scint_pos, scints_in_layer,
                               bar_width, bar_length, readout_width, readout_length, readout_thickness,
                               alpha, scint_spacings, layer_spacings):
    """
    Helper function for create_fluka_input()
    Calculates the (X, Y, Z)_min, max coordinates given a scintillator number ["01" - "48"]
    Returns a list (len 6) with Xs, Ys and Zs
    """
    layer_N = int(layer_N[-2:])
    

    # For scintillators running along the Y-axis
    if layer_N_orientation == "along_Y":

        # Bar coordinates
        X_min = - bar_length / 2
        X_max = + bar_length / 2

        # Translating to relative positions ([1, 2, 3] -> [-1, 0, 1] or [1, 2, 3, 4] -> [-1.5, -0.5, 0.5, 1.5])
        relative_scint_pos = scint_pos - (scints_in_layer - 1) / 2

        # Even number of scints in the layer
        if scints_in_layer % 2 == 0:
            Y_min = (relative_scint_pos) * bar_width + relative_scint_pos * scint_spacings[layer_N - 1]

        # Odd number of scints in the layer (center scintillator lies on Y=0)
        elif scints_in_layer % 2 != 0:
            Y_min = (relative_scint_pos - 0.5) * bar_width + relative_scint_pos * scint_spacings[layer_N - 1]

        Y_max = Y_min + bar_width

        # Readout electronics coordinates
        XR_min = X_min - readout_length
        XR_max = X_max + readout_length

        YR_min = Y_min - alpha
        YR_max = Y_max + (readout_width - alpha - bar_width)

        # Plane coordinates for defining readout electronics casings/holes
        plane_pos = X_max
        plane_neg = X_min
        plane_Hpos = X_max + readout_thickness
        plane_Hneg = X_min - readout_thickness

    # For scintillators running along the X-axis
    elif layer_N_orientation == "along_X":

        # Bar coordinates

        # Translating to relative positions ([1, 2, 3] -> [-1, 0, 1] or [1, 2, 3, 4] -> [-1.5, -0.5, 0.5, 1.5])
        relative_scint_pos = scint_pos - (scints_in_layer - 1) / 2

        # Even number of scints in the layer
        if scints_in_layer % 2 == 0:
            X_min = (relative_scint_pos) * bar_width + relative_scint_pos * scint_spacings[layer_N - 1]

        # Odd number of scints in the layer (center scintillator lies on Y=0)
        elif scints_in_layer % 2 != 0:
            X_min = (relative_scint_pos - 0.5) * bar_width + relative_scint_pos * scint_spacings[layer_N - 1]
        
        X_max = X_min + bar_width

        Y_min = - bar_length / 2
        Y_max = + bar_length / 2

        # Readout electronics coordinates
        XR_min = X_min - alpha
        XR_max = X_max + (readout_width - alpha - bar_width)

        YR_min = Y_min - readout_length
        YR_max = Y_max + readout_length

        # Plane coordinates for defining readout electronics casings/holes
        plane_pos = Y_max
        plane_neg = Y_min
        plane_Hpos = Y_max + readout_thickness
        plane_Hneg = Y_min - readout_thickness

    # Bar coordinates
    Z_min = (layer_N - 1) * bar_width + sum(layer_spacings[:layer_N - 1])
    Z_max = Z_min + bar_width

    # Readout electronics coordinates
    ZR_min = Z_min - alpha
    ZR_max = Z_max + (readout_width - alpha - bar_width)

    # Readout electronic hole coordinates
    XH_min = XR_min + readout_thickness
    XH_max = XR_max - readout_thickness

    YH_min = YR_min + readout_thickness
    YH_max = YR_max - readout_thickness

    ZH_min = ZR_min + readout_thickness
    ZH_max = ZR_max - readout_thickness

    return [[X_min, X_max, Y_min, Y_max, Z_min, Z_max], 
            [XR_min, XR_max, YR_min, YR_max, ZR_min, ZR_max],
            [XH_min, XH_max, YH_min, YH_max, ZH_min, ZH_max],
            [plane_pos, plane_neg, plane_Hpos, plane_Hneg, 0, 0]]

def create_FLUKA_input(
        output_path: str, 
        layer_structure: dict=None, layer_orientation: dict=None, inp_file_name: str=None, 
        readout_offset: int=3, custom_layer_spacings: list=None, custom_scintillator_spacing: list=None, 
        lattice_copies: int=None, lattice_angles: list=None) -> None:
    """
    Creates a complete FLUKA input with the NOVCoDA detector, a dummy water phantom and a dummy proton beam

    Inputs:
    -output_path: Where should the .inp file be saved?
    -layer_structure: How are the layers structured?
        Ex 3x3 detector: 
            layer_structure = {
            "Layer01": ["01", "02", "03"],
            "Layer02": ["04", "05", "06"],
            "Layer03": ["07", "08", "09"]
            }
        Default: 4 scint x 12 layers
    -layer_orientation: How are the layers oriented? IMPORTANT: Must be the same number of layers as layer_structure
            Ex 3x3 detector: 
            layer_structure = {
            "Layer01": "along_X",
            "Layer02": "along_Y",
            "Layer03": "along_X"
            }
        Default: 4 scint x 12 layers

    -inp_file_name: What should the .inp be called?
        Default: None (will turn into "NOVCoDA_model.inp)
    -readout_offset: Offset coordinate for scintillator spacing on the readout electronics
        Default: 3 mm
    -custom_layer_spacing [None][mm]: List of layer spacings between each layer, i.e. [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        Default: 6 mm -> [6, 6, ..., 6], length: number of layers - 1   -> !Must match with layer_structure!
    -custom_scintillator_spacing [None][mm]: List of scintillator spacing in each layer, i.e [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
        Default 23 mm -> [23, 23, ..., 23]: length: number of layers    -> !Must match with layer_structure!
    -lattice_copies: How many copies of the detector should there be? Angular seperation between detectors is 360 degrees / (lattice_copies + 1)
        Default: None
    """

    bar_width = 12 # [mm]
    bar_length = 140 # [mm]

    readout_width = 27 # [mm]
    readout_length = 120 # [mm]
    readout_thickness = 2 # [mm]

    layer_spacing = 6 # [mm]
    scintillator_spacing = 23 # [mm]

    if layer_structure is None:

        # Structure of the default detector along with corresponding names
        layer_structure = {
            "Layer01": ["01", "02", "03", "04"],
            "Layer02": ["05", "06", "07", "08"],
            "Layer03": ["09", "10", "11", "12"],
            "Layer04": ["13", "14", "15", "16"],
            "Layer05": ["17", "18", "19", "20"],
            "Layer06": ["21", "22", "23", "24"],
            "Layer07": ["25", "26", "27", "28"],
            "Layer08": ["29", "30", "31", "32"],
            "Layer09": ["33", "34", "35", "36"],
            "Layer10": ["37", "38", "39", "40"],
            "Layer11": ["41", "42", "43", "44"],
            "Layer12": ["45", "46", "47", "48"]
        }
    
    if layer_orientation is None:

        # Layer orientations of the default detector
        layer_orientation = {
            "Layer01": "along_X",
            "Layer02": "along_Y",
            "Layer03": "along_X",
            "Layer04": "along_Y",
            "Layer05": "along_X",
            "Layer06": "along_Y",
            "Layer07": "along_X",
            "Layer08": "along_Y",
            "Layer09": "along_X",
            "Layer10": "along_Y",
            "Layer11": "along_X",
            "Layer12": "along_Y"
        }

    if custom_layer_spacings is None:
        layer_spacings = [layer_spacing for i in range(11)]
    else:
        layer_spacings = custom_layer_spacings

    if custom_scintillator_spacing is None:
        scint_spacings = [scintillator_spacing for i in range(12)]
    else:
        scint_spacings = custom_scintillator_spacing

    # Value for centering the detector before rotation/translation
    centering_NOVO_rot = round(-0.5 * (12 * bar_width + sum(layer_spacings)), 3)

    bar_readout_coordinates = []

    # Loading all coordinates
    for layer_N, scints in layer_structure.items():
        scint_pos = 0
        scints_in_layer = len(scints)
        layer_N_orientation = layer_orientation[layer_N]
        for scint_M in scints:
            scint_pos += 1
            bar_readout_coordinates.append(_calculate_RPP_coordinates(layer_N, layer_N_orientation, scint_pos, scints_in_layer,
                                                                    bar_width, bar_length,readout_width, readout_length, readout_thickness, 
                                                                    readout_offset, scint_spacings, layer_spacings))

    # Calculating case coordinates (for lattice purposes) (+ 1 cm safety margin in all directions)
    case_min_x = min(np.array(bar_readout_coordinates)[:, 1, 0]) - 10.0
    case_max_x = max(np.array(bar_readout_coordinates)[:, 1, 1]) + 10.0

    case_min_y = min(np.array(bar_readout_coordinates)[:, 1, 2]) - 10.0
    case_max_y = max(np.array(bar_readout_coordinates)[:, 1, 3]) + 10.0

    case_min_z = min(np.array(bar_readout_coordinates)[:, 1, 4]) - 10.0
    case_max_z = max(np.array(bar_readout_coordinates)[:, 1, 5]) + 10.0

    case_coordinates = [case_min_x, case_max_x, case_min_y, case_max_y, case_min_z, case_max_z]

    # Voids planes between scintillator layers
    void_Zs = np.unique(np.array(bar_readout_coordinates)[:, 0, 4:6])
    void_Zs = np.array([0.5 * void_Zs[2 * i - 1] + 0.5 * void_Zs[2 * i] for i in range(1, int(0.5 * len(void_Zs)))])

    if lattice_angles is None and lattice_copies is not None:
        assert lattice_copies >= 1, f"lattice_copies: {lattice_copies} must be an integer of 1 or higher"
        lattice_angles = [360 / (i + 2) for i in range(lattice_copies)] # Default was it to evenly spread out the copies

    # Assign default .inp file name if no name is given
    if inp_file_name is None:
        inp_file_name = "NOVCoDA_model.inp"
    else:
        if inp_file_name[-4:] != ".inp":
            inp_file_name += ".inp"
    
    # If .inp file already exists, create a copy of it to avoid overriding a previous version
    n_copy = 0
    while os.path.exists(output_path + r"\\" + inp_file_name):
        n_copy += 1
        inp_file_name = "NOVCoDA_model(" + str(n_copy) + ").inp"

    f = open(output_path + r"\\" + inp_file_name, "w")

    # -----------------------START OF FLUKA INPUT-----------------------

    # Correct format template for FLUKA/FLAIR card. All inputs must be strings!
    # f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("","","","","","","",""))
    f.write("* NOVCoDA model with scintillator casing details")

    # --------------------DEFAULTS, BEAM AND ROTATION-------------------
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("TITLE","","","","","","","OLDFLAIR"))

    f.write("\n* Simulation defaults plus physics cards that allows Coalescense and Evaporation (for PGs)")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("DEFAULTS","","","","","","","PRECISIO"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("PHYSICS","3.0","","","","","","EVAPORAT"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("PHYSICS","1.0","","","","","","COALESCE"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("PHYSICS","1.0","0.005","0.15","2.0","2.0","2.","IONSPLIT"))

    f.write("\n* Beam characteristics and beam position")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("BEAM","-0.190","0.0","0.0","-1.24","-0.85","0.0","PROTON"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("BEAMPOS","0.0","0.0","-47.2","0.0","0.0","",""))

    f.write("\n* NOVCoDA rotation cards. Adjust azimuthal angles for rotations")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","100.","0.0","0.0","0.0","0.0",f"{-0.1 * centering_NOVO_rot + 20.0}","NOVO_rot1"))   # Isocenter to detector surface distance: 20 cm
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0","90.0","0.0","0.0",f"{0.1 * centering_NOVO_rot}","NOVO_rot1"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","100.","0.0","90.0","0.0","0.0","0.0","NOVO_rot1"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0","90.0","0.0","0.0","0.0","NOVO_rot1"))

    # Lattice rotation cards
    if lattice_copies is not None:
        for angle_num, angle in enumerate(lattice_angles):
            f.write(f"\n* Lattice card for copy {angle_num + 2}, rotation: {angle} degrees")
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","100.","0.0","0.0","0.0","0.0",f"{-0.1 * centering_NOVO_rot + 20.0}",f"NOVO_rot{angle_num + 2}"))   # Isocenter to detector surface distance: 20 cm
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0","90.0","0.0","0.0",f"{0.1 * centering_NOVO_rot}",f"NOVO_rot{angle_num + 2}"))
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","100.","0.0","90.0","0.0","0.0","0.0",f"NOVO_rot{angle_num + 2}"))
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0","90.0","0.0","0.0","0.0",f"NOVO_rot{angle_num + 2}"))
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0",f"{angle}","0.0","0.0","0.0",f"NOVO_rot{angle_num + 2}"))
            f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300.","0.0",f"{-angle}","0.0","0.0","0.0",f"lattis{angle_num + 1}"))

    # ------------------------------GEOMETRY----------------------------
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("GEOBEGIN","","","","","","","COMBNAME"))
    f.write("\n    0    0")

    # Target, void and blackbody
    f.write("\n* Black body")
    f.write("\nSPH blkbody    0.0 0.0 0.0 100000.0") #Free format card
    f.write("\n* Void sphere")
    f.write("\nSPH Void       0.0 0.0 0.0 10000.0") #Free format card
    f.write("\n* Water dummy - needed for dose to water")
    f.write("\nSPH wdum       100050.0 0.0 0.0 10.0") #Free format card
    f.write("\n* Air subsphere")
    f.write("\nSPH Air       0.0 0.0 0.0 1000.0") #Free format card

    # -------Dummy water target-------
    f.write(f"\nRCC target    0.0 0.0 0.0 0.0 -20.0 20.0 7.5")

    # -------Lattice regions--------
    if lattice_copies is not None:
        f.write(f"\n* Lattice copies")
        for copy in range(len(lattice_angles)):
            f.write(f"\nstart_transform NOVO_rot{copy + 2}")
            f.write(f"\nRPP case1     {list_to_str_vals(case_coordinates)}")
            f.write(f"\nend_transform")

    # -------NOVCoDA model-------
    f.write("\n* -----NOVCoDA model------")
    f.write("\n$start_transform NOVO_rot1") #Free format card

    # Writing case geometry (encapsulating the whole detector for lattice purposes)
    f.write(f"\nRPP case1     {list_to_str_vals(case_coordinates)}")

    # Writing scintillator bar geometries
    f.write(f"\n*Scintillator bars (01 - 48)")
    for bar_num, bar in enumerate(bar_readout_coordinates):
        bar_name = ("0" + str(bar_num + 1))[-2:]
        f.write(f"\nRPP bar{bar_name}     {list_to_str_vals(bar[0])}")

    # Writing readout electronics (full lengths)
    f.write(f"\n*Readout electronic casings (01 - 48)")
    for bar_num, bar in enumerate(bar_readout_coordinates):
        bar_name = ("0" + str(bar_num + 1))[-2:]
        f.write(f"\nRPP elec{bar_name}    {list_to_str_vals(bar[1])}")

    # Writing readout electronics holes (full lengths)
    f.write(f"\n*Readout electronic holes (01 - 48)")
    for bar_num, bar in enumerate(bar_readout_coordinates):
        bar_name = ("0" + str(bar_num + 1))[-2:]
        f.write(f"\nRPP hole{bar_name}    {list_to_str_vals(bar[2])}")

    # Writing readout electronics holes (full lengths)
    f.write(f"\n*Intersection planes for readout electronic casings/holes")

    # Layers for defining readout electronics and readout electronic holes
    f.write(f"\nYZP alX_pos   {str(round(0.1 * 70, 3))}")
    f.write(f"\nYZP alX_neg   {str(round(0.1 * -70, 3))}")  
    f.write(f"\nYZP alX_Hpos  {str(round(0.1 * 72, 3))}")  
    f.write(f"\nYZP alX_Hneg  {str(round(0.1 * -72, 3))}")
    
    f.write(f"\nXZP alY_pos   {str(round(0.1 * 70, 3))}")
    f.write(f"\nXZP alY_neg   {str(round(0.1 * -70, 3))}")  
    f.write(f"\nXZP alY_Hpos  {str(round(0.1 * 72, 3))}")  
    f.write(f"\nXZP alY_Hneg  {str(round(0.1 * -72, 3))}")

    # Layers for defining the voids per layer
    f.write(f"\nIntersection planes for void definition")
    f.write(f"\nYZP vdX_pos   {str(round(0.1 * 75, 3))}")
    f.write(f"\nYZP vdX_neg   {str(round(0.1 * -75, 3))}") 
    f.write(f"\nXZP vdY_pos   {str(round(0.1 * 75, 3))}")
    f.write(f"\nXZP vdY_neg   {str(round(0.1 * -75, 3))}") 

    # Void planes between scintillator layers
    voidZ_name = 0
    for voidZ in void_Zs:
        voidZ_name += 1
        f.write(f"\nXYP vdZ{("0" + str(voidZ_name))[-2:]}_{("0" + str(voidZ_name + 1))[-2:]}  {voidZ}")

    f.write("\n$end_transform") #Free format card
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("END","","","","","","",""))



    # ----------------------------REGIONS--------------------------------
    f.write(f"\n* Scintillator regions: MREG = 1 - {layer_structure[list(layer_structure)[-1]][-1]}") 
    for bar_num, bar in enumerate(bar_readout_coordinates):

        bar_name = ("0" + str(bar_num + 1))[-2:]
        layer_N = next((layer for layer, scints in layer_structure.items() if bar_name in scints), None)
        layer_N_orientation = layer_orientation[layer_N]
        plane = layer_N_orientation[-1]

        f.write(f"\nBAR{bar_name}       5 +bar{bar_name} -al{plane}_neg +al{plane}_pos")

    f.write("\n* Black hole")
    f.write("\nBLKBODY      5 +blkbody -void")

    f.write("\n* Void around")
    if lattice_copies is not None:
        f.write(f"\nVOID      5 +void -VOXEL -case1 {list_to_str_vals([f"-case{i + 2}" for i in range(len(lattice_angles))])}")
    else:
        f.write(f"\nVOID      5 +void -VOXEL -case1")
    
    if lattice_copies is not None:
        for copy in range(len(lattice_angles)):
            f.write(f"\nCASE{copy + 2}        5 +case{copy + 2}")
    
    f.write("\n* Void boxes")
    
    for layerN, orientation in layer_orientation.items():
        plane = orientation[-1]
        next_layer_text = ""
        previous_layer_text = ""

        # Include current detector layer elecs and bars
        current_layer_elec_text = list_to_str([f"-elec{i}" for i in layer_structure[layerN]])
        current_layer_bar_text = list_to_str([f"-bar{i}" for i in layer_structure[layerN]])
        
        # Include detector layer below except for the first layer
        if layerN != list(layer_orientation)[0]:
            next_layer = "Layer" + f"0{int(layerN[-2:]) - 1}"[-2:]
            next_layer_text = list_to_str([f"-elec{i} -bar{i}" for i in layer_structure[next_layer]])

        # Include detector layer above except for the last layer
        if layerN != list(layer_orientation)[-1]:
            previous_layer = "Layer" + f"0{int(layerN[-2:]) + 1}"[-2:]
            previous_layer_text = list_to_str([f"-elec{i} -bar{i}" for i in layer_structure[previous_layer]])
        
        f.write(f"\nVBOX{layerN[-2:]}        5 " +
                f"-vd{plane}_neg +al{plane}_pos {current_layer_elec_text} {next_layer_text} {previous_layer_text}" + 
                f"|-al{plane}_pos +al{plane}_neg {current_layer_bar_text} {next_layer_text} {previous_layer_text}" + 
                f"|-al{plane}_neg +vd{plane}_pos {current_layer_elec_text} {next_layer_text} {previous_layer_text}")

    f.write("\n* Readout electronic shells")
    for layerN, orientation in layer_orientation.items():
        plane = orientation[-1]

        for barM in layer_structure[layerN]:
            f.write(f"\n ELC{barM}_n      5 +elec{barM} -hole{barM} -al{plane}_Hpos | +elec{barM} +al{plane}_Hpos -al{plane}_pos")
            f.write(f"\n ELC{barM}_p      5 +elec{barM} -hole{barM} +al{plane}_Hneg | +elec{barM} -al{plane}_Hneg +al{plane}_neg")

    f.write("\n* Air holes in readout electronic shells")  

    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("END","","","","","","",""))

    # Lattice cards
    for copy in range(len(lattice_angles)):
        f.write(f"\nLATTICE        CASE{copy + 2}                                                  lattis{copy + 2}")
    
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("GEOEND","","","","","","",""))


if __name__ == "__main__":
    PATH = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\Python-skript\Model_creator"

    # Structure of the default detector along with corresponding names
    layer_structure = {
        "Layer01": ["01", "02", "03", "04"],
        "Layer02": ["05", "06", "07", "08"],
        "Layer03": ["09", "10", "11", "12"],
        "Layer04": ["13", "14", "15", "16"],
        "Layer05": ["17", "18", "19", "20"],
        "Layer06": ["21", "22", "23", "24"],
        "Layer07": ["25", "26", "27", "28"],
        "Layer08": ["29", "30", "31", "32"],
        "Layer09": ["33", "34", "35", "36"],
        "Layer10": ["37", "38", "39", "40"],
        "Layer11": ["41", "42", "43", "44"],
        "Layer12": ["45", "46", "47", "48"]
    }

    # Layer oriententation of the default detector
    layer_oriententation = {
        "Layer01": "along_X",
        "Layer02": "along_Y",
        "Layer03": "along_X",
        "Layer04": "along_Y",
        "Layer05": "along_X",
        "Layer06": "along_Y",
        "Layer07": "along_X",
        "Layer08": "along_Y",
        "Layer09": "along_X",
        "Layer10": "along_Y",
        "Layer11": "along_X",
        "Layer12": "along_Y"
    }



    create_FLUKA_input(PATH)