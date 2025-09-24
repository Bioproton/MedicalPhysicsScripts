'''
Code for converting the FLUKA simulation data into nifti compressed files (.nii.gz). This version ensures a standard pixel size for the PG/FN images, 
namely 1mm x 1mm x 3mm. 
'''
import numpy as np
import matplotlib.pyplot as plt
# library for treating nifti files
import nibabel as nib
import os
import dicom2nifti
import modules as modules
from scipy.ndimage import shift

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
    CT_positions,_,pixel_size,_,shape_x,shape_y,shape_z = convert_to_CT_coordinates(dicom_positions,dicom_path)

  
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
    shape_x_1mm = shape_x*pixel_size[0] # 310
    shape_y_1mm = shape_y*pixel_size[1] # 310
    volume_shape = (shape_x_1mm, shape_y_1mm, shape_z) 
   
    min_coords = [dicom_positions['x'][0],dicom_positions['y'][0], dicom_positions['z'][0]]
    max_coords = [dicom_positions['x'][1],dicom_positions['y'][1], dicom_positions['z'][1]]

    edges = [
        np.linspace(min_coords[i], max_coords[i], volume_shape[i] + 1)
        for i in range(3)
    ]
    hist, _ = np.histogramdd(coordinates, bins=edges)

    return hist

def save_as_nifti(hist,output_file,nifti_image):
    ref_img = nib.load(nifti_image)
    ref_affine = ref_img.affine
    # Setting pixelsize to 1 mm
    ref_affine[0][0] = -1 
    ref_affine[1][1] = -1
    ref_shape = ref_img.shape 

    your_volume = hist.astype(np.float32)
    new_img = nib.Nifti1Image(your_volume, ref_affine)

    # 4. Save to file
    nib.save(new_img,output_file)


def match_dose_to_pg_fn_images(dose_image_path, pg_image_path, save = False,output_dose = "", output_pg = ""):
    # Load pg image
    pg_image = nib.load(pg_image_path)

    # Find origin 
    pg_min_x = pg_image.header["qoffset_x"] # here: positive value, in reality negative
    pg_min_y = pg_image.header["qoffset_y"]

    # Load dose image
    dose_image = nib.load(dose_image_path)
    # Find origin
    dose_min_x = dose_image.header["qoffset_x"]
    dose_min_y = dose_image.header["qoffset_y"]

    # Load pixel arrays
    pg_array = pg_image.get_fdata()
    dose_array = dose_image.get_fdata()

    pg_shape = pg_array.shape
    dose_shape = dose_array.shape

    # Find shift values
    shift_x = dose_min_x - pg_min_x
    shift_y = dose_min_y - pg_min_y
    aligned_dose = shift(dose_array, shift=(-shift_x,-shift_y,0), mode='nearest')

    # Align to the smallest dimensions in each image
    aligned_dose =aligned_dose[:pg_shape[0],:,2:] #aligned_image_b[:310,:,2:] # start i z = 39 
    aligned_pg = pg_array[:,:dose_shape[1],:aligned_dose.shape[2]]

    # If save == True: save as nifti image. Generic affine matrix used here (np.eye). Adjust if necessary
    # output_dose = r"D:\Study2_dosereconstruction\testing\aligned_dose.nii.gz"
    # output_pg = r"r"D:\Study2_dosereconstruction\testing\aligned_pg.nii.gz")"
    if save:
        nifti_dose_aligned = nib.Nifti1Image(aligned_dose,np.eye(4))
        nifti_pg_aligned = nib.Nifti1Image(aligned_pg,np.eye(4))
        nib.save(nifti_dose_aligned,output_dose)
        nib.save(nifti_pg_aligned,output_pg)

    return aligned_dose, aligned_pg



