'''
    Script for extracting ROI label statistics for multiple atlases from PET SUVR image.
    This script supersedes the older pet_quants.py. The new script principally depends on:
        a) antsnetct output (rather than the older ANTsCT pipeline)
        b) numpy-based ROI stats functions available through antsnetct: https://github.com/ftdc-picsl/antsnetct/blob/c70f75ecb4844f875d2f4031334d59b44665a313/antsnetct/ants_helpers.py#L2532-L2640

'''

import os 
import glob
from antsnetct import *
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
    trcInd = [i for i, s in enumerate(fParts) if "trc" in s]
    acqInd = [i for i, s in enumerate(fParts) if "acq" in s]
    runInd = [i for i, s in enumerate(fParts) if "run" in s]
    lastInd = max(acqInd,runInd)[0]
    fStem = "{}/{}".format(dirName, "_".join(fParts[:(lastInd+1)]))
    
    id = fParts[0]
    ses = fParts[1]
    
    if "sub-" in id:
        id = id.split('-')[1]
    if "ses-" in ses:
        ses = ses.split('-')[1]
    
    return((id,ses,fStem))


def getSegName(dseg_file):
    baseName = os.path.basename(path)
    fParts = str.split(baseName,"_")
    segName = [s for i, s in enumerate(fParts) if "seg-" in s]
    return(segName.replace("seg-",""))


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
        description="Summarize ROI values using a user-supplied label image and definitions file.")
    parser.add_argument('-s', '--subject', default=None, action='store', required=True, help='SubjectID')
    parser.add_argument('-t', '--session', default=None, action='store', required=True, help='SessionID')
    parser.add_argument('-p', '--parcellation_list', nargs="+", default=None, action = 'store', required = False, help = 'Optional list of segmentation/parcellation names, if not indicated by the BIDS seg entity.')
    parser.add_argument('-l','--label_images', nargs="+", help='list of user-specified label files')
    parser.add_argument('-d','--label_definitions', nargs="+", help='list of user-specified label descriptions to accompany label_images')
    parser.add_argument('-o', '--outputStem', nargs=1, default=None,  action='store', required=True, help='output stem')
    parser.add_argument('-i', '--PETFile', nargs=1, help='PET file path')
    args = parser.parse_args()
    print(args)
    
    outputStem = args.outputStem[0]
    petFile = args.PETFile[0]
    petDir = os.path.dirname(petFile[0])
    outputDir = os.path.dirname(args.outputStem[0])
    
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    psOut = getMyPID( 'jefphi', outputStem )
    threads = getMyThreads( 'jefphi', outputStem)
    logging.info("Started with nThreads="+str(threads))
    
    user = os.getenv('USER')
    threads = getMyThreads( user, outputStem )
    logging.info("Starting ROI label stats calculation with nThreads="+str(threads))
    
    label_stats_output_files = list()
    
    for i in range(len(args.label_images)):
        label_image = args.label_images[i]
        label_image = bids_helpers.image_to_bids(src_image = args.label_images[i],
            dataset_dir = "/project/ftdc_pipeline/data/ashs_t1ext",
            dest_rel_path = outputDir.replace("/project/ftdc_pipeline/data/pennpet",".."),
            overwrite = True)
        label_desc = bids_helpers.load_label_definitions(args.label_definitions[i])
        try:
            args.parcellation_list
        except NameError:
            segName = getSegName(label_image)
        else:
            segName = args.parcellation_list[i]
        
        # Get SUVR values for each label image.
        label_suvr_stats = ants_helpers.numpy_label_statistics(label_image = label_image,
        label_definitions = label_desc, work_dir = outputDir, scalar_image = petFile)
#        label_suvr_file = "{}/{}_desc-suvr_labelstats.tsv".format(outputDir,os.path.basename(label_image).replace(dropString,''))
        label_suvr_file = outputStem.replace("_desc-", segName + "_desc-") + "_labelstats.tsv"
        bids_helpers.write_tabular_data(label_suvr_stats, label_suvr_file)
        label_stats_output_files.append(label_suvr_file)
        logging.info("Output written to " + label_suvr_file)

if __name__ == "__main__":
    main()
