################################################################################
#
#       sort_dicoms_impt.py
#
#       Script for setting up FLUKA simulation environment and sorting DICOM files
#       This is valid for IMPT plans
#
#
#
import os
import pydicom
from os.path import join as pjoin
import math as m
import string
import random
import shutil
import numpy as np
import argparse

# Error prevention
import pydicom.config
pydicom.config.enforce_valid_values = False

# Module import
import modules
################################################################################

#### Defining arguments
parser = argparse.ArgumentParser(epilog="See the wiki for more information at \
https://git.app.uib.no/particletherapyIFT/FRES/wikis/home")

parser.add_argument("--histories", help="Use to specify number of histories to add to START card", type=int)
args = parser.parse_args()

# Specifies number of particles to set in input file
if args.histories:
    histories = args.histories
else:
    histories = 1.25E6

def main():
    script_type = "sort"

    Modality = modules.define_modality("impt")

    # Define valid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    path_dcm = input('Provide the directory of the DICOM files: ')
    files = os.listdir(path_dcm)
    for file_rp in files:
        if "RP" in file_rp:
            input_dicom_file = path_dcm + "/" + file_rp
   		
    #Raystation compabilitet	
    ds = pydicom.dcmread(input_dicom_file)

    if 'IonBeamSequence' in ds:
        for beam in ds.IonBeamSequence:
            beam.TreatmentMachineName = "ProBeam360"
            ds.save_as(input_dicom_file)
    # Import all DICOM files
    ct_list, slice_location_list, dose_list, struct_list, plan_list = modules.get_dicoms(path_dcm, script_type)

    slice_no = 1
    cp = modules.get_dicom_ct_parameters(ct_list, slice_location_list, slice_no)
    pp = modules.get_dicom_rtplan_parameters(plan_list)[0]

    grid = modules.check_scoring_grids(pp, dose_list)

    # Remove invalid characters from name
    cp['patient_name'] = ''.join(c for c in cp['patient_name'] if c in valid_chars)

    # Creating new path if non-existing
    fluka_path = pjoin(path_dcm,"FLUKA_"+cp['patient_name']+"_"+pp['plan_name'])
    if not os.path.exists(fluka_path):
        os.makedirs(fluka_path)

    # Saving renamed DICOMs
    modules.save_dicoms(fluka_path, ct_list, slice_location_list, dose_list, struct_list, plan_list, cp['patient_name'], pp['plan_name'], pp)

    # Creating lists for FLUKA input parameters
    # Lists needed if more then ONE RT Plan is located in the folder
    dicom_positions = {'x':[], 'y':[], 'z':[]}
    scoring_grids = {'x_min_dose':[], 'y_min_dose':[], 'z_min_dose':[], 'x_max_dose':[], 'y_max_dose':[], 'z_max_dose':[],
                     'x_min_ct':[], 'y_min_ct':[], 'z_min_ct':[], 'x_max_ct':[], 'y_max_ct':[], 'z_max_ct':[]}

    for i in range(len(pp['beam_name_list'])):
        if grid == 1 and i == 0: # If use all equal grids and first run
            # Get corresponding dose parameters
            dp = modules.get_correct_dose_parameters(pp, dose_list, grid, i)
        if grid == 2: # If use of unequal grids. Run for all fields
            dp = modules.get_correct_dose_parameters(pp, dose_list, grid, i)
        # Calculates the translation of the voxel target in order to
        # get isocenter at origin in FLUKA

        dicom_positions['x'].append((cp['patient_position'][0]-pp['isocenter_list'][i][0]-cp['pixel_size'][0]/2.0)/10)
        dicom_positions['z'].append((cp['patient_position'][2]-pp['isocenter_list'][i][2]-cp['slice_thickness']/2.0)/10)

        if cp['orientation_vector'] == [1,0,0,0,-1,0]: # HEAD FIRST PRONE
            dicom_positions['y'].append(-(float(cp['patient_position'][1])-float(pp['isocenter_list'][i][1])-float(cp['pixel_size'][1])/2.0)/10)
        else:
            dicom_positions['y'].append((float(cp['patient_position'][1])-float(pp['isocenter_list'][i][1])-float(cp['pixel_size'][1])/2.0)/10)

        # Calculates the max and min values for scoring the same grid as the TPS
        # Number of bins defined above

        # Functions
        gridmin = lambda dp,iso,pxs: (dp-iso-pxs/2.0)/10.0
        gridmax = lambda xmin,db,pxs: xmin+(db*pxs)/10.0

        x_min_dose = gridmin(dp['dose_position'][0],pp['isocenter_list'][i][0],dp['pixel_size'][0])
        x_max_dose = gridmax(x_min_dose,dp['xbins_tps'],dp['pixel_size'][0])
        y_min_dose = gridmin(dp['dose_position'][1],pp['isocenter_list'][i][1],dp['pixel_size'][1])
        y_max_dose = gridmax(y_min_dose,dp['ybins_tps'],dp['pixel_size'][1])
        z_min_dose = gridmin(dp['dose_position'][2],pp['isocenter_list'][i][2],dp['slice_thickness'])
        z_max_dose = gridmax(z_min_dose,dp['zbins_tps'],dp['slice_thickness'])


        if cp['orientation_vector'] == [1,0,0,0,-1,0] and dp['orientation_vector'] == [-1,0,0,0,-1,0]:
            x_max_dose = (dp['dose_position'][0]-pp['isocenter_list'][i][0]+dp['pixel_size'][0]/2.0)/10.0
            x_min_dose = x_max_dose-(dp['xbins_tps']*dp['pixel_size'][0])/10.0
            y_min_dose = (-dp['dose_position'][1]+pp['isocenter_list'][i][1])/10.0
            y_max_dose = y_min_dose+(dp['ybins_tps']*dp['pixel_size'][1])/10.0

        global z_min_ct
        x_min_ct = dicom_positions['x'][i]
        x_max_ct = x_min_ct+(cp['columns']*cp['pixel_size'][0]/10.0)
        y_min_ct = dicom_positions['y'][i]
        y_max_ct = y_min_ct+(cp['rows']*cp['pixel_size'][1]/10.0)
        z_min_ct = dicom_positions['z'][i]
        z_max_ct = z_min_ct+(cp['number_of_slices']*cp['slice_thickness']/10)

        scoring_grids['x_min_dose'].append(x_min_dose); scoring_grids['y_min_dose'].append(y_min_dose); scoring_grids['z_min_dose'].append(z_min_dose)
        scoring_grids['x_max_dose'].append(x_max_dose); scoring_grids['y_max_dose'].append(y_max_dose); scoring_grids['z_max_dose'].append(z_max_dose)
        scoring_grids['x_min_ct'].append(x_min_ct); scoring_grids['y_min_ct'].append(y_min_ct); scoring_grids['z_min_ct'].append(z_min_ct)
        scoring_grids['x_max_ct'].append(x_max_ct); scoring_grids['y_max_ct'].append(y_max_ct); scoring_grids['z_max_ct'].append(z_max_ct)


    # Creates FLUKA/Flair input files. One for each separate beam.
    for i in range((pp['number_of_beams'])):
        create_dat_files(plan_list, fluka_path, i)
        create_input_files(fluka_path, pp, cp, dp, dicom_positions, scoring_grids, i)
        copy_and_rename_source(fluka_path, pp, i)

    print("\nFiles saved to: \n", fluka_path,"\n")

 # Function for FLUKA input file creation
