"""
Simple wrapper script for UKAT B0 mapping code

Intended for use in Docker container for XNAT

Usage: ukat_b0.py <indir> <outdir>
"""
import os
import sys

import numpy as np
import nibabel as nib
import json

from ukat.data import fetch
from ukat.mapping.b0 import B0

indir = sys.argv[1]
outdir = sys.argv[2]

# Load input data
print("Loading from %s" % indir)
data = []
affine = None
fprefix = None
phase_info_in_fname = False

# First we need to figure out if dcm2niix has embedded phase/mag info in the
# file name as it sometimes needs to do this
for fname in os.listdir(indir):
    if fname.endswith(".nii") or fname.endswith(".nii.gz"):
        base_fname = fname[:fname.index(".")]
        if base_fname.endswith("_ph"):
            phase_info_in_fname = True

if phase_info_in_fname:
    print("INFO: Phase information is embedded in filename")

for fname in os.listdir(indir):
    if fname.endswith(".nii") or fname.endswith(".nii.gz"):
        base_fname = fname[:fname.index(".")]
        if os.path.exists(os.path.join(indir, base_fname + ".json")):
            nii = nib.load(os.path.join(indir, fname))
            with open(os.path.join(indir, base_fname + ".json")) as f:
                metadata = json.load(f)

            image = nii.get_fdata()
            te = metadata.get("EchoTime", None)
            if image.ndim > 3 and image.shape[3] > 1:
                print("WARNING: Image %s is 4D - ignoring" % fname)
            elif te is None:
                print("WARNING: Image %s has no EchoTime defined in metadata - ignoring" % fname)
            elif not phase_info_in_fname and "PHASE" not in metadata.get("ImageType", []):
                print("INFO: Image %s is not phase  - ignoring" % fname)
            elif phase_info_in_fname and not base_fname.endswith("_ph"):
                print("INFO: Image %s is not phase - ignoring" % fname)
            else:
                print("Processing %s" % fname)
                data.append((te*1000, image))
                if affine is None:
                    affine = nii.header.get_best_affine()
                if fprefix is None:
                    fprefix = base_fname
                else:
                    fprefix = os.path.commonprefix([fprefix, base_fname])
        else:
            print("WARNING: Found Nifti file %s without corresponding JSON - ignoring" % fname)

if data:
    data = sorted(data, key=lambda x: x[0])
    imgs = np.stack([d[1] for d in data], axis=-1)
    tes = [d[0] for d in data]
    print("INFO: %i images found" % len(data))
    print("INFO: TEs: %s" % tes)
    mapper = B0(imgs, tes, affine=affine)

    # Extract the maps and save to Nifti
    first_echo = mapper.phase0
    second_echo = mapper.phase1
    difference_echos = mapper.phase_difference
    b0map = mapper.b0_map

    # Save output maps to Nifti
    mapper.to_nifti(output_directory=outdir, maps=['phase0', 'phase1', 'phase_difference', 'b0_map'], base_file_name=fprefix)
else:
    print("WARNING: No data found - no B0s map will be generated")

print("DONE")
print("%s" % os.listdir(outdir))

