""""
Script with Class with capabilities to process data from NOVCoDA detector simulations
"""
import numpy as np
import time
import os
import csv
import math
import pandas as pd


#PATH = "\\klient.uib.no\FELLES\LAB-IT\IFT\Medisinskfysikk\Sander\Studie 1\Anon_Brain_01\FLUKA_Hv_14_2fields_90grad_1\270_degree\Results_spot_1\scintillator_interactions"
PATH = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\Studie 1\Pasienter\Anon_Brain_01\270_degrees\Results_spot_1\scintillator_interactions"
#PATH = "s"

class DetectionDataStorage:
    """
    Class to store and process data from NOVCoDA detector simulations
    """

    def __init__(
            self, 
            folder_path: str, 
            primaries_per_spawn: int = 10000000, 
            max_files: int = 100
        ) -> None:

        self.folder_path = folder_path.replace("\\", "/")
        #self.folder_path = folder_path
        self.primaries_per_spawn = primaries_per_spawn
        self.max_files  = max_files
        self.feature_names = np.array([
            "ncase", "icode", "particle_in", "particle_out", "fnpg_flag",
            "targetZ", "targetA", "energy_out", "energy_in",
            "crash_x", "crash_y", "crash_z", "region", "particle_generation",
            "particle_age", "source_x", "source_y", "source_z"
            ])
        
        # List variable to store all entries from the N number of "scintillator_interaction.txt"-files
        self.data = []

        # List variable that will contain the list entries of the interactions we want (219/221 for gamma, and (n,p) for neutron)
        # The physical events are not reconstructed, but have only been filtered out.
        self.single_gamma_events = []
        self.neutron_events = []

        # List-tuple variable to store NCASEs for situations where gamma chains are =3 and neutron chains =2
        # Entries will be on the form [(NCASE_1, LLOUSE_1, regions_1, edeps_1), ...], i.e. [(23421, 1, [4, 7], [0.020, 0.015]]
        # Events are therefore reconstructed
        self.double_neutron_chains = []
        self.triple_gamma_chains = []

        self.double_neutron_events = []
        self.triple_gamma_events = []
        self.double_gamma_events = []

        self.detectable_double_neutron_events = []
        self.detectable_triple_gamma_events = []

        self.detectable_single_gamma_events = []
        self.detectable_double_gamma_events = []


    def load_data(self, supress_messages=True) -> None:

        from mgdraw_v05_output_reader import collect_txt_data
        folder = os.listdir(self.folder_path)
        n_files = len(os.listdir(self.folder_path))
        m = 0   # File counter
        n = 0   # Line counter

        time_stamp = time.time()

        print(f"Reading {n_files} scintillator_interactions.txt-files")

        for filename in folder:
            
            # Skip any other files
            if "scintillator_interactions.txt" not in filename:
                break

            m += 1  # Incement file counter
            if m > self.max_files:
                print(f"Max files reached: {m - 1}/{self.max_files}, stopping data collection")
                break
            data_entry = collect_txt_data(self.folder_path + "\\" + filename, primaries_per_spawn=self.primaries_per_spawn , spawn_number=m) # Shape [eg. (3000, 1), ..., (3000, 1)]
            self.data.append(data_entry)

        self.data = np.concatenate(self.data, axis=1)
        
        print(f"Total time used on data collection: {round(time.time() - time_stamp,2)} s")

    def interaction_frequency(self):
        """
        Function that writes how many times each ICODE occurred in the detector elements
        """

        unique_icode, counts = np.unique(self.data[1,:], return_counts=True)
        
        sorted_indicies = np.argsort(-counts)
        for i in sorted_indicies:
            print(f"Interaction {unique_icode[i]} happened {counts[i]} times")

    def event_builder(self, print_results=True):
        '''
        Function filters out the physics interactions used in FN/PG-detection.
        For PG:
            219: Compton
            221: Photoelectric absorption
        For FN: (n, p)-interactions with ICODEs:
            100: Elastic collisions with hadrons
            300: Elastic collisions with low energy neutrons

        Coincidences are also found and reported if print_results=True
        '''
        # Class used for storing events
        class InteractionEvent():

            def __init__(self, crash_x, crash_y, crash_z, source_x, source_y, source_z, 
                        energy_out, energy_in, particle_age, particle_generation,
                        targetA, targetZ, icode, fnpg_flag, ncase, region, chain):

                self.crash_x = crash_x
                self.crash_y = crash_y
                self.crash_z = crash_z

                self.source_x = source_x
                self.source_y = source_y
                self.source_z = source_z
                
                self.energy_in = energy_in
                self.energy_out = energy_out
                self.particle_age = particle_age

                self.ncase = ncase
                self.targetA = targetA
                self.targetZ = targetZ
                self.icode = icode

                self.particle_generation = particle_generation
                self.fnpg_flag = fnpg_flag
                self.region = region
                self.chain = chain

        # Time recorder
        time_stamp = time.time()
        print(f"\n-----------EVENT BUILDING-----------")

        #-----------------------------EVENT BUILDING-------------------------------------


        # Collecting all the data and storing them in more descriptive variables
        ncases, icodes, particles_in, particles_out, fnpg_flags, targetZs, \
        targetAs, energies_out, energies_in, crash_xs, crash_ys, crash_zs, \
        regions, particles_gen, particles_age, source_xs, source_ys, source_zs = self.data

        # Flag to indicate how many events are related to the "same" gamma/neutron
        gamma_chain = 0
        neutron_chain = 0

        # Particle origin identification: The source coordinates
        particle_id = [source_xs[0], source_ys[0], source_zs[0]]

        # Variables to store previous gamma/neutron energies for chain logic checks
        previous_gamma_energy = 0.0
        previous_neutron_energy = 0.0

        # List variable to store interaction region (MREG) for gamma and neutron chains
        gamma_chain_regions = []
        neutron_chain_regions = []

        # List variables to store energy depositions for gamma and neutron chains
        gamma_chain_edeps = []
        neutron_chain_edeps = []

        # List variable to store NCASEs for irregular gamma and neutron chains for potential investigation
        irregular_gammas = []
        irregular_neutrons = []

        # Looping over all entries
        for index, icode in enumerate(icodes):

            icode = int(icode)

            if particle_id != [source_xs[index], source_ys[index], source_zs[index]]:
                # If there is a new particle origin, then a new event chain is initiated
                gamma_chain = 0
                neutron_chain = 0
                particle_id = [source_xs[index], source_ys[index], source_zs[index]]


            '''---------------GAMMAS---------------'''
            # Compton interaction (219) will always have two list entries: on each for the outgoing photon and electron
            if icode == 219:
                if particles_out[index] == 3:
                    # The compton electron is not interesting, so it is skipped
                    continue

                elif particles_out[index] == 7:

                    if gamma_chain > 0 and previous_gamma_energy != energies_in[index]:
                        # The chain is irregular and might need supervision
                        # Chain is reset
                        gamma_chain = 0
                        gamma_chain_regions = []
                        gamma_chain_edeps = []
                        irregular_gammas.append(ncases[index])

                    # Updating gamma chain
                    gamma_chain += 1

                    # Updating what scintillator/region the gamma interacted in
                    gamma_chain_regions.append(regions[index])

                    # Updating how much energy the interaction deposited
                    gamma_chain_edeps.append(round(energies_in[index] - energies_out[index], 6))

                    # Updating the previous_gamma_energy value
                    previous_gamma_energy = energies_out[index]

                    # Adding the gamma Event to the gamma events list
                    self.single_gamma_events.append(
                        InteractionEvent(
                            crash_xs[index], crash_ys[index], crash_zs[index], \
                            source_xs[index], source_ys[index], source_zs[index], \
                            energies_out[index], energies_in[index], particles_age[index], \
                            particles_gen[index], targetAs[index], targetZs[index], \
                            icode, fnpg_flags[index], ncases[index], regions[index], gamma_chain)
                            )
                    
                    if gamma_chain == 2:
                        self.double_gamma_events.append(self.single_gamma_events[-2])
                        self.double_gamma_events.append(self.single_gamma_events[-1])
                    
                    if gamma_chain == 3:
                        # If a triple gamma chain is found, append the NCASE and the FN/PG flag
                        # Chains with values 3+ (4, 5, 6, ...) are not appended to avoid double counting
                        self.triple_gamma_chains.append((ncases[index], fnpg_flags[index], gamma_chain_regions, gamma_chain_edeps))

                        self.triple_gamma_events.append(self.single_gamma_events[-3])
                        self.triple_gamma_events.append(self.single_gamma_events[-2])
                        self.triple_gamma_events.append(self.single_gamma_events[-1])


                else:
                    assert 1==0, f"Non gamma/electron found in a Compton scatter: {particles_out[index]}" + \
                        f" found in NCASE {ncases[index]}"
                    
            #   221 events will alwyas have a single list entry
            elif icode == 221:
                # Photoelectric absorption events are generally the end of the chain
                gamma_chain += 1
                gamma_chain_regions.append(regions[index])
                gamma_chain_edeps.append(energies_out[index])

                self.single_gamma_events.append(
                    InteractionEvent(
                        crash_xs[index], crash_ys[index], crash_zs[index], \
                        source_xs[index], source_ys[index], source_zs[index], \
                        energies_out[index], energies_in[index], particles_age[index], \
                        particles_gen[index], targetAs[index], targetZs[index], \
                        icode, fnpg_flags[index], ncases[index], regions[index], gamma_chain)
                        )
                
                if gamma_chain == 2:
                    self.double_gamma_events.append(self.single_gamma_events[-2])
                    self.double_gamma_events.append(self.single_gamma_events[-1])
                
                if gamma_chain == 3:
                    # If a triple gamma chain is found, append the NCASE and the FN/PG flag
                    # Chains with values 3+ (4, 5, 6, ...) are not appended to avoid double counting
                    self.triple_gamma_chains.append((ncases[index], fnpg_flags[index], gamma_chain_regions, gamma_chain_edeps))

                    self.triple_gamma_events.append(self.single_gamma_events[-3])
                    self.triple_gamma_events.append(self.single_gamma_events[-2])
                    self.triple_gamma_events.append(self.single_gamma_events[-1])

                '''---------------NEUTRONS---------------'''
            elif icode == 100 and particles_in[index] == 8 and \
                    targetAs[index] == 1 and targetZs[index] == 1:
                
                # Elastic 100 -interactions with (n, p) has two entries. The proton one is skipped
                if particles_out[index] == 1:
                    # Skipping proton entry
                    continue

                elif particles_out[index] == 8:

                    if neutron_chain > 0 and previous_neutron_energy != energies_in[index]:
                        # The neutron chain is irregular and might need supervision
                        # Chain is reset
                        neutron_chain = 0
                        neutron_chain_regions = []
                        neutron_chain_edeps = []
                        irregular_neutrons.append(ncases[index])
                    
                    # Updating neutron chain
                    neutron_chain += 1

                    # Updating previous neutron energy values
                    previous_neutron_energy = energies_out[index]

                    # Updating what scintillator the neutron interacted in
                    neutron_chain_regions.append(regions[index])

                    # Updating how much energy was deposited in the interaction
                    neutron_chain_edeps.append(round(energies_in[index] - energies_out[index], 6))

                    # Adding the current event to the neutron event dictionary
                    self.neutron_events.append(
                        InteractionEvent(
                            crash_xs[index], crash_ys[index], crash_zs[index], \
                            source_xs[index], source_ys[index], source_zs[index], \
                            energies_out[index], energies_in[index], particles_age[index], \
                            particles_gen[index], targetAs[index], targetZs[index], \
                            icode, fnpg_flags[index], ncases[index], regions[index], neutron_chain)
                            )
                    if neutron_chain == 2:
                        # If a double (n, p) chain is found, append the NCASE and the FN/PG flag
                        # Chains with values 2+ (3, 4, 5, ...) are not appended to avoid double counting
                        self.double_neutron_chains.append((ncases[index], 
                                                    fnpg_flags[index -2] + fnpg_flags[index], 
                                                    neutron_chain_regions, neutron_chain_edeps))
                        
                        self.double_neutron_events.append(self.neutron_events[-2])
                        self.double_neutron_events.append(self.neutron_events[-1])

                else:
                    assert 1==0, f"Non neutron/proton found in a (n,p)-scatter: {particles_out[index]}" + \
                    f" found in NCASE {ncases[index]}"

            # If an elastic (n, p) interaction occurs with ICODE 300, then the proton is listed before the neutron.
            # This is a rather long statement 
            elif targetAs[index] == 1 and targetZs[index] == 1 and\
                    particles_in[index] == 8 and icode == 300:
                
                # If the interaction secondary is a proton, then the next in the (n, p)-interaction should be a neutron
                if particles_out[index] == 1:
                    continue

                # If we have a neutron now and had a proton previously, then we have a legit (n, p)-interaction
                if particles_out[index] == 8 and particles_out[index - 1] == 1:

                    if neutron_chain > 0:
                        if previous_neutron_energy != energies_in[index]:
                            # Irregular neutron chain found
                            # Neutron chain is reset
                            neutron_chain = 0
                            neutron_chain_regions = []
                            neutron_chain_edeps = []
                            irregular_neutrons.append(ncases)

                    # Updating neutron chain
                    neutron_chain += 1

                    # Updating previous neutron energy value
                    previous_neutron_energy = energies_out[index]

                    # Updating in what region/scintillator the neutron interacted in
                    neutron_chain_regions.append(regions[index])

                    # Updating how much energy was deposited in the interaction
                    neutron_chain_edeps.append(round(energies_in[index] - energies_out[index], 6))

                    # Adding the current event to the neutron event dictionary
                    self.neutron_events.append(
                        InteractionEvent(
                            crash_xs[index], crash_ys[index], crash_zs[index], \
                            source_xs[index], source_ys[index], source_zs[index], \
                            energies_out[index], energies_in[index], particles_age[index], \
                            particles_gen[index], targetAs[index], targetZs[index], \
                            icode, fnpg_flags[index], ncases[index], regions[index], neutron_chain)
                            )
                    # If a double (n, p) chain is found, append the NCASE and the FN/PG flag
                    # Chains with values 2+ (3, 4, 5, ...) are not appended to avoid double counting              
                    if neutron_chain == 2:
                        self.double_neutron_chains.append((ncases[index], fnpg_flags[index -2] + fnpg_flags[index], 
                                                    neutron_chain_regions, neutron_chain_edeps))
                        
                        self.double_neutron_events.append(self.neutron_events[-2])
                        self.double_neutron_events.append(self.neutron_events[-1])

            # If the ICODE is not (219), (225), (ICODE 100 with target A, Z = 1, 1) or (ICODE 300 with A, Z = 1, 1, secondaries=1, 8, incoming=8), then the chain is reset
            else:
                gamma_chain = 0
                neutron_chain = 0

                gamma_chain_regions = []
                neutron_chain_regions = []

                gamma_chain_edeps = []
                neutron_chain_edeps = []
        
        if len(irregular_gammas) > 0:
            print(f"Irregular gamma chains found: {len(irregular_gammas)} / {len(self.single_gamma_events)}")
        if len(irregular_neutrons) > 0:
            print(f"Irregular neutron chains found: {len(irregular_neutrons)} / {len(self.neutron_events)}")
        

        # DETECTABILITY TESTING
        # For single gamma events [NB!: Does not check for hits occuring in the same bar immedietely after one another! Does not represent true detectability]
        for index in range(len(self.single_gamma_events)):
            dE = round(self.single_gamma_events[index].energy_in - self.single_gamma_events[index].energy_out, 6)
            if dE < 0.010:  # Less than 10 keV
                continue
            self.detectable_single_gamma_events.append(self.single_gamma_events[index])


        # For double gamma events
        for index in range(len(self.double_gamma_events)):
            if self.double_gamma_events[index].chain != 2:
                continue

            region1 = self.double_gamma_events[index - 1].region
            region2 = self.double_gamma_events[index - 0].region

            if len(np.unique([region1, region2])) < 2:
                continue

            dE1 = round(self.double_gamma_events[index - 1].energy_in - self.double_gamma_events[index - 1].energy_out, 6)
            dE2 = round(self.double_gamma_events[index - 0].energy_in - self.double_gamma_events[index - 0].energy_out, 6)

            if dE1 < 0.010 or dE2 < 0.010:
                continue

            self.detectable_double_gamma_events.append(self.double_gamma_events[index - 1])
            self.detectable_double_gamma_events.append(self.double_gamma_events[index - 0])

        # For triple gamma events
        for index in range(len(self.triple_gamma_events)):
            if self.triple_gamma_events[index].chain != 3:
                continue

            # Checking if the three interactions happened in three unique scintillators
            region1 = self.triple_gamma_events[index - 2].region
            region2 = self.triple_gamma_events[index - 1].region
            region3 = self.triple_gamma_events[index - 0].region

            # If the three interactions do not happen in three unique scintillators, skip this entry
            if len(np.unique([region1, region2, region3])) < 3:
                continue

            # Energy depositions
            dE1 = round(self.triple_gamma_events[index - 2].energy_in - self.triple_gamma_events[index - 2].energy_out, 6)  # First hit
            dE2 = round(self.triple_gamma_events[index - 1].energy_in - self.triple_gamma_events[index - 1].energy_out, 6)  # Second hit
            dE3 = round(self.triple_gamma_events[index - 0].energy_in - self.triple_gamma_events[index - 0].energy_out, 6)  # Third hit

            # If energy depositions are too low, then they will not be detected in the detector and they are therefore skipped
            if dE1 < 0.010 or dE2 < 0.010 or dE3 < 0.010:
                continue

            # This event has passed the detectability tests and is good to go
            self.detectable_triple_gamma_events.append(self.triple_gamma_events[index - 2]) # First hit
            self.detectable_triple_gamma_events.append(self.triple_gamma_events[index - 1]) # Second hit
            self.detectable_triple_gamma_events.append(self.triple_gamma_events[index - 0]) # Third hit

        # For neutron events
        for index in range(len(self.double_neutron_events)):
                
                if self.double_neutron_events[index].chain != 2:
                    continue

                # Checking if the three interactions happened in three unique scintillators
                region1 = self.double_neutron_events[index - 1].region
                region2 = self.double_neutron_events[index - 0].region

                # If the three interactions do not happen in three unique scintillators, skip this entry
                if len(np.unique([region1, region2])) < 2:
                    continue

                # Energy depositions
                dE1 = round(self.double_neutron_events[index - 1].energy_in - self.double_neutron_events[index - 1].energy_out, 6)  # First hit
                dE2 = round(self.double_neutron_events[index - 0].energy_in - self.double_neutron_events[index - 0].energy_out, 6)  # Second hit

                # If energy depositions are too low (200 keV), then they will not be detected in the detector and they are therefore skipped
                if dE1 < 0.200 or dE2 < 0.200:
                    continue
            
                # This event has passed the detectability tests and is good to go
                self.detectable_double_neutron_events.append(self.double_neutron_events[index - 1]) # First hit
                self.detectable_double_neutron_events.append(self.double_neutron_events[index - 0]) # Second hit

        print(f"Event building complete, time used: {round(time.time() - time_stamp, 2)} s")

        '''---------------RESULTS---------------'''

    def event_summary(self):
            '''Summarizes the gamma and neutron events
            '''
            # Gamma events
            N_direct = 0
            for index in range(len(self.detectable_triple_gamma_events)):
                if self.detectable_triple_gamma_events[index].chain != 3:
                    continue

                # Check if PG comes directly from production to detection
                flag1 = self.detectable_triple_gamma_events[index - 2].fnpg_flag   # First hit
                flag2 = self.detectable_triple_gamma_events[index - 1].fnpg_flag   # Second hit
                flag3 = self.detectable_triple_gamma_events[index - 0].fnpg_flag   # Third hit

                if flag1 + flag2 + flag3 == 3:  # All flags must be 1
                    N_direct += 1

            print("\n----------RESULTS----------")
            print(f"Total gamma event secondaries: {len(self.single_gamma_events)}")
            print(f"Triple gamma events: {int(len(self.triple_gamma_events) / 3)}")
            print(f"Triple gamma events, detectable: {int(len(self.detectable_triple_gamma_events) / 3)}")
            print(f"Triple gamma events, detectable and direct: {N_direct}")
            
            # Neutron events
            
            N_direct = 0
            # Sorting through all events
            for index in range(len(self.detectable_double_neutron_events)):
                if self.detectable_double_neutron_events[index].chain != 2:
                    continue

                # Check if PG comes directly from production to detection
                flag1 = self.detectable_double_neutron_events[index - 1].fnpg_flag   # First hit
                flag2 = self.detectable_double_neutron_events[index - 0].fnpg_flag   # Second hit

                if flag1 + flag2 == 2:  # All flags must be 1
                    N_direct += 1


            print(f"\nTotal neutron event secondaries: {len(self.neutron_events)}")
            print(f"Double neutron events: {int(len(self.double_neutron_events) / 2)}")
            print(f"Double neutron events, detectable: {int(len(self.detectable_double_neutron_events) / 2)}")
            print(f"Double neutron events, detectable and direct: {N_direct}")


    def mgdraw_to_csv_builder(self, all_events=False) -> None:
        '''
        Function that uses the functions event_builder and collect_txt_data to
        create .csv-files with a list mode of all the relevant gamma and neutron
        interactions in the detector. 

        all_events decides if all gamma/neutron events (i.e. double gamma, quintuple neutron) is to be included, or if it is only the triple gamma/double neutron events

        NB: The csv-files should include in what region the event happened in,
        as the coincidence interactions should happen in different regions(scintillators)
        '''

        csv_gamma_file = self.folder_path + "/events_gammas.csv"
        csv_neutron_file = self.folder_path + "/events_neutrons.csv"

        if all_events == True:
            GammaEventList = self.single_gamma_events
            NeutronEventList = self.neutron_events
        else:
            GammaEventList = self.triple_gamma_events
            NeutronEventList = self.double_neutron_events

        # Writing gamma file
        with open(csv_gamma_file, "w", newline="") as burner_file:
            csv_file_writer = csv.writer(burner_file)
            csv_file_writer.writerow([
                "x", "y", "z", "sourceX", "sourceY", "sourceZ", "PDG", 
                "edepMeV", "trackLocalTime", "trackID", "parentID", "eventID", 
                "targetA", "targetZ", "processName"
            ])
            for Event in GammaEventList:
                csv_file_writer.writerow([
                    Event.crash_x, Event.crash_y, Event.crash_z, 
                    Event.source_x, Event.source_y, Event.source_z,
                    22, round(Event.energy_in - Event.energy_out, 5), 
                    round(Event.particle_age * 1e3, 5),     # Time is then given in nanoseconds
                    Event.particle_generation - 1, Event.particle_generation - 2, 
                    Event.ncase, Event.targetA, Event.targetZ, "compt"
                ])
        burner_file.close()

        # Writing neutron file
        with open(csv_neutron_file, "w", newline="") as burner_file:
            csv_file_writer = csv.writer(burner_file)
            csv_file_writer.writerow([
                "x", "y", "z", "sourceX", "sourceY", "sourceZ", "PDG", 
                "edepMeV", "trackLocalTime", "trackID", "parentID", "eventID", 
                "targetA", "targetZ", "processName"
            ])
            for Event in NeutronEventList:
                csv_file_writer.writerow([
                    Event.crash_x, Event.crash_y, Event.crash_z, 
                    Event.source_x, Event.source_y, Event.source_z,
                    2112, round(Event.energy_in - Event.energy_out, 5), 
                    round(Event.particle_age * 1e3, 5),     # Time is then given in nanoseconds
                    Event.particle_generation - 1, Event.particle_generation - 2, 
                    Event.ncase, Event.targetA, Event.targetZ, "hadElastic"
                ])
        burner_file.close()

        print(f".csv files created: \n {csv_gamma_file} \n {csv_neutron_file}")

    def calculate_cone_params(self) -> None:

        time_stamp = time.time()

        # Lists to store cone parameters for 1) Data exploration, 2) Event indicies for event exploration, 3) Export to csv for simple backprojection
        self.gamma_cone_params = []
        self.gamma_cone_event_indicies = []
        self.csv_gamma_cone_params = []

        # Lists to store cone parameters for 1) Data exploration, 2) Event indicies for event exploration, 3) Export to csv for simple backprojection
        self.neutron_cone_params = []
        self.neutron_cone_event_indicies = []
        self.csv_neutron_cone_params = []
        
        # Prerequisite: event_builder() must have been used before calculate_cone_params()
        if len(self.detectable_triple_gamma_events) == 0:
            print(f"Prereqiusite not met: Events have not been reconstructed. Performing event construction...")
            self.event_builder()
        
        # Defining physical constants
        c = 3.00 * 1e8 # [m/s] speed of light in vaccuum (used as c=1 when it is practical)
        m_e = 0.510999 # [MeV/c^2], rest mass of an electron, from NIST: https://physics.nist.gov/cgi-bin/cuu/Value?mec2mev
        m_n = 939.565 # [MeV/c^2], rest mass of a neutron, from NIST: https://physics.nist.gov/cgi-bin/cuu/Value?mnc2mev
        
        reconstruction_fails = np.array([0, 0])
        # Calculating gamma cones
        for index in range(len(self.detectable_triple_gamma_events)):

            # Skip all entries where the chain is not 3
            if self.detectable_triple_gamma_events[index].chain != 3:
                continue

            # Saving which scintillator the interaction happened in
            region1 = self.detectable_triple_gamma_events[index - 2].region
            region2 = self.detectable_triple_gamma_events[index - 1].region
            region3 = self.detectable_triple_gamma_events[index - 0].region

            # Saving interaction code and source coordinates
            ncase = self.detectable_triple_gamma_events[index].ncase
            sourceX = self.detectable_triple_gamma_events[index].source_x
            sourceY = self.detectable_triple_gamma_events[index].source_y
            sourceZ = self.detectable_triple_gamma_events[index].source_z

            # Scintillator hits (first, second and third hit)
            s1 = np.array([self.detectable_triple_gamma_events[index - 2].crash_x, self.detectable_triple_gamma_events[index - 2].crash_y, self.detectable_triple_gamma_events[index - 2].crash_z])  # First hist
            s2 = np.array([self.detectable_triple_gamma_events[index - 1].crash_x, self.detectable_triple_gamma_events[index - 1].crash_y, self.detectable_triple_gamma_events[index - 1].crash_z])  # Second hit
            s3 = np.array([self.detectable_triple_gamma_events[index - 0].crash_x, self.detectable_triple_gamma_events[index - 0].crash_y, self.detectable_triple_gamma_events[index - 0].crash_z])  # Third hit

            # Energy depositions
            dE1 = round(self.detectable_triple_gamma_events[index - 2].energy_in - self.detectable_triple_gamma_events[index - 2].energy_out, 6)  # First hit
            dE2 = round(self.detectable_triple_gamma_events[index - 1].energy_in - self.detectable_triple_gamma_events[index - 1].energy_out, 6)  # Second hit

            # Calculating distance vectors between hits
            d12 = s1 - s2   # Distance vector between hit 1 and 2
            d23 = s2 - s3   # Distance vector between hit 2 and 3

            # Calculating theta2 from d12, d23 (Formula 3.4 in Setterdahl 2025)
            theta2 = np.arccos(np.matmul(d12, d23) / (np.linalg.norm(d12) * np.linalg.norm(d23)))   # Units in radians

            # Calculating E1 from thetha2 and dE2 (Formula 3.3 in Setterdahl 2025)
            E1 = 0.5 * (dE2 + np.sqrt(dE2**2 + ((4 * dE2 * m_e) / (1 - np.cos(theta2))) ) )

            # Calculating E0 from E1 and dE1 OR calculate theta from E1 and dE1 (Formulas 3.2 and 3.5 in Setterdahl 2025)
            E0 = E1 + dE1

            if 1 + m_e * (E0**(-1) - E1**(-1)) > 1.0 and 1 + m_e * (E0**(-1) - E1**(-1)) < -1.0:
                print(f"Invalid arccos value: {1 + m_e * (E0**(-1) - E1**(-1)) }")
                print(f"E0: {E0}")
                print(f"E1: {E1}")

            theta = np.arccos(1 + m_e * (E0**(-1) - E1**(-1)) )

            # If calculation of theta goes awry
            if math.isnan(theta):
            #    print(f"nan theta-value found")
            #    print(f"E0: {E0}, E1: {E1}, theta2: {theta2}")
            #    print(f"Value inside arccos: {1 + m_e * (E0**(-1) - E1**(-1))}")
                reconstruction_fails[0] += 1


            # Calculating the cone axis (n) (Correction on formula on page 32 in Setterdahl 2025)
            n = (s1 - s2)  / np.linalg.norm(s1 - s2)

            # The cone vertex is just the first scattering coordinate
            a = s1

            # Storing the gamma cone parameters 
            cone_params = np.concatenate((np.array([theta]), n, a, np.array([region1, region2, region3]), np.array([E0, theta2])))

            # Cone params that can be saved as .csv-files for simple backprojection. Same format as Lena's code
            csv_cone_params = np.concatenate((np.array([ncase]), a, n, np.array([theta]), np.array([sourceX, sourceY, sourceZ])))

            self.gamma_cone_params.append(cone_params)
            self.gamma_cone_event_indicies.append(index)
            self.csv_gamma_cone_params.append(csv_cone_params)

        for index in range(len(self.detectable_double_neutron_events)):

            # Skip all entries where the chain is not 2
            if self.detectable_double_neutron_events[index].chain != 2:
                continue

            # Checking if the three interactions happened in three unique scintillators
            region1 = self.detectable_double_neutron_events[index - 1].region
            region2 = self.detectable_double_neutron_events[index - 0].region

            # Saving interaction code and source coordinates
            ncase = self.detectable_double_neutron_events[index].ncase
            sourceX = self.detectable_double_neutron_events[index].source_x
            sourceY = self.detectable_double_neutron_events[index].source_y
            sourceZ = self.detectable_double_neutron_events[index].source_z

            # Scintillator hits (first, second and third hit)
            s1 = np.array([self.detectable_double_neutron_events[index - 1].crash_x, self.detectable_double_neutron_events[index - 1].crash_y, self.detectable_double_neutron_events[index - 1].crash_z])  # First hist [cm]
            s2 = np.array([self.detectable_double_neutron_events[index - 0].crash_x, self.detectable_double_neutron_events[index - 0].crash_y, self.detectable_double_neutron_events[index - 0].crash_z])  # Second hit [cm]

            # Distance vector between the two hits
            d12 = (s1 - s2) / 100 # [m]

            # Energy deposition
            Ep = round(self.detectable_double_neutron_events[index - 1].energy_in - self.detectable_double_neutron_events[index - 1].energy_out, 6)  # First hit

            # Collision times
            t1 = self.detectable_double_neutron_events[index - 1].particle_age # First hit [µs]
            t2 = self.detectable_double_neutron_events[index - 0].particle_age # Second hit [µs]
            TOF = (t2 - t1) / 1e6   # Time of flight [s]

            # Calculating the scattered neutron energy, formula 3.7 in Setterdahl 2025
            En_scat = 0.5 * m_n * ((np.linalg.norm(d12) / (TOF)) / c) ** 2   # Unit in MeV

            # Calculating the original neutron energy, formula 3.6 in Setterdahl 2025
            En = En_scat + Ep   # Unit in MeV

            # Calculating the cone half angle theta, formula 3.8 in Setterdahl 2025
            theta = np.arccos(np.sqrt(En_scat/En))  # Unit in radians

            # If calculation of theta goes awry
            if math.isnan(theta):
                #print(f"nan theta-value found")
                #print(f"En: {En}, E1: {Ep}, TOF: {TOF}")
                reconstruction_fails[1] += 1

            # Calculating the cone axis (n) (Correction on formula on page 32 in Setterdahl 2025)
            n = (s1 - s2)  / np.linalg.norm(s1 - s2)

            # The cone vertex is just the coordinate of the first hit
            a = s1

            # Storing the neutron cone parameters 
            cone_params = np.concatenate((np.array([theta]), n, a, np.array([region1, region2]), np.array([En, Ep])))

            # Cone params that can be saved as .csv-files for simple backprojection. Same format as Lena's code
            csv_cone_params = np.concatenate((np.array([ncase]), a, n, np.array([theta]), np.array([sourceX, sourceY, sourceZ])))

            self.neutron_cone_params.append(cone_params)
            self.neutron_cone_event_indicies.append(index)
            self.csv_neutron_cone_params.append(csv_cone_params)

        print(f"Cone parameters calculated, time used: {round(time.time() - time_stamp, 3)} s")
        print(f"Gamma cones: {len(self.gamma_cone_params)}, neutron cones: {len(self.neutron_cone_params)}")
        print(f"Reconstruction fails: Gammas ({reconstruction_fails[0]}), Neutrons ({reconstruction_fails[1]})")

        # Converting lists into numpy arrays
        self.gamma_cone_params = np.array(self.gamma_cone_params)
        self.gamma_cone_event_indicies = np.array(self.gamma_cone_event_indicies)
        self.csv_gamma_cone_params = np.array(self.csv_gamma_cone_params)

        self.neutron_cone_params = np.array(self.neutron_cone_params)
        self.neutron_cone_event_indicies = np.array(self.neutron_cone_event_indicies)
        self.csv_neutron_cone_params = np.array(self.csv_neutron_cone_params)

    def create_cone_param_csvs(self) -> None:
        """
        Function that uses the 'csv_neutron_cone_params' and 'csv_gamma_cone_params' to create two csv files with cone parameters
        These csv files can then be used to perform simple backprojection either directly through "..." or by conversion into .root files
        """

        # Defining file paths
        gamma_file = self.folder_path + "/gamma_ConeParams.csv"
        neutron_file = self.folder_path + "/neutron_ConeParams.csv"

        csv_header = ["eventID", "x1", "y1", "z1", "nx", "ny", "nz","theta", "sourceX", "sourceY", "sourceZ"]

        # Writing gamma cone params to .csv file
        df = pd.DataFrame(self.csv_gamma_cone_params)
        df.to_csv(gamma_file, header=csv_header, index=None)
        
        # Writing neutron cone params to .csv file
        df = pd.DataFrame(self.csv_neutron_cone_params)
        df.to_csv(neutron_file, header=csv_header, index=None)

        print(f".csv files created: \n {gamma_file} \n {neutron_file}")


if __name__ == "__main__":
    fldrpth = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\Studie 1\Pasienter\Test"
    test = DetectionDataStorage(fldrpth)
    test.load_data()

    test.event_builder()
    test.calculate_cone_params()
    test.create_cone_param_csvs()
