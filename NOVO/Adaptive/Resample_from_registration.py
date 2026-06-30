import pydicom
import SimpleITK as sitk
import numpy as np
import os
from rt_utils import RTStructBuilder
import matplotlib.pyplot as plt

'''
Load dicom folders containing only CT images. The fixed dicom folder is the path to the reference image (planning CT). The moving dicom folder
is the path to the image to be registered (control CT). Important: The dicom reg file from RayStation is applied in the other direction (planning --> control), 
therefore the registration matrix needs to be inverted. 
'''

fixed_dicom_folder = r"C:\Users\amibe\OneDrive\Documentos\NOVO\Study3_HNC\Adaptive_weekly_5\pCT"
moving_dicom_folder = r"C:\Users\amibe\OneDrive\Documentos\NOVO\Study3_HNC\Adaptive_weekly_5\cCTs_w_reg_struct\week3\CT"
dicom_reg_file_path = r"c:\Users\amibe\OneDrive\Documentos\NOVO\Study3_HNC\Adaptive_weekly_5\cCTs_w_reg_struct\week3\REG1.2.752.243.1.1.20260128125310658.5050.63017.dcm"

output = r"C:\Users\amibe\OneDrive\Documentos\NOVO\Study3_HNC\Adaptive_weekly_5\cCTs_w_reg_struct\week3\output_week3_wo_mask"

'''Load dicom files from the specified folders.'''
reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames(moving_dicom_folder)
reader.SetFileNames(dicom_names)
image = reader.Execute()  
image = sitk.Cast(image, sitk.sitkFloat32)


reader2 = sitk.ImageSeriesReader()
dicom_names2 = reader2.GetGDCMSeriesFileNames(fixed_dicom_folder)
reader2.SetFileNames(dicom_names2)
image_pCT = reader2.Execute() 
image_pCT = sitk.Cast(image_pCT, sitk.sitkFloat32)


'''Compute the resampled image based on the reg file'''

ds = pydicom.dcmread(dicom_reg_file_path)

matrix = None

for reg in ds.RegistrationSequence:
    for mat in reg.MatrixRegistrationSequence:
        for m in mat.MatrixSequence:
            matrix = np.array(m.FrameOfReferenceTransformationMatrix).reshape(4,4)

matrix= np.linalg.inv(matrix) #Using the inverse

transform = sitk.AffineTransform(3)

R = matrix[:3, :3]
t = matrix[:3, 3]

transform.SetMatrix(R.flatten())
transform.SetTranslation(t)

resampled = sitk.Resample(
    image, #moving (normal)
    image_pCT,  #fixed (normal)                    # reference grid
    transform,
    sitk.sitkLinear,
    0.0,
    sitk.sitkFloat32
)

os.makedirs(output, exist_ok=True)
array = sitk.GetArrayFromImage(resampled)
#mask_array = sitk.GetArrayFromImage(resampled_mask)

# Get original files (for metadata reuse)
original_files = dicom_names2

for i in range(len(array)):
    slice_array = array[i]
    #slice_array_mask = mask_array[i]

    ds = pydicom.dcmread(original_files[i])
    slope = float(ds.RescaleSlope) #1.0
    intercept = float(ds.RescaleIntercept) #-1000
   
    stored = (slice_array - intercept) / slope
    #stored[slice_array_mask == 0] = 0.0
    stored = np.round(stored).astype(np.int16)



    ds.PixelData = stored.tobytes()
    position = list(image_pCT.TransformIndexToPhysicalPoint((0, 0, i))) #image eller image2+
    ds.ImagePositionPatient = position
  
    out_path = os.path.join(output, f"slice_{i:04d}.dcm")
    ds.save_as(out_path)
