''' Script for reconstructing the 1d histograms of pg/fn production. Load pg and fn nifti-images, and plot along depth-axis '''


import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from convert_to_nifti import get_voxelcage,convert_to_CT_coordinates
import pydicom
import modules as modules

def load_nifti(filename):
    #pg_filename ="C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/pg_image.nii.gz"
    data = nib.load(filename)
    pixel_array = data.get_fdata()

    # When loading nifti-files, the images are rotated. Rotate back to correct value.
    pixel_array =  np.rot90(pixel_array, k=1) 
    return pixel_array


# Provide the directorty of the DICOM image series
def plot_1D_distribution(dicom_path,pixel_arr):
    dicom_positions = get_voxelcage(dicom_path)
    CT_positions,pixel_size,slice_thickness,columns,rows,num_slices = convert_to_CT_coordinates(dicom_positions,dicom_path)

    x_vals = np.zeros(pixel_arr.shape[1]) #x
    for j in range(pixel_arr.shape[0]): # y 
        for i in range(pixel_arr.shape[2]): #z
            x_vals_at_j_i = pixel_arr[j,:,i]
            x_vals+=x_vals_at_j_i

    # NB: Pass på at CT-positions[x][0] er midten av første voxel. så start burde være en halv voxel til venstre
    #x_axis = np.linspace(CT_positions['x'][0]-pixel_size[0]/2,CT_positions['x'][1]+pixel_size[0]/2,columns)
    x_axis = np.arange(CT_positions['x'][0]-pixel_size[0]/2, CT_positions['x'][0]+ columns*pixel_size[0]-pixel_size[0]/2,pixel_size[0])
    return x_axis,x_vals


'''Example of usage'''
pixel_array_pg = load_nifti("C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/pg_image.nii.gz")
pixel_array_fn = load_nifti("C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/fn_image.nii.gz")

dicom_path = "C:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Hv_14/DICOMS"
x_axis_pg,x_vals_pg = plot_1D_distribution(dicom_path,pixel_array_pg)
x_axis_fn,x_vals_fn = plot_1D_distribution(dicom_path,pixel_array_fn)
plt.figure(figsize=(8,6))
plt.plot(x_axis_pg,x_vals_pg,label = "PG")
plt.plot(x_axis_fn,x_vals_fn, label = "FN")
plt.plot(x_axis_dose,dose_x_vals/2e3, label = "Dose")
#plt.axvline(x=-37.519, color='green', linestyle='--', linewidth=1, label = "Dose falloff 50%")
#plt.axvline(x=-35.722660625, color='blue', linestyle='--', linewidth=1,label = "PG falloff 50%")
#plt.axvline(x=-37.539066875, color='gray', linestyle='--', linewidth=1,label = "PG falloff 20%")
#plt.axvline(x=-38.76953560000001, color='gray', linestyle='--', linewidth=1,label = "Dose falloff 20%")
#plt.ylim(0,64000)
#plt.xlim(-100,100)
plt.legend()
