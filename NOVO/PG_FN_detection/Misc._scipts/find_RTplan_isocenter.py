import pydicom

# Path to DICOM plan (RP...dcm)
rtplan_file = r"\\klient.uib.no\FELLES\LAB-IT\IFT\Medisinskfysikk\Sander\Studie 1\Anon_Brain_01\RP1.2.752.243.1.1.20250529162730899.1100.24200.dcm"
rtplan_file = r"\\klient.uib.no\FELLES\LAB-IT\IFT\Medisinskfysikk\Sander\Studie 1\Anon_HNC_05\RP1.2.752.243.1.1.20250509100134489.4400.57445.dcm"

rp = pydicom.dcmread(rtplan_file)

for beam in rp.IonBeamSequence:
    name = getattr(beam, "BeamName", f"Beam {beam.BeamNumber}")

    cp0 = beam.IonControlPointSequence[0]
    iso = cp0.IsocenterPosition

    print(f"{name}: Isocenter = {iso}")