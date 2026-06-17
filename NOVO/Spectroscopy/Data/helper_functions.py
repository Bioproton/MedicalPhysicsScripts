import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import load_npz

def read_production_spect(foldername,num_files=80):
    files = os.listdir(foldername)

    ICODE_pg = []
    XSCO_pg = []
    YSCO_pg = []
    ZSCO_pg = []
    energies_pg = []
    ICHTAR_pg = []
    IBTAR_pg = []
    IONA_pg = []
    IONZ_pg = []

    for file in files[:num_files]:
        #print(foldername+file)
        data = np.load(foldername+"/"+file)
        id = (list(data["id"]))
        #print(len(id))
        ICODE = list(data["ICODE"])
        XSCO = list(data["XSCO"])
        YSCO = list(data["YSCO"])
        ZSCO = list(data["ZSCO"])
        energy = (list(data["energy"]))
        IBTAR = list(data["IBTAR"])
        ICHTAR =list(data["ICHTAR"])
        IONA =list(data["IONA"])
        IONZ =list(data["IONZ"])

        #print(id[0])

        for i in range(len(id)):
            if id[i] == "7":

                ICODE_pg.append(ICODE[i])
                XSCO_pg.append(XSCO[i])
                YSCO_pg.append(YSCO[i])
                ZSCO_pg.append(ZSCO[i])
                energies_pg.append(energy[i])
                IBTAR_pg.append(IBTAR[i])
                ICHTAR_pg.append(ICHTAR[i])
                IONA_pg.append(IONA[i])
                IONZ_pg.append(IONZ[i])
        
    ZSCO_pg = np.array(ZSCO_pg).astype(float)
    XSCO_pg = np.array(XSCO_pg).astype(float)
    YSCO_pg = np.array(YSCO_pg).astype(float)
    energies_pg = np.array(energies_pg).astype(float)


    return ICODE_pg, XSCO_pg, YSCO_pg, ZSCO_pg, energies_pg, ICHTAR_pg, IBTAR_pg, IONA_pg, IONZ_pg

def read_production_spect_coordinates(foldername,num_files=80):
    files = os.listdir(foldername)

    XSCO_pg = []
    YSCO_pg = []
    ZSCO_pg = []
   

    for file in files[:num_files]:
        #print(foldername+file)
        data = np.load(foldername+"/"+file)
        XSCO = list(data["XSCO"])
        YSCO = list(data["YSCO"])
        ZSCO = list(data["ZSCO"])
        id = (list(data["id"]))
        #print(id[0])

        for i in range(len(id)):
            if id[i] == "7":
                XSCO_pg.append(XSCO[i])
                YSCO_pg.append(YSCO[i])
                ZSCO_pg.append(ZSCO[i])
               
        
    ZSCO_pg = np.array(ZSCO_pg).astype(float)
    XSCO_pg = np.array(XSCO_pg).astype(float)
    YSCO_pg = np.array(YSCO_pg).astype(float)


    return  XSCO_pg, YSCO_pg, ZSCO_pg



def read_production_spect_short(foldername,num_files=80):
    files = os.listdir(foldername)
    ZSCO_pg = []
    energies_pg = []
    ICHTAR_pg = []
    IBTAR_pg = []
    IONA_pg = []
    IONZ_pg = []

    for file in files[:num_files]:
        data = np.load(foldername+file)
        id = (list(data["id"]))

        ZSCO = (list(data["ZSCO"]))
        energy = (list(data["energy"]))
        IBTAR = list(data["IBTAR"])
        ICHTAR =list(data["ICHTAR"])
        IONA =list(data["IONA"])
        IONZ =list(data["IONZ"])

        for i in range(len(id)):
            if id[i] == "7":
                ZSCO_pg.append(ZSCO[i])
                energies_pg.append(energy[i])
                IBTAR_pg.append(IBTAR[i])
                ICHTAR_pg.append(ICHTAR[i])
                IONA_pg.append(IONA[i])
                IONZ_pg.append(IONZ[i])
        
    ZSCO_pg = np.array(ZSCO_pg).astype(float)
    energies_pg = np.array(energies_pg).astype(float)

    return  ZSCO_pg, energies_pg, ICHTAR_pg, IBTAR_pg, IONA_pg, IONZ_pg

