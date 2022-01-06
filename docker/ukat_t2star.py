"""
Simple wrapper script for UKAT T2star mapping code

Intended for use in Docker container for XNAT

Usage: ukat_t2star.py <indir> <outdir> <method>
"""
import os
import sys

import numpy as np
import nibabel as nib
import json

from ukat.data import fetch
from ukat.mapping.t2star import T2Star

def is_mag_fname(fname):
    if "_" not in fname:
        return True
    ftype = fname[fname.rindex("_")+1:]
    try:
        seriesnum = int(ftype)
        return True
    except ValueError:
        # File has disambiguation string, so is phase
        # or real/imag part
        return False

indir = sys.argv[1]
outdir = sys.argv[2]
method = sys.argv[3]

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
            elif not phase_info_in_fname and "PHASE" in metadata.get("ImageType", []):
                print("INFO: Image %s is not magnitude - ignoring" % fname)
            elif phase_info_in_fname and not is_mag_fname(base_fname):
                print("INFO: Image %s is not magnitude - ignoring" % fname)
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
    data = sorted(data)
    imgs = np.stack([d[1] for d in data], axis=-1)
    tes = [d[0] for d in data]
    print("INFO: %i images found" % len(data))
    print("INFO: TEs: %s" % tes)
    mapper_loglin = T2Star(imgs, tes, affine=affine, method=method)
    # Extract the T2* map from the object
    t2star_loglin = mapper_loglin.t2star_map

    # Save output maps to Nifti
    mapper_loglin.to_nifti(output_directory=outdir, maps=['m0', 't2star'], base_file_name=fprefix)
else:
    print("WARNING: No data found - no T2* map will be generated")

print("DONE")
print("%s" % os.listdir(outdir))