def create_input_files(fluka_path, pp, cp, dp, dicom_positions, scoring_grids, i):

    # Define input file. DO NOT remove beam name from filename, as it is used for field weighting
    field_path = pjoin(fluka_path,pp['beam_name_list'][i])
    if not os.path.exists(field_path):
        os.makedirs(field_path)

    file_name = pjoin(field_path, str(pp['beam_name_list'][i])+".inp")
    f = open(file_name,"w")

    try:
        range_shifter = create_range_shifter(pp,i,scoring_grids)
    except:
        pass

    # Correctly format for FLUKA/FLAIR card. All inputs must be strings!
    # f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("","","","","","","",""))
    f.write("* Patient name: "+str(cp['patient_name']))
    f.write("\n* Plan name: "+str(pp['plan_name_list'][i]))
    f.write("\n* Treatment field: "+str(pp['beam_name_list'][i]))
    f.write("\n* Number of fractions: "+str(pp['no_of_fractions']))
    f.write("\n* Isocenter position in DICOM coordinate system [x,y,z] [mm]: "+str( [round(iso,3) for iso in  map(float, pp['isocenter_list'][i])] ) )
    f.write("\n* Maximum beam energy: "+str(float(pp['maximum_energy_list'][i])*-1000.0)+" MeV") # Times -1000 to get MeV and positive value
    f.write("\n* Minimum beam energy: "+str(float(pp['minimum_energy_list'][i])*-1000.0)+" MeV") # Times -1000 to get MeV and positive value
    f.write("\n* Gantry angle: "+str(pp['gantry_angle_list'][i])+" deg")
    f.write("\n* Patient support angle (table rotation): "+str(pp['patient_support_angle'][i])+" deg")
    f.write("\n* Table top roll angle: "+str(pp['tabletop_roll_angle'][i])+" deg")
    f.write("\n* Table top pitch angle: "+str(pp['tabletop_pitch_angle'][i])+" deg")
    f.write("\n* Treatment Machine: "+pp['treatment_machine'][i])
    f.write("\n* Number of spots for this treatment field: "+str(pp['spot_number_list'][i]))
    f.write("\n* The following numbers are for all fractions and are only valid for CAP_GENERAL at HUS:")
    f.write("\n* Total number of primaries for this field: "+str("%12.11e"%particles_per_field))
    f.write("\n* Total number of primaries for all fields combined: "+str("%12.11e"%total_number_of_particles))
    f.write("\n* Scoring bins [x,y,z]: "+str([dp['xbins_tps'],dp['ybins_tps'],dp['zbins_tps']]))
    f.write("\n* Scoring bin size [x,y,z] [mm]: "+str([dp['pixel_size'][0],dp['pixel_size'][1],dp['slice_thickness']]))

    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("TITLE","","","","","","","OLDFLAIR"))
    f.write("\nTPS recalculation")
    f.write("\n* Needed due to the high number of regions")
    f.write("\n* in the dicom image. Can be further increased.")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("GLOBAL","5000.","","","","","","OLDFLAIR"))
    f.write("\n* Set the defaults for precision simulations")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("DEFAULTS","","","","","","","PRECISIO"))
    f.write("\n* Define the beam characteristics.")
    f.write("\n* Maximum energy and particle type.")
    f.write("\n* Maximum energy: "+str(float(pp['maximum_energy_list'][i])*-1000.0)+" MeV") # Times -1000 to get MeV and positive value
    f.write("\n* Minimum energy: "+str(float(pp['minimum_energy_list'][i])*-1000.0)+" MeV") # Times -1000 to get MeV and positive value
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("BEAM",str(pp['maximum_energy_list'][i]),"","","","","",str(pp['particle_type_list'][i])))
    f.write("\n* Needed for source routine.")
    f.write("\n* User must compile source file.")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("SOURCE","","","","","","",""))

    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("GEOBEGIN","","","","","","","COMBNAME"))
    f.write("\n* Translates the dicom image into the")
    f.write("\n* right position according to the dicom images.")
    f.write("\n* Filename for the .vxl file must be added by user.")
    f.write("\n* ..+....1....+....2....+....3....+....4....+....5....+....6....+....7..")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("VOXELS",str(dicom_positions['x'][i]),str(dicom_positions['y'][i]),str(dicom_positions['z'][i]),"","","",""))
    f.write("\n    0    0")
    f.write("\n* Black body")
    f.write("\nSPH blkbody    0.0 0.0 0.0 100000.0") #Free format card
    f.write("\n* Void sphere")
    f.write("\nSPH void       0.0 0.0 0.0 10000.0") #Free format card
    f.write("\n* Water dummy - needed for dose to water")
    f.write("\nSPH wdum       100050.0 0.0 0.0 10.0") #Free format card

    try:
        f.write(range_shifter['start_transform'])
        f.write(range_shifter['RPP_position_1'])
        f.write(range_shifter['RPP_position_2'])
        f.write(range_shifter['RPP_comment'])
        f.write(range_shifter['RPP'])
        f.write(range_shifter['end_transform'])
    except:
        pass

    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("END","","","","","","",""))
    f.write("\n* Black hole")
    f.write("\nBLKBODY      5 +blkbody -void")
    f.write("\n* Void around")

    try:
        f.write("\nVOID         5 +void -VOXEL -"+str(pp['range_shifter_info'][i]['range_shifter_ID']))
    except:
        f.write("\nVOID         5 +void -VOXEL")

    f.write("\n* Water dummy")
    f.write("\nWDUM         5 +wdum")
    try:
        f.write(range_shifter['REGION_comment'])
        f.write(range_shifter['REGION'])
    except:
        pass

    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("END","","","","","","",""))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("GEOEND","","","","","","",""))

    f.write("\n* ..+....1....+....2....+....3....+....4....+....5....+....6....+....7..")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ASSIGNMA","BLCKHOLE","BLKBODY","","","","",""))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ASSIGNMA","VACUUM","VOID","","","","",""))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ASSIGNMA","WATER","WDUM","","","","",""))
    f.write("\n*Voxel cage")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ASSIGNMA","VACUUM","VOXEL","","","","",""))

    try:
        f.write(range_shifter['ASSIGNMA_comment'])
        f.write(range_shifter['ASSIGNMA'])
    except:
        pass

    # USERWEIG card
    f.write("\n* Needed for dose to water scoring")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("USERWEIG","","","3.","1.","","0.0",""))
    
    # USERDUMP card
    f.write("\n* Necessary for mgdraw to run")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("USERDUMP","100.","93.","0.0","1.0","","","test"))
    
    # PHYSICS
    f.write("\n* Activate coalescence")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("PHYSICS","1.","","","","","","COALESCE"))
    
    f.write("\n* Activate evaporation")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("PHYSICS","3.","","","","","","EVAPORAT"))
    
    # TRANSPORT
    f.write("\n* Deltaray generation threshold")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("DELTARAY","0.00001","","","","","",""))
    
    f.write("\n* Activate ion transport")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("IONTRANS","HEAVYION","","","","","",""))

    # Scoring dose to water for all particles with TPS scoring regions and bins
    f.write("\n* Scores dose to water for all particles, same region and bins as TPS")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","ALL-PART","-50",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"DoseH2O"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring LET x Fluence for protons with TPS scoring regions and bins
    f.write("\n* Scores LET x Fluence for protons, same region and bins as TPS")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","PROTON","-40",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"LET"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring LET**2 x Fluence for protons with TPS scoring regions and bins
    f.write("\n* Scores LET**2 x Fluence for protons, same region and bins as TPS")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","PROTON","-41",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"LETsq"))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring Rorvik RBE_max with TPS scoring regions and bins
    f.write("\n* Scores Rorvik RBE_max, same region and bins as TPS")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","PROTON","-60",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"RoRBEmx"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring Mairani RBE_max with TPS scoring regions and bins
    f.write("\n* Scores Mairani RBE_max, same region and bins as TPS")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","ALL-PART","-70",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"MaRBEmx"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring Belli RBE_max with TPS scoring regions and bins
    f.write("\n* Scores Belli RBE_max, same region and bins as TPS")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","PROTON","-65",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"BeRBEmx"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring Belli RBE_min with TPS scoring regions and bins
    f.write("\n* Scores Belli RBE_min, same region and bins as TPS")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","PROTON","-66",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"BeRBEmn"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring dose to medium for all particles with TPS scoring regions and bins
    f.write("\n* Scores dose to medium for all particles, same region and bins as TPS")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","DOSE","-21",str(scoring_grids['x_max_dose'][i]),str(scoring_grids['y_max_dose'][i]),str(scoring_grids['z_max_dose'][i]),"DOSE2MED"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_dose'][i]),str(scoring_grids['y_min_dose'][i]),str(scoring_grids['z_min_dose'][i]),str(dp['xbins_tps']),str(dp['ybins_tps']),str(dp['zbins_tps'])," &"))

    # Scoring of dose over each voxel
    # May be too many bins for FLUKA
    f.write("\n* Scores dose over the whole target.")
    f.write("\n* One bin for each voxel.")
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN","10.","DOSE","-23",str(scoring_grids['x_max_ct'][i]),str(scoring_grids['y_max_ct'][i]),str(scoring_grids['z_max_ct'][i]),"DoseVOX"))
    f.write("\n*{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}"\
            .format("USRBIN",str(scoring_grids['x_min_ct'][i]),str(scoring_grids['y_min_ct'][i]),str(scoring_grids['z_min_ct'][i]),str(cp['columns']),str(cp['rows']),str(cp['number_of_slices'])," &"))

    # Range shifter
    try:
        f.write(range_shifter['ROT-DEFI'])
        f.write("\n* Approximate start position of beam")
        f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("!point",str(source_pos[0]),str(source_pos[1]),"0","","2000","","startpos"))
    except:
        pass

    f.write("\n* Set the random number seed")
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("RANDOMIZ","1.0",str(random.randrange(1, 9.E8)),"","","","",""))

    f.write("\n* Set the number of primary histories to be simulated in the run")
    f.write("\n* Number of spots for this treatment field: "+str(pp['spot_number_list'][i]))
    f.write("\n* The following numbers are only valid for CAP_GENERAL at HUS:")
    f.write("\n* Total number of primaries for this field: "+str("%12.11e"%particles_per_field))
    f.write("\n* Total number of primaries for all fields combined: "+str("%12.11e"%total_number_of_particles))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("START",str(histories),"","","","","",""))
    f.write("\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("STOP","","","","","","",""))

    f.close()
    return

# Bug with rotation is located here. #FIXME
def create_range_shifter(pp,i,scoring_grids):
    range_shifter = {}
    rot_angle = 180-pp['gantry_angle_list'][i]
    range_shifter['ROT-DEFI'] = "\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ROT-DEFI","300","",str(rot_angle),"","","","RS")
    range_shifter['start_transform'] = "\n$start_transform RS"
    range_shifter['end_transform'] = "\n$end_transform"
    range_shifter['RPP_comment'] = "\n* Range shifter"
    range_shifter['RPP_position_1'] = "\n* Move RPP so that it covers the beam trajectory"
    range_shifter['RPP_position_2'] = "\n* Use the startpos point as reference"

    range_shifter['RPP'] = "\nRPP "+str(pp['range_shifter_info'][i]['range_shifter_ID'])+"       "+str(scoring_grids['x_min_ct'][i])+" "+str(scoring_grids['x_max_ct'][i])+" 0.0 "+str(pp['range_shifter_info'][i]['range_shifter_WET']/10.0)+" "+str(scoring_grids['z_min_ct'][i])+" "+str(scoring_grids['z_max_ct'][i])
    range_shifter['REGION_comment'] = "\n* Range shifter"
    range_shifter['REGION'] = "\nRSHIFTER     5 "+str(pp['range_shifter_info'][i]['range_shifter_ID'])
    range_shifter['ASSIGNMA_comment'] = "\n* Range shifter"
    range_shifter['ASSIGNMA'] = "\n{0:<10.8s}{1:>10.10s}{2:>10.10s}{3:>10.10s}{4:>10.10s}{5:>10.10s}{6:>10.10s}{7:<8.8s}".format("ASSIGNMA","WATER","RSHIFTER","","","","","")

    return range_shifter