def read_production_spect_target_nucleus_specific(foldername,num_files=80,ichtar="8",ibtar="16"):
    files = os.listdir(foldername)
    ZSCO_pg = []
    energies_pg = []
    IONA_pg = []
    IONZ_pg = []

    for file in files[:num_files]:
        data = np.load(foldername+"/"+file)
        id = (list(data["id"]))

        ZSCO = (list(data["ZSCO"]))
        energy = (list(data["energy"]))
        IBTAR = list(data["IBTAR"])
        ICHTAR =list(data["ICHTAR"])
        IONA =list(data["IONA"])
        IONZ =list(data["IONZ"])

        for i in range(len(id)):
            if id[i] == "7" and ICHTAR[i] == ichtar and IBTAR[i]==ibtar:
                ZSCO_pg.append(ZSCO[i])
                energies_pg.append(energy[i])
                IONA_pg.append(IONA[i])
                IONZ_pg.append(IONZ[i])

    ZSCO_pg = np.array(ZSCO_pg).astype(float)
    energies_pg = np.array(energies_pg).astype(float)

    return  ZSCO_pg, energies_pg,IONA_pg, IONZ_pg

def read_scintillator_interactions_v02_ncase_only(foldername, num_files=80):
    files = os.listdir(foldername)

    ncase_list = []
    #ICODE = []
    #JTRACK = []
    #KPART_IP = []
    LLOUSE = []
    ICHTAR = []
    IBTAR = []
    TKI_IP = []
    ETRACK_AM = []
    #MREG_list = []
    #LTRACK = []
    #ATRACK = []
    #XSCO_prod = []
    #YSCO_prod = []
    #ZSCO_prod = []

    i = 0

    for file in files[:num_files]:
        #print(i, file)
        i+=1
        file_path = os.path.join(foldername, file)

        # Accumulate per NCASE (only → mreg removed)
        accum = {}

        with open(file_path, "r") as f:
            for line in f:
                elements = np.array(line.split())

                if len(elements) == 18:
                    if elements[2] == "7" and elements[3] == "3" and "**" not in elements[14]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[7])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
                if len(elements) == 17:
                    if elements[2] == "7" and elements[3] == "3" and "**" not in elements[13]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[6])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
            
            

        # Save results after finishing each file
        for ncase, data in accum.items():
            row = data["last_row"]
            if len(row) == 18:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5])
                IBTAR.append(row[6])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[8]))
            
            if len(row) == 17:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5][:2])
                IBTAR.append(row[5][2:])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[7]))
        

    return (LLOUSE, ICHTAR,
            IBTAR, np.array(TKI_IP), np.array(ETRACK_AM))
    #return (ncase_list, ICODE, JTRACK, KPART_IP, LLOUSE, ICHTAR,
    #        IBTAR, np.array(TKI_IP), np.array(ETRACK_AM),
    #        LTRACK, ATRACK,
    #        np.array(XSCO_prod), np.array(YSCO_prod), np.array(ZSCO_prod))


