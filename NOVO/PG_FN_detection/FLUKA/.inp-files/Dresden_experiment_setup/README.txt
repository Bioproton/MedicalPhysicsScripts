- OncoRay51_model.inp
    FLUKA input file for the NOVO000051 Dresden experiment setup

- Lattice51.inp
    FLUKA input file for the NOVO000051 Dresden experiment setup
    Includes three LATTICE copies, resulting in a quadruple detector setup

- PTB_model_creator.ipynb
    Example notebook for running OncoRay_model_creator.py
    Creates .inp file(s) with user-defined names and shifts
    Mainly used to automate manual changes in similar .inp files

- OncoRay_model_creator.py
    Master script that creates .inp file(s) with the 12-bar Dresden NOVCoDA model
    Uses data from the Excel file OncoRay_model_FLUKA_coordinates, 
    and the script NOVO_to_FLUKA_coordinates
    The PMMA target is included

- NOVO_to_FLUKA_coordinates.py
    Translates between "NOVO coordinates" (the model's own coordinate system) 
    and "FLUKA coordinates" (coordinates after shifts, rotations and positioning)

- OncoRay_model_FLUKA_coordinates.xlsx
    Includes measurements how the bars were positioned in the Dresden 12-2025 experiments
    Also includes a lot of parameters to model the additional components around/next to
    the scintillator bars (readout electronics, support bars, PMTs)

