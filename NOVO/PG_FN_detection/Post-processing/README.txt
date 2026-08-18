Scripts for post-processing FLUKA output using mgdraw

- mgdraw_output_reader_NOVO_v04.py
    Main post-processing script
    Performs the following:
        .load_data()
            - Reads scintillator_interactions.txt-files from a given folder
            - Optional: Translates coordinates from FLUKA coordinates to OncoRay measurement coordinates
        .filter_hits()
            - Filters away hits not used
            - Filters away cross scatter hits arising from LATTICE detector copies
            - Merges hits occuring in quick succession in 
              the same scintillator bar (of the same NCASE)
            - Merges hits occuring in quick succession in
              the same scintillator bar (of different NCASES)
            - Optional: Rescales time stamps to a given beam current / beam structure 
            - Optional: outputs gamma_hits.txt, neutron_hits.txt and all_hits.txt files
        .event_builder()
            - Builds coincidence events (triple gamma-ray, double neutron)
            - Optional: outputs .inp files for ngimager (backprojection imaging code)


- mgdraw_v05_output_reader.py -> Obsolete!
    Reads scintillator_interaction files from mgdraw version 6


- mgdraw_txt_file_reader_06.py
    Reads scintillator_interaction files from mgdraw version 6, 8 and 9


- time_converter_NOVO.py
    Rescales FLUKA times to mimic a beam current structure
    Used in conjunction with ...NOVO_v03.py


- hit_txt_file_reader_v01.py
    Reads and stores pre-post-processed hit data (gamma_hits.txt or neutron_hits.txt)
    Saves a lot of time by bypassing the whole 
    hit filtering process after readering scintillator_interactions.txt files
    Pre-post-processing will have to be performed in advance of using this script
    Any event data will have to go through either:
        - The original ...NOVO_v03.py-script
        - A copy of the event building part of the ...NOVO_v03.py-script
