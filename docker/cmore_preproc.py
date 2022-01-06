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
t2star_method = sys.argv[3]

# Load input data
print("Loading from %s" % indir)
print("Produciung output in %s" % outdir)

for fname in os.listdir(indir):
    print(fname)

os.makedirs("%s/nifti" % outdir, exist_ok=True, mode=0o777)
cmd = "dcm2niix -o %s/nifti -f %%n_%%p_%%q -z y %s" % (outdir, indir)
print(cmd)
os.system(cmd)

os.makedirs("%s/t2star_in" % outdir)
os.system("cp %s/nifti/*T2star* %s/t2star_in" % (outdir, outdir))
os.makedirs("%s/t2star" % outdir)
cmd = "python ukat_t2star.py %s/t2star_in %s/t2star %s" % (outdir, outdir, t2star_method)
print(cmd)
os.system(cmd)

os.makedirs("%s/b0map" % outdir)
cmd = "python ukat_b0.py %s/t2star_in %s/b0map" % (outdir, outdir)
print(cmd)
os.system(cmd)

print("DONE")
print("%s" % os.listdir(outdir))
print("%s" % os.listdir("%s/nifti" % outdir))

