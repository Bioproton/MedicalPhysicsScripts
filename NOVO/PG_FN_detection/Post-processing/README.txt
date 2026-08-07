Scripts for post-processing FLUKA output using mgdraw

- mgdraw_output_reader_NOVO_v03.py
    Main post-processing script
    Performs the following:
        [.load_data()]
            - Reads scintillator_interactions.txt-files from a given folder
        [.filter_hits()]
            - Filters away hits not used
            - Merges hits occuring in quick succession in 
              the same scintillator bar
            - Optional: outputs gamma_hits.txt, neutron_hits.txt and all_hits.txt files
        [.event_builder()]
            - Builds coincidence events (triple gamma-ray, double neutron)
            - Optional: outputs .inp files for ngimager (backprojection imaging code)

    Input required:

        Initialization: DetectionDataStorage(...)
            - folder_path: Path to FLUKA output data
            - primaries_per_spawn: Primaries per spawn (i.e. per output file)
            - max_files: Maximum files to read
            - detector: Not used

        Data loading: .load_data(...)
            - mgdraw_verion_8_plus: Was mgdraw versions 8+ used?
                mgdraw_v06: 18 outputs -> mgdraw_v05_output_reader.py
                mgdraw_v08+: 19 outputs -> mgdraw_txt_file_reader_06.py

        Hit filering: .filter_hits(...)
            - time_structure: Rescales times {"pulsed", "continuous", None}
            - beam current: beam current to be replicated [nA]
            - write_hits_to_file: True/False -> Creates gamma_hits.txt/neutron_hits.txt
        
        Event building: .event_builder(...)
            - write_ngimager_file: True/False -> Creates input files for ngimager

- mgdraw_v05_output_reader.py


- mgdraw_txt_file_reader_06.py


- time_converter_NOVO.py


- hit_txt_file_reader_v01.py
    Reads and stores pre-post-processed hit data (gamma_hits.txt or neutron_hits.txt)
    Saves a lot of time by bypassing the whole 
    hit filtering process after readering scintillator_interactions.txt files
    Pre-post-processing will have to be performed in advance of using this script
    Any event data will have to go through either:
        - The original ...NOVO_v03.py-script
        - A copy of the event building part of the ...NOVO_v03.py-script