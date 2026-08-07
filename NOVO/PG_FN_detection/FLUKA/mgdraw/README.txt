Contains Fortran scripts to be used in FLUKA
Last update 07.08.2025:
Removal of mgdraw versions v03, v04 and v05.
Upload of mgdraw version v06 (48 bar NOVCoDA) and versions v08 (singular Dresden model) and v09 (quadruple Dresden-model)


mgdraw_v06_patient_detection.f
  Prints explicit FLUKA interactions in FLUKA regions 1 - 48 (scintillator bars) in list mode
  18 output values per entry:
  NCASE: Primary particle ID, ICODE: Interaction code, JTRACK: Incident particle type, KPART(IP): IPth secondary particle type, 
  LLOUSE: Direct from production to detection? (0=No, 1=Yes), ICHTAR, IBTAR: Z and A-values of target atom, 
  Tki(IP): Total kinetic energy of IPth secondary particle [GeV], ETRACK-AM(JTRACK): Kinetic energy of incident particle [GeV]
  XSCO, YSCO, ZSCO: X, Y and Z-coordinate of interaction [cm], MREG: Region of interaction (1-48), 
  LTRACK: Incident particle generation, ATRACK: Time lapsed since primary proton spawn [µs],
  SPAUSR(2) - SPAUSR(4): X, Y and Z-production coordinates of secondary photon/neutron (in target/patient)

mgdraw_v08_OncoRay_model.f
  Prints explicit FLUKA interactions in FLUKA regions 1 - 48 (scintillator bars) in list mode
  18 output values per entry:
  NCASE: Primary particle ID, ICODE: Interaction code, JTRACK: Incident particle type, KPART(IP): IPth secondary particle type, 
  LLOUSE: Direct from production to detection? (0=No, 1=Yes), ISPUSR(1 - 2): Non-functional, 
  Tki(IP): Total kinetic energy of IPth secondary particle [GeV], ETRACK-AM(JTRACK): Kinetic energy of incident particle [GeV]
  XSCO, YSCO, ZSCO: X, Y and Z-coordinate of interaction [cm], MREG: Region of interaction (1-48), 
  LTRACK: Incident particle generation, ATRACK: Time lapsed since primary proton spawn [µs],
  SPAUSR(2) - SPAUSR(4): X, Y and Z-production coordinates of secondary photon/neutron (in target/patient) [cm],
  SPAUSR(1): Kinetic energy of produced secondary photon/neutron at production [GeV]

mgdraw_v09_OncoRay_lattice.f (In development)
  Prints explicit FLUKA interactions in FLUKA regions 1 - 48 (scintillator bars) in list mode
  Exludes entries with cross scatter between lattice copies
  18 output values per entry:
  NCASE: Primary particle ID, ICODE: Interaction code, JTRACK: Incident particle type, KPART(IP): IPth secondary particle type, 
  LLOUSE: Direct from production to detection? (0=No, 1=Yes), ISPUSR(4 - 4): Cross-scatter value, 
  Tki(IP): Total kinetic energy of IPth secondary particle [GeV], ETRACK-AM(JTRACK): Kinetic energy of incident particle [GeV]
  XSCO, YSCO, ZSCO: X, Y and Z-coordinate of interaction [cm], MREG: Region of interaction (1-48), 
  LTRACK: Incident particle generation, ATRACK: Time lapsed since primary proton spawn [µs],
  SPAUSR(2) - SPAUSR(4): X, Y and Z-production coordinates of secondary photon/neutron (in target/patient) [cm],
  SPAUSR(1): Kinetic energy of produced secondary photon/neutron at production [GeV]
