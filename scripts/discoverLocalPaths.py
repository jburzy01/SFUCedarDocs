############################################################
# This script uses rucio to search for DIDs on the grid and
# writes the local paths of the files into. The input files
# are specified below. The output files have a similar name
# pattern.
############################################################

import datetime
import os
import subprocess
import sys
import time

import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('files', nargs='+', help='List of files to process')

args = parser.parse_args()

# Decide here, which input files you want to process
inputDIDPaths = []

#inputDIDPaths.append(data18)

for f in args.files:
    inputDIDPaths.append( f ) 


gridSite = "CA-SFU-T2_LOCALGROUPDISK"

DIDType = "container"
debug = True

def bold(s):
    return '\033[1m' + s + '\033[0m'
def info(indentation = 0):
    return indentation*" " + "INFO: "
def warning(indentation = 0):
    return indentation*" " + bold("WARNING") + ": "
def error(indentation = 0):
    return indentation*" " + bold("ERROR") + ": "

def executeCommand(command, printErrorMessage = True):
    myEnv = os.environ.copy()
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash', env=myEnv)
    out, err = p.communicate()
    out = out.decode("ascii")
    err = err.decode("ascii")
    if err == "/bin/bash: rucio: command not found\n":
        print('Cannot execute rucio command. Did you forget to execute "setupATLAS" and "lsetup rucio"? Exiting.')
        sys.exit()
    if "Cannot authenticate" in err and "ERROR" in err:
        print('Cannot execute rucio command. Did you forget to create a grid proxy? Execute "voms-proxy-init -voms atlas". Exiting.')
        sys.exit()
    if err != "" and printErrorMessage:
        print("ERROR MESSAGE: "+ err)
    return out, err

def readInputDIDs(inputDIDPath):
    with open(inputDIDPath, "r") as f:
        inputDIDs = []
        for line in f:
            l = line.strip()
            if l.startswith("#") or l == "":
                continue
            inputDIDs.append(l)
    return inputDIDs

def findLocalPathsFromContainer(inputDIDs, outputFile):
    errorCount = 0
    incompleteContainerCount = 0
    missingDatasetCount = 0
    missingFileCount = 0
    currentDID = 0

    nDIDs = len(inputDIDs)
    # loop over input containers
    for inputDID in inputDIDs:
        currentDID += 1
        print("  " + str(currentDID).rjust(len(str(nDIDs))) + "/" + str(nDIDs) + ": " + inputDID)

        # find out how many datasets this container has in total
        cmd_countDatasets = "rucio list-content --short " + inputDID + " | wc -l"
        out, err = executeCommand(cmd_countDatasets)
        nDatasetsTotal = int(out)
        if debug: print("    Found " + str(nDatasetsTotal).rjust(3) + " datasets in total")

        # find out how many datasets are replicated on the grid site
        cmd_datasetListOnRSE = "rucio list-dataset-replicas --csv " + inputDID + " | grep \"" + gridSite + "\""
        out, err = executeCommand(cmd_datasetListOnRSE)
        datasets = out.strip("\n").split("\n")
        if datasets == ['']:
            datasets = []
        nDatasetsRSE = len(datasets)
        if debug: print("    Found " + str(nDatasetsRSE).rjust(3) + " datasets on " + gridSite)

        # see if they are different and try to find reason
        if nDatasetsRSE > nDatasetsTotal:
            errorCount += 1
            print(error(4) + "More datasets on " + gridSite + " (" + str(nDatasetsRSE) + ") than in total (" + str(nDatasetsTotal) + ")?! Must be an error!!!")
            print(error(4) + str(datasets))
            print(error(4) + str(nDatasetsTotal))
        elif nDatasetsRSE < nDatasetsTotal:
            # check if empty datasets are the reason
            if nDatasetsRSE == 0:
                print(warning(4) + "Fewer datasets on " + gridSite + " (" + str(nDatasetsRSE) + ") than in total (" + str(nDatasetsTotal) + ").")
                incompleteContainerCount += 1
                missingDatasetCount += nDatasetsTotal - nDatasetsRSE
            elif nDatasetsRSE > 0:
                cmd_checkForEmptyDatasets = "rucio list-dataset-replicas " + inputDID + " | grep \"DATASET\" | wc -l"
                out, err = executeCommand(cmd_checkForEmptyDatasets)
                nDatasetsTotalwoEmpty = int(out)
                nDatasetsEmpty = nDatasetsTotal - nDatasetsTotalwoEmpty

                if nDatasetsEmpty > 0:
                    print(info(4) + "There are " + str(nDatasetsEmpty) + " datasets that seem to be empty.")
                if nDatasetsRSE < nDatasetsTotalwoEmpty:
                    print(warning(4) + "Fewer datasets on " + gridSite + " (" + str(nDatasetsRSE) + ") than in total (" + str(nDatasetsTotalwoEmpty) + ").")
                    incompleteContainerCount += 1
                    missingDatasetCount += nDatasetsTotalwoEmpty - nDatasetsRSE

        allFilesOnRSE = 0
        allFilesInTotal = 0
        # loop over datasets
        for line in datasets:
            # entry 0: gridSiteName, 1: #files on this RSE, 2: #files anywhere
            dataset = line.split(",")
            # gridSiteName = dataset[0]
            filesOnRSE = int(dataset[1])
            allFilesOnRSE += filesOnRSE
            filesInTotal = int(dataset[2])
            allFilesInTotal += filesInTotal

            if filesOnRSE < filesInTotal:
                filesMissing = filesInTotal-filesOnRSE
                missingFileCount += filesMissing
                print(warning(4) + str(filesMissing) + " (of " + str(filesInTotal) + ") files are missing in a dataset.")
            elif filesOnRSE > filesInTotal:
                print("More files on this RSE than in total?! Must be an error!!!")
                print(dataset)

    cmd_getLocalPaths = "getLocalDataPath rucio list-file-replicas --pfns --rse " + gridSite + " " + " ".join(inputDIDs)
    out, err = executeCommand(cmd_getLocalPaths)
    if err != "" or out.startswith("Error"):
        print(error(2) + "Unknown error. Please investigate! Not writing file.")
        print(error(2) + err)
        print(error(2) + out)
        errorCount += 1
    else:
        with open(outputFile, "w") as fOut:
            t = time.time()
            timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            fOut.write(80*'#'+"\n")
            fOut.write('# This file was created on ' + timestamp + ' by the script discoverLocalPaths.py' + "\n")
            if errorCount > 0 or incompleteContainerCount > 0 or missingDatasetCount > 0 or missingFileCount > 0:
                fOut.write('# During execution:' + "\n")
                fOut.write('#   ' + str(errorCount) + ' errors occurred,' + "\n")
                fOut.write('#   ' + str(incompleteContainerCount) + ' containers were incomplete,' + "\n")
                fOut.write('#   ' + str(missingDatasetCount) + ' datasets were missing,' + "\n")
                fOut.write('#   ' + str(missingFileCount) + ' files were missing.' + "\n")
            fOut.write(80*'#' + "\n\n")
            fOut.write(out)
        print("  Wrote file " + outputFile)

    return errorCount, incompleteContainerCount, missingDatasetCount, missingFileCount

