Contains Fortran scripts to be used in FLUKA
Last update 08.07.2025:
Uploaded files

mgdraw_v04_only_bxdraw.f
  Fortran scipt for FLUKA with the mgdraw subroutine that writes two outputs: 
    - at events where a neutron or a photon enters one of the scintillators -> ****_scintillator_regions.txt
      -> Compatible with bxdraw_txt_file_reader.py, mgdraw_output_merger_v2.py and mgdraw_bxdraw_plotter.py
    - at events where a neutron or a photon exits the target -> ****parts_leaving_target.txt

mgdraw_v03_detection.f
  Incomplete and currently deprecated Fortran scipt for FLUKA with the mgdraw subroutine that writes three outputs for detection purposes:
    - UNIT=67: ****_flagged_pgs_fns.txt: Output on all FNs and PGs that are produced in the target
      -> Used as an information baseline to compare against what is detected
    - UNIT=80: ****_FN_PG_detected.txt: Output on all flagged FNs/PGs that interact in any scintillator element
      -> ANY interaction will trigger an output, even irrelevant ones
    - UNIT=81: ****_non_FN_PG_detected.txt: Output on all flagged non-Fns/PGs that interact in any scintillator element
      -> ANY interaction will trigger an output, even irrelevant ones
    A particle will be flagged as a true FN/PG if:
      FN: Particle is a neutron, it was produced by a proton (1) by ICODE=101 inside the target (MREG==49)
      PG: Particle is a photon, it was produced by a proton (1) or a heavy ion (-2) in by ICODE=101 or ICODE=106 inside the target (MREG==49)
    If a FN/PG interacts in the target after production, or if it enters any electronic box, it is flagged as a non-FN/PG

mgdraw_v05_detection.f
  Fortran scipt for FLUKA with the mgdraw subroutine that will record all interactions that happenes within the NOVCoDA detector scintillators.
  Prompt gammas and fast neutrons that are produced in the target (MREG 49), and in addition travel directly to the scintillators and interact will be flagged LLOUSE=1
  Outputs:
    - UNIT=80: ****_scintillator_interactions.txt: All interactions in the scintillators (defined as MREG regions 1-48) are recorded
  
