'''
Code for converting the FLUKA simulation data into nifti compressed files (.nii.gz).
'''
import numpy as np
import matplotlib.pyplot as plt
# library for treating nifti files
import nibabel as nib
import os
import dicom2nifti
import modules as modules

# Get coordinates of the FLUKA voxelcage
def get_voxelcage(dicom_path):
    script_type = "sort"
    Modality = modules.define_modality("impt")
    ct_list, slice_location_list, dose_list, struct_list, plan_list = modules.get_dicoms(dicom_path, script_type)
    slice_no = 1
    print(len(ct_list))
    cp = modules.get_dicom_ct_parameters(ct_list, slice_location_list, slice_no)
    pp = modules.get_dicom_rtplan_parameters(plan_list)[0]
    dicom_positions = {'x':[], 'y':[], 'z':[]}

    dicom_positions['x'].append((cp['patient_position'][0]-pp['isocenter_list'][0][0]-cp['pixel_size'][0]/2.0)/10)
    dicom_positions['z'].append((cp['patient_position'][2]-pp['isocenter_list'][0][2]-cp['slice_thickness']/2.0)/10)
    dicom_positions['y'].append((float(cp['patient_position'][1])-float(pp['isocenter_list'][0][1])-float(cp['pixel_size'][1])/2.0)/10)

    dicom_positions['x'].append(dicom_positions['x'][0]+(cp['columns']*cp['pixel_size'][0]/10.0))
    dicom_positions['y'].append(dicom_positions['y'][0]+(cp['rows']*cp['pixel_size'][1]/10.0))
    dicom_positions['z'].append(dicom_positions['z'][0]+(cp['number_of_slices']*cp['slice_thickness']/10))

    return dicom_positions

def convert_to_CT_coordinates(dicom_positions,dicom_path):
    CT_positions = {'x':[], 'y':[], 'z':[]}
    script_type = "sort"
    ct_list, slice_location_list, dose_list, struct_list, plan_list = modules.get_dicoms(dicom_path, script_type)
    slice_no = 1
    cp = modules.get_dicom_ct_parameters(ct_list, slice_location_list, slice_no)
    pp = modules.get_dicom_rtplan_parameters(plan_list)[0]

    CT_positions['x'].append(dicom_positions['x'][0]*10+cp['pixel_size'][0]/2.0 + pp['isocenter_list'][0][0])
    CT_positions['y'].append(dicom_positions['y'][0]*10+float(cp['pixel_size'][1])/2.0 + float(pp['isocenter_list'][0][1]))
    CT_positions['z'].append(dicom_positions['z'][0]*10+cp['slice_thickness']/2.0 + pp['isocenter_list'][0][2])

    return CT_positions,len(ct_list), cp['pixel_size'],cp['slice_thickness'],cp["columns"],cp["rows"],len(ct_list)


def create_array(filepath,dicom_path,particle_type):
    dicom_positions = get_voxelcage(dicom_path)
    CT_positions,_,_,_,shape_x,shape_y,shape_z = convert_to_CT_coordinates(dicom_positions,dicom_path)

  
    files = os.listdir(filepath)
    coordinates = []
    errors = 0
    # Reading pg and fn production data. The data is arranged in folder, with a file for each core used in the simulation. 
    for file in files:
        f = open(filepath + "/" + file, "r")
        for line in f:
            elements = np.array(line.split())
            # This try-except loop was necessary because of a bug in the fortran file
            # creating the simulation data (mgdraw_production.f). 
            # should be fixed now. if so, errors list should be empty. 
            try:
                if len(elements) < 15:
                    for i in range(len(elements)):
                        value_str = elements[i]
                        if len(value_str) > 10:
                            for j in range(1,len(value_str)):
                                if value_str[j] == "-":
                                    elements[i] = value_str[:j]
                                    elements = list(elements)
                                    elements.insert(i+1,value_str[j:])
                                    elements=np.array(elements)

                elements = elements.astype(float)
                if particle_type == "pg":
                    # for "old" mgdraw results
                    #coordinates.append(elements[9:12]) 
                    coordinates.append(elements[1:4])
                if particle_type == "fn":
                    #coordinates.append(elements[4:7])
                    coordinates.append(elements[1:4])
            except:
                errors+=1
                continue
    coordinates = np.array(coordinates)
    volume_shape = (shape_x, shape_y, shape_z)
   
    min_coords = [dicom_positions['x'][0],dicom_positions['y'][0], dicom_positions['z'][0]]
    max_coords = [dicom_positions['x'][1],dicom_positions['y'][1], dicom_positions['z'][1]]

    edges = [
        np.linspace(min_coords[i], max_coords[i], volume_shape[i] + 1)
        for i in range(3)
    ]
    hist, _ = np.histogramdd(coordinates, bins=edges)

    return hist

# Function to save the simulation results as nifti file. nifti_image is the dicom image series saved as a nifti image. used 
# to copy the affine matrix for saving pg/fn results. Se codeline 119-122.
def save_as_nifti(hist,output_file,nifti_image):
    ref_img = nib.load(nifti_image)
    ref_affine = ref_img.affine
    ref_shape = ref_img.shape 

    your_volume = hist.astype(np.float32)
    #flipped_volume = np.flip(your_volume, axis=1) #BUG: Flipping unecessary
    new_img = nib.Nifti1Image(your_volume, ref_affine)

    # 4. Save to file
    nib.save(new_img,output_file)

##########################################################################################
'''Example of use. Change if necessary'''
# Path of the saved DICOMS
dicom_path = "C:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Lunge/DICOMS"
# Path of the saved FLUKA results. Saved in folders such as fn_produced, pg_produced etc...
filepath = "C:/Users/amibe/OneDrive/Documentos/NOVO/Konferanser/ESTRO/simulerte_data/Results_lunge/100mill_50cores_emax/100mill_50cores_emax" + "/fn_produced"
hist_image = create_array(filepath,dicom_path,particle_type="fn") #specify particle type "fn" or "pg".
# Name of the output file
output_file = 'C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Lunge/fn_image.nii.gz' 
nifti_image = "C:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Lunge/dicom_nifti.nii.gz" #The DICOM image series saved as nifti (nii.gz)
save_as_nifti(hist_image,output_file,nifti_image)

##########################################################################################
'''Code for exporting DICOM image series to nifti file'''
#input_folder = "C:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Lunge/DICOMS/"
#output_file = "c:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/nifti_volume.nii.gz"
#dicom2nifti.convert_directory(input_folder, os.path.dirname(output_file))