if __name__ == "__main__":

    errorCount = incompleteContainerCount = missingDatasetCount = missingFileCount = 0
    currentPath = 0
    nPaths = len(inputDIDPaths)
    # loop over input files containing list of containers/datasets
    for inputDIDPath in inputDIDPaths:
        currentPath += 1
        print(str(currentPath).rjust(len(str(nPaths))) + "/" + str(nPaths) + ": " + inputDIDPath)
        inputDIDs = readInputDIDs(inputDIDPath)
        dirName = "/".join(inputDIDPath.split("/")[:-1])
        outputName = "pathLists_" + inputDIDPath.split("/")[-1]
        if not dirName == "":
            outputName = dirName + "/" + outputName

        errorC = missingDatasetC = missingFileC = 0
        if DIDType == "container":
            errorC, incompleteContainerC, missingDatasetC, missingFileC = findLocalPathsFromContainer(inputDIDs, outputName)
        # elif DIDType == "dataset":
        #     errorC, missingDatasetC, missingFileC = findLocalPathsFromDataset(inputDIDs, outputName)
        # elif DIDType == "file":
        #     errorC, missingDatasetC, missingFileC = findLocalPathsFromFile(inputDIDs, outputName)
        else:
            print(error(4) + "Couldn't find the DIDType " + DIDType + ". Skipping this line!")
            errorCount += 1
            continue
        errorCount += errorC
        incompleteContainerCount += incompleteContainerC
        missingDatasetCount += missingDatasetC
        missingFileCount += missingFileC

    print("\n"+60*"=")
    if errorCount == 0:
        print("The script ran successfully!")
    else:
        print("The script ran with " + str(errorCount) + " errors.")
    if incompleteContainerCount == 0:
        pass
        # print("All containers are complete")
    else:
        print(str(incompleteContainerCount) + " containers are incomplete on " + gridSite)
    if missingDatasetCount > 0:
        print(str(missingDatasetCount) + " datasets are missing on " + gridSite)
    if missingFileCount > 0:
        print(str(missingFileCount) + " files are missing on " + gridSite)
