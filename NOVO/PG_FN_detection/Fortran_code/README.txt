Contains Fortran scripts to be used in FLUKA

mgdraw_v04_only_bxdraw.f
  Fortran scipt with the mgdraw subroutine that writes two outputs: 
    - at events where a neutron or a photon enters one of the scintillators -> ****_scintillator_regions.txt
      -> Compatible with bxdraw_txt_file_reader.py, mgdraw_output_merger_v2.py and mgdraw_bxdraw_plotter.py
    - at events where a neutron or a photon exits the target -> ****parts_leaving_target.txt
