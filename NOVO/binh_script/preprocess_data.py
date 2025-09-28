import torch 
import nifti_dicom_2_tensor as nd2t
import torchio as tio

binary_mask = "AlignedBinary_mask_hv14.nii.gz"

binary_mask_tensor = nd2t.nifti_to_tensor(binary_mask)


def mask_FN_PG_dose(tensor, binary_mask = binary_mask): 
    """
    Masks PG and FN production outside the patient

    Args: 
    - tensor (tensor): Aligned PD, PG or FN tensor
    - binary_mask (tensor): tensor used to mask out production outside the patient

    Returns:
    - FN/PG only inside the patient
    """

    binary_mask_tensor = nd2t.nifti_to_tensor(binary_mask)

    masked_tensor = torch.mul(tensor,binary_mask_tensor)

    return masked_tensor


