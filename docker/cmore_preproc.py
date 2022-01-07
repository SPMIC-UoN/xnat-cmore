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
if len(sys.argv) > 3:
    dcm2niix_args = sys.argv[3]
else:
    dcm2niix_args = "-m n -f %%n_%%p_%%q -z y"
if len(sys.argv) > 4:
    t2star_method = sys.argv[4]
else:
    t2star_method = "all"

# Load input data
print("Loading from %s" % indir)
print("Producing output in %s" % outdir)

for fname in os.listdir(indir):
    print(fname)

# Do nifti conversion
os.makedirs("%s/nifti" % outdir, exist_ok=True, mode=0o777)
cmd = "dcm2niix -o %s/nifti %s %s" % (outdir, dcm2niix_args, indir)
print(cmd)
os.system(cmd)

# Generate T2* map if we have relevant data
os.makedirs("%s/t2star_in" % outdir)
os.system("cp %s/nifti/*T2star* %s/t2star_in" % (outdir, outdir))
os.makedirs("%s/t2star" % outdir)
cmd = "python ukat_t2star.py %s/t2star_in %s/t2star %s" % (outdir, outdir, t2star_method)
print(cmd)
os.system(cmd)

# Generate B0 map if we have relevant data
os.makedirs("%s/b0map" % outdir)
cmd = "python ukat_b0.py %s/t2star_in %s/b0map" % (outdir, outdir)
print(cmd)
os.system(cmd)

# Make sure we don't upload empty resource catalogs for irrelevant outputs
for subdir in ("b0map", "t2star"):
    d = os.path.join(outdir, subdir)
    if not os.listdir(d):
        os.rmdir(d)

print("DONE")

