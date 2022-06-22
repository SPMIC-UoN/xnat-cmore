# CMORE preprocessing on XNAT

This module contains an XNAT container service plugin to run preprocessing for CMORE data.

## Installation

### Prerequisites

XNAT 1.7 or 1.8 is required.

The XNAT container service plugin must be installed. This is present by default in XNAT 1.8, however for
version 1.7 if may need to be installed first.

### Install the Docker container

 - From the menu select `Administer->Plugin Settings`
 - Select `Images and commands`
 - Select `Add new image`
 - For `Image Name` enter `martincraig/xnat-cmore`. Leave version blank
 - Select `Pull image`

### Add the command definition if required

There is a bug in some versions of XNAT that means the command definition is not correctly extracted
from the Docker image. Under `Administer->Plugin Settings`, look for `Run CMORE preprocessing` under `Command Configurations`. If
it is *not* present you will need to do the following:

 - Under `Images and Commands` expand hidden images
 - Find `martincraig/xnat-cmore` and click `Add Command`
 - Delete any text, and paste the contents of `docker/cmore_preproc_cmd.json` into the window
 - Click `Save command`

## Enabling and using the command

To enable the command for the site, navigate to `Administer->Plugin Settings->Command configurations`, ensure that `Run CMORE preprocessing` is enabled using the toggle button.

Once this is done, you can enable the command for a project by selecting `Project Settings` and toggling the `Run CMORE preprocessing` button.

To run the command on a session, navigate to the MR session and click the checkbox to select all scans. Select `Run Container->cmore-preproc`

### Command options

Command options can be set at a project level (in Project Settings) and also overridden when the container is run.

 - `dcm2niix flags` - These options are passed to the DCM2NIIX command. You can modify them if you want to use a particular naming convention or convert your DICOMS in a particular way, however the default should work in most cases
 - `T2star method` - Two different methods of fitting the T2* map are provided, `loglin` or `2p_exp`. The default is `all` which will run both methods and upload separately named maps
 - `T2star matcher` - This is a substring which will be used to identify scans that contain T2* mapping data. It will probably need to be customized at the project level depending on the scan naming convention in the acquisitions.
 
## Background information

Original specification of the preprocessing for the CMORE project is as follows:

The T1 data needs converting to nifti:

  - For Siemens, there are 3 files, it’s T1Map_LongT1_MOCO with a single image that is the one I am interested in for CMORE. The conversion I use is dcm2niix –o [output folder] –f %n_%p_%q –m y –z y [dicom folder]

  - For Philips, there is 1 file where the final 2 images are the maps I am interested in. If these could be separated from the other images during conversion, but the 2 maps can be in a single file after conversion. The conversion I use is dcm2niix –o [output folder] –f %n_%p_%q –p y –z y [dicom folder]

The T2* data needs converting to nifti, and then T2*, R2* and B0 maps calculated:

Conversion: For Siemens, I use is dcm2niix –o [output folder] –f %n_%p_%q –m y –z y [dicom folder], for Philips I use dcm2niix –o [output folder] –f %n_%p_%q –m y –p y –z y [dicom folder]

Mapping: For T2* fit, output T2* and R2* maps for 2 parameter exponential fit and also the log-linear fit.

  - For Siemens, there are 2 files, one for magnitude and one for phase data. The magnitude data file has all 12 echoes for T2* mapping within the single file. For B0, echo 1 is 1st image and echo 2 is 2nd image of phase data.

  - For Philips, the magnitude and phase data are in the same file. For T2* mapping, magnitude data is images 1-12. For B0, echo 1 is 13th image and echo 2 is 14th image.

 