def read_scintillator_interactions_v02(foldername, num_files = 80):
    files = os.listdir(foldername)
    ncase = []
    ICODE = []
    JTRACK = []
    KPART_IP = []
    LLOUSE = []
    ICHTAR = []
    IBTAR = []
    TKI_IP = []
    ETRACK_AM = []
    MREG = []
    LTRACK = []
    ATRACK = []
    XSCO_prod = []
    YSCO_prod = []
    ZSCO_prod = []
 
    for file in files[:num_files]:
        f = open(foldername + "/" + file,"r")
        for line in f:
            elements = np.array(line.split())
            if len(elements) == 18:
                if elements[2] == "7" and elements[3] == "3" and "**" not in elements[14]: 
                    ncase.append(elements[0])
                    ICODE.append(elements[1])
                    JTRACK.append(elements[2])
                    KPART_IP.append(elements[3])
                    LLOUSE.append(elements[4])
                    ICHTAR.append(elements[5])
                    IBTAR.append(elements[6])
                    TKI_IP.append(elements[7])
                    ETRACK_AM.append(elements[8])
                    MREG.append(elements[12])
                    LTRACK.append(elements[13])
                    ATRACK.append(elements[14])
                    XSCO_prod.append(elements[15])
                    YSCO_prod.append(elements[16])
                    ZSCO_prod.append(elements[17])
            if len(elements) == 17:
                if elements[2] == "7" and elements[3] == "3" and "**" not in elements[14]: 
                    ncase.append(elements[0])
                    ICODE.append(elements[1])
                    JTRACK.append(elements[2])
                    KPART_IP.append(elements[3])
                    LLOUSE.append(elements[4])
                    ICHTAR.append(elements[5][:2])
                    IBTAR.append(elements[5][2:])
                    TKI_IP.append(elements[6])
                    ETRACK_AM.append(elements[7])
                    MREG.append(elements[11])
                    LTRACK.append(elements[12])
                    ATRACK.append(elements[13])
                    XSCO_prod.append(elements[14])
                    YSCO_prod.append(elements[15])
                    ZSCO_prod.append(elements[16])


            

    ZSCO_prod = np.array(ZSCO_prod).astype(float)
    XSCO_prod = np.array(XSCO_prod).astype(float)
    YSCO_prod = np.array(YSCO_prod).astype(float)
    TKI_IP = np.array(TKI_IP).astype(float)
    ETRACK_AM = np.array(ETRACK_AM).astype(float)

    return ncase,ICODE,JTRACK,KPART_IP,LLOUSE,ICHTAR,IBTAR,TKI_IP,ETRACK_AM,LTRACK,ATRACK,XSCO_prod,YSCO_prod,ZSCO_prod


def read_composition(filename):
    compositions = {}

    with open(filename, "r") as f:   # replace with your filename
        for line in f:
            if ":" in line:
                element, value = line.split(":")
                compositions[element.strip()] = float(value.strip())

    return compositions




# NOT FINISHED YET, FIX ADDITIONAL ELEMENTS
# should be okay now, fixed additional elemenets
# after elements = elements[1:]
def read_scintillator_interactions_v02_ncase_only_adaptive_weekly(foldername, num_files=100):
    files = os.listdir(foldername)

    ncase_list = []
    #ICODE = []
    #JTRACK = []
    #KPART_IP = []
    LLOUSE = []
    ICHTAR = []
    IBTAR = []
    TKI_IP = []
    ETRACK_AM = []
    #MREG_list = []
    #LTRACK = []
    #ATRACK = []
    #XSCO_prod = []
    #YSCO_prod = []
    #ZSCO_prod = []
    regs = []

    i = 0

    for file in files[:num_files]:
        #print(i, file)
        i+=1
        file_path = os.path.join(foldername, file)

        # Accumulate per NCASE (only → mreg removed)
        accum = {}

        with open(file_path, "r") as f:
            for line in f:
                elements = np.array(line.split())

                #Adaptation for adaptive weekly, MREG added in the start
                if elements[5] == "1":
                    regs.append(elements[0])
                elements = elements[1:]
                
                if len(elements) == 20:
                    if elements[2] == "7" and elements[3] == "3" and "**" not in elements[14]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[7+2])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
                if len(elements) == 19:
                    if elements[2] == "7" and elements[3] == "3" and "**" not in elements[13]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[6+2])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
            
            

        # Save results after finishing each file
        for ncase, data in accum.items():
            row = data["last_row"]
            if len(row) == 20:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5])
                IBTAR.append(row[6])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[8+2]))
            
            if len(row) == 19:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5][:2])
                IBTAR.append(row[5][2:])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[7+2]))
        

    return (LLOUSE, ICHTAR,
            IBTAR, np.array(TKI_IP), np.array(ETRACK_AM), regs)
    #return (ncase_list, ICODE, JTRACK, KPART_IP, LLOUSE, ICHTAR,
    #        IBTAR, np.array(TKI_IP), np.array(ETRACK_AM),
    #        LTRACK, ATRACK,
    #        np.array(XSCO_prod), np.array(YSCO_prod), np.array(ZSCO_prod))