def create_dat_files(plan_list, fluka_path, i):
    #print("plan_list",plan_list)
    #print("fluka_path", fluka_path)
    for b in range(len(plan_list)):
        ds = pydicom.read_file(plan_list[b])
        pp = modules.get_dicom_rtplan_parameters(plan_list)[0]
        r = np.mean(pp['source_axis_distances'])/10.0 #distance from source to isocenter
        field_path = pjoin(fluka_path,pp['beam_name_list'][i])
        #print("field_path",field_path)
        if not os.path.exists(field_path):
            os.makedirs(field_path)


        ibs = ds.IonBeamSequence[i]
        # Create lists
        beam_energies = []; spot_position_x = []; spot_position_y = []; spot_position_z = []
        spot_weights = []; spot_size_x = []; spot_size_y = []; spot_size_z = []
        cosx = []; cosy = []; cosz = []

        # Covert gantry angle to radians
        gantry_angle = m.radians(ibs.IonControlPointSequence[0].GantryAngle)
        tabletop_roll_angle = m.radians(ibs.IonControlPointSequence[0].TableTopRollAngle) # Not fully supported yet
        patient_support_angle = m.radians(ibs.IonControlPointSequence[0].PatientSupportAngle)
        tabletop_pitch_angle = m.radians(ibs.IonControlPointSequence[0].TableTopPitchAngle) # Not supported yet

        gantry_angle -= tabletop_pitch_angle

        # Angles larger than 360 deg start at 0 deg.
        while gantry_angle >= 2*m.pi:
            gantry_angle -= 2*m.pi

        # Angles smaller than 0 deg start at 360 deg.
        while gantry_angle <= 0:
            gantry_angle += 2*m.pi

        # Define beam directions to find source position
        sourcecosx = m.sin(-gantry_angle)*m.cos(patient_support_angle)
        sourcecosy = m.cos(gantry_angle)
        sourcecosz = m.sin(-gantry_angle)*m.sin(-patient_support_angle)

        # Define source position
        sourceposx = -r*sourcecosx; sourceposy = -r*sourcecosy; sourceposz = -r*sourcecosz

        # Coordinate transformation functions
        fx = lambda x,y,ga,psa:x*m.cos(ga)*m.cos(psa)-y*m.sin(-psa)
        fy = lambda x,ga:x*m.sin(ga)
        fz = lambda x,y,ga,psa:x*m.cos(ga)*m.sin(-psa)+y*m.cos(psa)

        # Beam direction function
        cos = lambda a,b,c:-a/m.sqrt(a**2+b**2+c**2)

        # Loops for appending different beam parameters to predefined lists
        for h in range(0,ibs.NumberOfControlPoints,2):
            icps = ibs.IonControlPointSequence[h]

            # Spot sizes for x and y in gantry coordinate system (FWHM)
            magnetXspotsize = icps.ScanningSpotSize[0]/10.0
            magnetYspotsize = icps.ScanningSpotSize[1]/10.0

            for j in range(icps.NumberOfScanSpotPositions):
                # Coordinate displacements for x and y in gantry coordinate system
                magnetXdisp = ds.IonBeamSequence[i].IonControlPointSequence[h].ScanSpotPositionMap[2*j]/10.0
                magnetYdisp = ds.IonBeamSequence[i].IonControlPointSequence[h].ScanSpotPositionMap[2*j+1]/10.0
                # Coordinate displacements for x y and z in fluka coordinate system
                xdisp = fx(magnetXdisp,magnetYdisp,gantry_angle,patient_support_angle)
                ydisp = fy(magnetXdisp,gantry_angle)
                zdisp = fz(magnetXdisp,magnetYdisp,gantry_angle,patient_support_angle)

                # Adding spot sizes for fluka coordinate system (FWHM)
                spot_size_x.append(abs(fx(magnetXspotsize,magnetYspotsize,gantry_angle,patient_support_angle)))
                spot_size_y.append(abs(fy(magnetXspotsize,gantry_angle)))
                spot_size_z.append(abs(fz(magnetXspotsize,magnetYspotsize,gantry_angle,patient_support_angle)))

                # Final beam directions
                cosx.append(cos(sourceposx-xdisp,sourceposy-ydisp,sourceposz-zdisp))
                cosy.append(cos(sourceposy-ydisp,sourceposx-xdisp,sourceposz-zdisp))
                cosz.append(cos(sourceposz-zdisp,sourceposy-ydisp,sourceposx-xdisp))

                # Adding the nominal beam energies and the weights for the beam spots
                beam_energies.append(float(icps.NominalBeamEnergy))
                if ibs.IonControlPointSequence[h].NumberOfScanSpotPositions == 1:
                    spot_weights.append(icps.ScanSpotMetersetWeights)
                else:
                    spot_weights.append(icps.ScanSpotMetersetWeights[j])
        # No idea why this does work, but it does... Think it has something to do how FLUKA handles patients in prone postitions
        if pp['patient_orientation'] == "HFP":
            sourceposx = -sourceposx
            cosx[:] = [x*-1 for x in cosx]

        # Identifies position of source in fluka coordinate system. Marked by point in geoviewer
        global source_pos
        source_pos = [sourceposx, sourceposy, sourceposz]

        ##### Convert MU to number of particles ####################
        if i == 0:
            print(("\nThe treatment machine for this plan is "+pp['treatment_machine'][i]))
            print ("Note that spots from this plan is weighted by number of particles regardless of treatment machine.")
            print ("It may therefore not neccessarily be valid.")

        # Koefficients for converting MU to particles
        # CAP_GENERAL Scanning mode - 70 MeV algorith - Eclipse 11
        if pp['treatment_machine'][i]=='CAP_GENERAL':
            koeff1 = -7.1347
            koeff2 = 16091
            koeff3 = 940494
        elif pp['treatment_machine'][i]=='ProBeam360':
            # R50-R20-current
            koeff1=-2.24534932e+01
            koeff2=2.62823437e+04
            koeff3=4.84199653e+05

        else:
            print('Treatment machine has not been calibrated.')
        beam_energies = np.array(beam_energies) # convert to numpy
        spot_weights = np.array(spot_weights)
        beam_meter = ds.FractionGroupSequence[0].ReferencedBeamSequence[i].BeamMeterset
        final_cum_meter_weight = ibs.FinalCumulativeMetersetWeight

        # Second polynomial fit, normalized to max dose
        spot_weights = (koeff1*beam_energies**2 + koeff2*beam_energies + koeff3)*beam_meter*spot_weights/final_cum_meter_weight
        global particles_per_field
        particles_per_field = sum(spot_weights)*pp['no_of_fractions']

        if i == 0: # Run only once
            get_total_number_of_particles(ds, koeff1, koeff2, koeff3, pp)

        # Define dat file for respective treatment field
        data_file_name = pjoin(field_path, modules.format_filename(ibs.BeamName)+".dat")
        data_file = open(data_file_name,"w")

        # Write some general info
        data_file.writelines("Patient: "+pp['patient_name']+"   ----   Plan: "+pp['plan_name']+\
        "   ----   Field: "+pp['beam_name_list'][i]+"   ----   No of fractions: "+str(pp['no_of_fractions'])+"\n")
        data_file.writelines("Total number of primaries for all fractions: "+ str("%12.11e"%total_number_of_particles)\
        +"   ----   Number of primaries for this field for all fractions: "+ str("%12.11e"%particles_per_field)+"\n")
        data_file.writelines("%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s\n" %\
        ("Ek[GeV]", "xPos[cm]", "yPos[cm]", "zPos[cm]", "xSize[cm]", "ySize[cm]",\
        "zSize[cm]", "SpotWeight", "xDir[cos]", "yDir[cos]", "zDir[cos]"))
        # Writes to the .dat file(s) that can be imported into the source.f routine
        # The parameters are altered according to beam angle and patient orientation to have correspondence in FLUKA.

        if pp['treatment_machine'][i]=='CAP_GENERAL':
            EnergyDiffCoeff1=0
            EnergyDiffCoeff2=1/1000.
            EnergyDiffCoeff3=0
        elif pp['treatment_machine'][i]=='ProBeam360':
            EnergyDiffCoeff1=3.703283757989935e-08
            EnergyDiffCoeff2=0.0009728178654085563
            EnergyDiffCoeff3=0.000924900646946889
            #EnergyDiffCoeff1=-5.41079183e-08
            #EnergyDiffCoeff2=1.01140089e-03
            #EnergyDiffCoeff3=-8.48881931e-04
        elif pp['treatment_machine'][i]=='ProB360_Colombus':
            EnergyDiffCoeff1=3.703283757989935e-08
            EnergyDiffCoeff2=0.0009728178654085563
            EnergyDiffCoeff3=0.000924900646946889
        else:
            print('Treatment machine has not been calibrated')
            EnergyDiffCoeff1=0
            EnergyDiffCoeff2=1
            EnergyDiffCoeff3=0

        for value in range(pp['spot_number_list'][i]):
            data_file.writelines("%-12.6f%-12.2f%-12.2f%-12.2f%-12.2f%-12.2f%-12.2f%-12.4e%-12.6f%-12.6f%-12.6f\n" %\
            ((beam_energies[value]**2*EnergyDiffCoeff1+EnergyDiffCoeff2*beam_energies[value]+EnergyDiffCoeff3), sourceposx, sourceposy, sourceposz, spot_size_x[value], spot_size_y[value],\
            spot_size_z[value], spot_weights[value], cosx[value], cosy[value], cosz[value]))

        data_file.close()

