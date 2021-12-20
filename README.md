CMORE preprocessing on XNAT
=========================== 

Ideally on upload to XNAT, the following would happen for T1 and T2* scans:

The T1 data needs converting to nifti:

  - For Siemens, there are 3 files, it’s T1Map_LongT1_MOCO with a single image that is the one I am interested in for CMORE. The conversion I use is dcm2niix –o [output folder] –f %n_%p_%q –m y –z y [dicom folder]

  - For Philips, there is 1 file where the final 2 images are the maps I am interested in. If these could be separated from the other images during conversion, but the 2 maps can be in a single file after conversion. The conversion I use is dcm2niix –o [output folder] –f %n_%p_%q –p y –z y [dicom folder]

The T2* data needs converting to nifti, and then T2*, R2* and B0 maps calculated:

Conversion: For Siemens, I use is dcm2niix –o [output folder] –f %n_%p_%q –m y –z y [dicom folder], for Philips I use dcm2niix –o [output folder] –f %n_%p_%q –m y –p y –z y [dicom folder]

Mapping: For T2* fit, output T2* and R2* maps for 2 parameter exponential fit and also the log-linear fit.

  - For Siemens, there are 2 files, one for magnitude and one for phase data. The magnitude data file has all 12 echoes for T2* mapping within the single file. For B0, echo 1 is 1st image and echo 2 is 2nd image of phase data.

  - For Philips, the magnitude and phase data are in the same file. For T2* mapping, magnitude data is images 1-12. For B0, echo 1 is 13th image and echo 2 is 14th image.

 

