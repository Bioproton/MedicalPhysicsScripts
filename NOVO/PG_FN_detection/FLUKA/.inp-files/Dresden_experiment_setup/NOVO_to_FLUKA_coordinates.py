# Script to translate NOVO detector coordinates into FLUKA coordinates
# Also allows the reverse coordinate transfer

import numpy as np
import math

# NEW VERSION
def NOVO_to_FLUKA_coordinate_transform(coordinates, trans1=np.array([0.0, 0.0, -10.6]), rot=np.array([90.0, 90.0, 90.0]), trans2=np.array([20.0, 0.0, 64.2]), reverse=False):
    '''
    Coordinate transform between NOVO (before rotations) and FLUKA coordinates (after rotations)
    Defaults made for OncoRay NOVCoDA setup
    coordinates: 
        Coordinates that are to be transformed
        Format: np.array([[x1, y1, z1], [x2, y2, z2], [z3, y3, z3]...])
    trans1: 
        First shift performed in the FLUKA .inp file (NOVO_rot)
        Format: np.array([X1, Y1, Z1])
    rot: 
        Rotation values from FLUKA .inp file   (NOVO_rot)
        Format: np.array([rot1, rot2, rot3])
    trans2: 
        Format: np.array([X2, Y2, Z2])
    reverse:
        True: Going from FLUKA coordinates to NOVO coordinates
        False: Going from NOVO coordinates to FLUKA coordinates
    '''

    # New coordinates
    XYZ = np.array([])

    # General formula:
    #   u' = CBA(u + v+ t)          # From definition coordinate system to new coordinate system
    # Reverse:
    #   u = [CBA^-1]u' - (v + t)    # From new coordinate system to definition coordinate system
    #   CBA^-1 = CBA^T because CBA is orthogonal

    v = trans1
    t = trans2

        # Calculating the transformation matrix
    A = np.array([
        [round(math.cos(math.radians(rot[0])), 5), round(math.sin(math.radians(rot[0])), 5), 0], 
        [round(-math.sin(math.radians(rot[0])), 5), round(math.cos(math.radians(rot[0])), 5), 0],
        [0, 0, 1]
    ])

    B = np.array([
        [1, 0, 0],
        [0, round(math.cos(math.radians(rot[1])), 5), round(math.sin(math.radians(rot[1])), 5)],
        [0, round(-math.sin(math.radians(rot[1])), 5), round(math.cos(math.radians(rot[1])), 5)]
    ])

    C = np.array([
        [round(math.cos(math.radians(rot[2])), 5), round(math.sin(math.radians(rot[2])), 5), 0],
        [round(-math.sin(math.radians(rot[2])), 5), round(math.cos(math.radians(rot[2])), 5), 0],
        [0, 0, 1]
    ])

    # If going from FLUKA coordinates to NOVO coordinates
    if reverse:

        # Due to orthogonality, taking the transpose of the transformation matrix is the same as the inverse
        CBA_T = np.transpose(np.matmul(np.matmul(C, B), A))

        # u = [CBA^-1]u' - (v + t)  [Transpose = inverse because of orthogonality]
        XYZ = np.matmul(coordinates, CBA_T) - (v + t)

    # If going from NOVO coordinates to FLUKA coordinates
    else:
        # Calculating the final CBA matrix
        CBA = np.matmul(np.matmul(C, B), A)

        # u' = CBA(u + v+ t)
        XYZ = np.matmul(coordinates + v + t, CBA)

    return XYZ

if __name__ == "__main__":

    # Coordinates from OncoRay NOVCoDA model (From FLUKA to NOVCoDA coordinates)
    u = np.array([
        [54.11309,  -2.18555,  22.61021],
        [53.95603,   2.00732,  22.3055],
        [65.35424,  -9.10020,  18.90049],
        [66.39774,  -3.74756,  23.91974],
        [73.54038,  -6.43782,  11.23986],
        [53.26059,  -1.84583,  24.59148],
        [53.27093,  -1.80405,  24.78111]
    ])

    uu = NOVO_to_FLUKA_coordinate_transform(u, reverse=True)
    print(uu)