def copy_and_rename_source(fluka_path, pp, i):
    field_path = pjoin(fluka_path,pp['beam_name_list'][i])
    if not os.path.exists(field_path):
        os.makedirs(field_path)

    script_path = os.path.dirname(os.path.abspath(__file__))
    #ad_path = pjoin(script_path,"additional_files")

    #copy additional files to patient-folder
    ad_path = pjoin(script_path,"additional_files")

    if i == 0:
        for directory in os.listdir(ad_path):
            if directory == "fluscw" or directory == "hus_calibration_curves"\
            or directory == "cli_files" or directory=="ProBeam360"\
            or directory == "comscw":
                subpath = pjoin(ad_path, directory)
                for adfile in os.listdir(subpath):
                    if directory == "cli_files":
                        if adfile.endswith(".shell"):
                            shutil.copy2(pjoin(subpath, adfile), fluka_path)
                    else:
                        shutil.copy2(pjoin(subpath, adfile), fluka_path)

    clipath = pjoin(ad_path, "cli_files")
    for adfile in os.listdir(clipath):
        if not adfile.endswith(".shell"):
            shutil.copy2(pjoin(clipath, adfile), field_path)

    source_path = pjoin(ad_path,"hus_source_files")
    source_path = pjoin(source_path,"source_HUS.f")
    source_name = pjoin(field_path,"source.f")
    shutil.copy2(source_path, source_name)

    # Read in the file
    filedata = None
    with open(source_name, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('filename.dat', pp['beam_name_list'][i]+".dat")

    # Write the file out again
    with open(source_name, 'w') as file:
      file.write(filedata)

def get_total_number_of_particles(ds, koeff1, koeff2, koeff3, pp):
    global total_number_of_particles
    total_number_of_particles = 0
    for i in range(len(ds.IonBeamSequence)):
        beam_meter = ds.FractionGroupSequence[0].ReferencedBeamSequence[i].BeamMeterset
        ibs = ds.IonBeamSequence[i]
        final_cum_meter_weight = ibs.FinalCumulativeMetersetWeight
        sum_weight = 0
        no_parts = 0
        for k in range(1,ibs.NumberOfControlPoints,2):
            icps = ibs.IonControlPointSequence[k]
            # Nominal beam energy had problems for beams with one energy. This hopefully fixes it.
            if "NominalBeamEnergy" in icps:
                energy = float(icps.NominalBeamEnergy)
            else:
                energy = float(ibs.IonControlPointSequence[k-1].NominalBeamEnergy)
            weight = icps.CumulativeMetersetWeight-sum_weight
            sum_weight += weight
            mu = beam_meter*weight/final_cum_meter_weight
            no_parts += (-koeff1*energy**2 + koeff2*energy + koeff3)*float(mu) # normed to max dose

        total_number_of_particles += no_parts

    total_number_of_particles *= pp['no_of_fractions']

if __name__ == '__main__':
    main()