def read_scintillator_interactions_v02_ncase_only_neutrons_adaptive_weekly(foldername, num_files=100):
    files = os.listdir(foldername)

    ncase_list = []
    LLOUSE = []
    ICHTAR = []
    IBTAR = []
    TKI_IP = []
    ETRACK_AM = []
    regs = []

    i = 0

    for file in files[:num_files]:
        #print(i, file)
        i+=1
        file_path = os.path.join(foldername, file)

        # Accumulate per NCASE (only → mreg removed)
        accum = {}

        with open(file_path, "r") as f:
            for line in f:
                elements = np.array(line.split())
                #Adaptation for adaptive weekly, MREG added in the start
                if elements[5] == "1":
                    regs.append(elements[0])
                elements = elements[1:]

                if len(elements) == 20:
                    if elements[2] == "8" and "**" not in elements[14]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[7+2])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
                if len(elements) == 19:
                    if elements[2] == "8" and "**" not in elements[13]:

                        ncase = elements[0]              # <─ Only grouping key
                        tki_ip_val = float(elements[6+2])

                        if ncase not in accum:
                            accum[ncase] = {
                                "TKI_IP": 0.0,
                                "last_row": elements
                            }

                        accum[ncase]["TKI_IP"] += tki_ip_val
                        accum[ncase]["last_row"] = elements
            
            

        for ncase, data in accum.items():
            row = data["last_row"]
            if len(row) == 20:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5])
                IBTAR.append(row[6])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[8+2]))
            
            if len(row) == 19:

                ncase_list.append(ncase)
                LLOUSE.append(row[4])
                ICHTAR.append(row[5][:2])
                IBTAR.append(row[5][2:])
                TKI_IP.append(data["TKI_IP"])
                ETRACK_AM.append(float(row[7+2]))
        

    return (LLOUSE, ICHTAR,
            IBTAR, np.array(TKI_IP), np.array(ETRACK_AM), regs)


def find_HU_group_info(lines, HU_group_elem, i_start, i_end):
    average_atomic_number = -1
    average_atomic_weight = -1
    average_density = -1

    nitrogen_atomic_content = 0
    oxygen_atomic_content = 0
    hydrogen_atomic_content = 0
    carbon_atomic_content = 0
    phospho_atomic_content = 0
    calcium_atomic_content = 0

    for i in range(i_start, i_end):
        elements = lines[i].split()
        if len(elements) > 0:
            if HU_group_elem == elements[1]:
                average_atomic_number = float(elements[2])
                average_atomic_weight = float(elements[3])
                average_density = float(elements[4])

                for j in range(i+4, i + 20):
                    elements_sub = lines[j].split()
                    if len(elements_sub) > 0:
                        if elements_sub[0] == "NITROGEN":
                            nitrogen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "OXYGEN":
                            oxygen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "HYDROGEN":
                            hydrogen_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "CARBON":
                            carbon_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "CALCIUM":
                            calcium_atomic_content = float(elements_sub[2])
                        if elements_sub[0] == "PHOSPHO":
                            phospho_atomic_content = float(elements_sub[2])
                    else:
                        break

    return {"average_atomic_number" : average_atomic_number,
             "average_atomic_weight" : average_atomic_weight,
             "average_density" : average_density, 
             "nitrogen_atomic_content" : nitrogen_atomic_content, 
             "oxygen_atomic_content" : oxygen_atomic_content,
             "hydrogen_atomic_content" : hydrogen_atomic_content,
             "carbon_atomic_content" : carbon_atomic_content,
             "calcium_atomic_content" : calcium_atomic_content,
             "phospho_atomic_content" : phospho_atomic_content,}
    



