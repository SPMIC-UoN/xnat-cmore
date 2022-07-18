"""
CMORE: Simple wrapper script for UKAT kidney segmentation code

Intended for use in Docker container for XNAT

Usage: cmore_tkv.py <indir> <outdir>
"""
import os
import sys

import numpy as np
import nibabel as nib
import json
import requests

from ukat.segmentation import whole_kidney

indir = sys.argv[1]
outdir = sys.argv[2]
project, subject, session = sys.argv[3:]
segmentation = None

# Load input data
print(" - Loading from %s" % indir)
for fname in os.listdir(indir):
    if fname.endswith(".nii") or fname.endswith(".nii.gz"):
        if segmentation is not None:
            print(f" - WARNING: Already found T2w image for kidney segmentation - ignoring {fname}")
            continue

        base_fname = fname[:fname.index(".")]
        nii = nib.load(os.path.join(indir, fname))
        image = nii.get_fdata()
        affine = nii.header.get_best_affine()

        # The segmentor needs both the image array and affine so the size of each voxel is known. post_process=True removes all but
        # the largest two areas in the mask e.g. removes small areas of incorrectly categorised tissue. This can cause issues if the
        # subject has more or less than two kidneys though.
        segmentation = whole_kidney.Segmentation(image, affine, post_process=True)

        # A binary mask of renal tissue can be generated. If the binary flag is not used, the output will be the probability each voxel is renal tissue.
        mask = segmentation.get_mask(binary=True)
        tkv = segmentation.get_tkv()

        segmentation.to_nifti(output_directory=outdir, base_file_name=base_fname, maps=['mask', 'left', 'right', 'individual'])
        volumes = segmentation.get_volumes()
        print(f" - Setting volumes on {host} = {volumes}")
        data = {}
        for k, v in volumes.items():
            data = {f"xnat:experimentData/fields/field[name=kv_{k}]/field" : str(v)}
        host, user, password = os.environ["XNAT_HOST"], os.environ["XNAT_USER"], os.environ["XNAT_PASS"]
        #host = host.replace("http://", "https://") # FIXME hack
        r = requests.put("%s/data/projects/%s/subjects/%s/experiments/%s" % (host, project, subject, session), data=data, auth=(user, password))
        if r.status_code != 200:
            raise RuntimeError(f"Failed to set kidney volume custom variables: {r.text}")

for fname in os.listdir(outdir):
    print(" - %s" % fname)
print(" - DONE")
