"""
CMORE: Runs dcm2niix, B0 and T2* mapping code on a scan

Intended for use in Docker container for XNAT
"""
import argparse
import os

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        argparse.ArgumentParser.__init__(self, prog="cmore_preproc", add_help=True, **kwargs)
        self.add_argument("--indir", help="Directory containing input DICOMs")
        self.add_argument("--outdir", help="Directory to store output")
        self.add_argument("--dcm2niix-args", help="Options to use when doing DICOM->NIFTI conversion", default="-m n -f %n_%p_%q -z y")
        self.add_argument("--t2star-method", help="Method to use when doing T2* processing", choices=["loglin", "2p_exp", "all"], default="all")
        self.add_argument("--t2star-matcher", help="Match substring to identify files for T2* processing", default="T2star")

arg_parser = ArgumentParser()
options = arg_parser.parse_args()
    
# Load input data
print("Loading from %s" % options.indir)
print("Producing output in %s" % options.outdir)
print("Input files:")
for fname in os.listdir(options.indir):
    print(fname)

print("\nDoing NIFTI conversion")
niftidir = os.path.join(options.outdir, "nifti")
os.makedirs(niftidir, exist_ok=True, mode=0o777)
cmd = "dcm2niix -o %s %s %s" % (niftidir, options.dcm2niix_args, options.indir)
print(cmd)
os.system(cmd)

print("\nGenerating T2* map if data available")
t2star_indir = os.path.join(options.outdir, "t2star_in")
t2star_outdir = os.path.join(options.outdir, "t2star")
os.makedirs(t2star_indir, exist_ok=True, mode=0o777)
os.makedirs(t2star_outdir, exist_ok=True, mode=0o777)
os.system("cp %s/*%s* %s" % (niftidir, options.t2star_matcher, t2star_indir))
cmd = "python cmore_t2star.py %s %s %s" % (t2star_indir, t2star_outdir, options.t2star_method)
print(cmd)
os.system(cmd)

print("\nGenerating B0 map if data available")
b0map_outdir = os.path.join(options.outdir, "b0map")
os.makedirs(b0map_outdir, exist_ok=True, mode=0o777)
cmd = "python cmore_b0.py %s %s" % (t2star_indir, b0map_outdir)
print(cmd)
os.system(cmd)

# Make sure we don't upload empty resource catalogs for irrelevant outputs
for subdir in (t2star_outdir, b0map_outdir):
    if not os.listdir(subdir):
        os.rmdir(subdir)

print("DONE")
