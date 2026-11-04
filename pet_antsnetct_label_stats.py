'''
    Script for extracting ROI label statistics from PET SUVR image using label images
    output by antsnetct. This script supersedes the older pet_quants.py. Dependencies:
        a) antsnetct output (rather than the older ANTsCT pipeline)
        b) the antsnetct.ants_helpers.numpy_label_statistics() function
        c) an SUVR map in the space of the T1 used for antsnetct
'''

import os 
import glob
from antsnetct import *
from ants import copy_image_info
import pandas as pd
import argparse
import logging

os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = str(1)
os.environ['MKL_NUM_THREADS'] = str(1)
os.environ['OMP_NUM_THREADS'] = str(1)
os.environ['NUMEXPR_NUM_THREADS'] = str(1)

def parsePath( path ):
    
    dirName = os.path.dirname(path)
    baseName = os.path.basename(path)
    fParts = str.split(baseName,"_")
    sesInd = [i for i, s in enumerate(fParts) if "ses" in s]
    trcInd = [i for i, s in enumerate(fParts) if "trc" in s]
    acqInd = [i for i, s in enumerate(fParts) if "acq" in s]
    runInd = [i for i, s in enumerate(fParts) if "run" in s]
    #descInd = [i for i, s in enumerate(fParts) if "desc" in s]
    lastInd = max(acqInd,runInd,trcInd,sesInd)[0]
    fStem = "{}/{}".format(dirName, "_".join(fParts[:(lastInd+1)]))
    
    id = fParts[0]
    ses = fParts[1]
    
    if "sub-" in id:
        id = id.split('-')[1]
    if "ses-" in ses:
        ses = ses.split('-')[1]
    
    return((id,ses,fStem))

def getSegName(dseg_file):
    baseName = os.path.basename(dseg_file)
    fParts = str.split(baseName,"_")
    segName = [s for i, s in enumerate(fParts) if "seg-" in s]
    return(segName[0].replace("seg-",""))

def getMyPID( uname, outputStem ):
    stream = os.popen("ps -elf | grep "+uname)
    jobList = stream.read().split('\n')
    stream.close()
    thisJob = [ x for x in jobList if outputStem in x ]
    
    if len(thisJob) > 1:
        return None
    
    return(thisJob[0].split(' ')[3])

def getMyThreads( uname, outputStem ):
    pid = getMyPID( uname, outputStem )
    stream = os.popen("ps -o thcount "+str(pid) )
    output = stream.read().split('\n')
    stream.close()
    return( output[1] )

def main():
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Get ROI label statistics from PET SUVR image for all dense segmentations (*dseg.nii.gz) in antsnetct output folder.")
    parser.add_argument('-i', '--PETFile', nargs=1, help='PET file path')
    parser.add_argument('-a', '--antsnetctT1', nargs=1, help='Bias-corrected T1 image from antsnetct output directory')
    args = parser.parse_args()
    print(args)
    
    petFile = args.PETFile[0]
    petDir = os.path.dirname(petFile)
    antsFile = args.antsnetctT1[0]
    antsDir = os.path.dirname(antsFile)
    (subj, petsess, petStem) = parsePath(petFile)
    (subj, mrisess, mriStem) = parsePath(antsFile)
    
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    #psOut = getMyPID( 'jefphi', outputStem )
    #logging.info("psOut: " + psOut)
    #threads = getMyThreads( 'jefphi', outputStem)
    #logging.info("Started with nThreads="+str(threads))
    
    user = os.getenv('USER')
    logging.info("user: " + user)
    #threads = getMyThreads( user, outputStem)
    #logging.info("Starting ROI label stats calculation with nThreads="+str(threads))
    
    label_parc_files = [f for f in glob.glob(mriStem + "_seg-*dseg.nii.gz") if "antsnetct_dseg.nii.gz" not in f]
    label_stats_output_files = list()
 
    for label_image in label_parc_files:
        lab_def = label_image.replace("nii.gz","tsv")
        label_desc = bids_helpers.load_label_definitions(lab_def)
        segName = getSegName(label_image)
        
        # Get SUVR values for each label image.
        try:
            label_suvr_stats = ants_helpers.numpy_label_statistics(label_image = label_image,
                label_definitions = label_desc, work_dir = petDir, scalar_image = petFile)
        except ValueError:
            petImg = image_read(petFile,3)
            antsImg = image_read(antsFile,3)
            petImg = copy_image_info(antsImg, petImg)
            image_write(petImg, petFile)
            label_suvr_stats = ants_helpers.numpy_label_statistics(label_image = label_image,
                label_definitions = label_desc, work_dir = petDir, scalar_image = petFile)
    
        label_suvr_file = petStem.replace("_desc-", "_seg-" + segName + "_desc-") + "_labelstats.tsv"
        bids_helpers.write_tabular_data(label_suvr_stats, label_suvr_file)
        label_stats_output_files.append(label_suvr_file)
    
    return(label_stats_output_files)

if __name__ == "__main__":
    main()
