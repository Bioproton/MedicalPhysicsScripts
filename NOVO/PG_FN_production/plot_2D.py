import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from convert_to_nifti import get_voxelcage,convert_to_CT_coordinates
import pydicom
import modules as modules
from reconstruct_1d import *
'''Define pixel arrays''''
# Load PG/FN files
pixel_array_pg = load_nifti("C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/pg_image.nii.gz")
pixel_array_fn = load_nifti("C:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/fn_image.nii.gz")

# Load info about DICOM series
dicom_path = "C:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Hv_14/DICOMS"
dicom_positions = get_voxelcage(dicom_path)
CT_positions,pixel_size,slice_thickness,columns,rows,slices=convert_to_CT_coordinates(dicom_positions,dicom_path)
pixel_arr_ct = pydicom.dcmread("c:/Users/amibe/OneDrive/Documentos/NOVO/Data/CT_images_from_DP/Hv_14/DICOMS/CT.Image_61_hv-14.dcm").pixel_array

# Load dose
dose_path = "c:/Users/amibe/OneDrive/Documentos/NOVO/Data/Produced_images/Hv-14/Dose/FLUKA_DICOM_emax_rmdose/dose/FLK_Bio-dose1.1_hv-14_AMB_Field_2_u.dcm"
dose_list = [dose_path]
dp,_ = modules.get_dicom_dose_parameters(dose_list)
dose = pydicom.dcmread(dose_path)
dose_pixel_arr = dose.pixel_array

x_axis_dose = np.arange(dp['dose_position'][0]-dp['pixel_size'][0]/2,dp['dose_position'][0] + dp['xbins_tps']*dp['pixel_size'][0]-dp['pixel_size'][0]/2,dp['pixel_size'][0])
y_axis_dose = np.arange(dp['dose_position'][1]-dp['pixel_size'][1]/2,dp['dose_position'][1] + dp['ybins_tps']*dp['pixel_size'][1]-dp['pixel_size'][1]/2,dp['pixel_size'][0])


'''Plot '''
dose_threshold = 60000# Adjust as needed #100 for fn/pg
dose_map = dose_pixel_arr[60,:,:] #pixel_array_fn[:,:,60]

masked_dose = np.ma.masked_where(dose_map < dose_threshold, dose_map)
diff = (y_axis_dose[-1]-CT_positions['y'][1]) + (y_axis_dose[0]-CT_positions['y'][0])

plt.imshow(pixel_arr_ct*mask_3d[:,:,61], extent=[CT_positions['x'][0],CT_positions['x'][1], CT_positions['y'][0],CT_positions['y'][1]], origin='upper', cmap='gray')

''' for plotting pg/fn'''
#plt.imshow(masked_dose,extent=[CT_positions['x'][0],CT_positions['x'][1], CT_positions['y'][0],CT_positions['y'][1]], cmap ="jet",alpha = 0.75)
#plt.colorbar()

'''For plotting dose. Comment out for pg/fn plotting'''
plt.imshow(masked_dose,extent=[x_axis_dose[0],x_axis_dose[-1],y_axis_dose[0]-diff,y_axis_dose[-1]-diff], alpha = 0.7,origin = "upper",cmap ="jet")
plt.colorbar()
plt.imshow(pixel_arr_ct*mask_3d[:,:,61], extent=[CT_positions['x'][0],CT_positions['x'][1], CT_positions['y'][0],CT_positions['y'][1]], origin='upper', cmap='gray',alpha = 0.0)
plt.axis("off")
plt.show()

#plt.plot(x_axis,x_vals/600-330, color = "green")
#plt.plot(x_axis_dose,dose_x_vals/4e5-330)
