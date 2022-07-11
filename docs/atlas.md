## First Time Configurations

To set up your environment for ATLAS-specific work, add the following lines to the file `$HOME/.bashrc`

    export RUCIO_ACCOUNT=<your lxplus username>
    source /home/atlas/Tier3/AtlasUserSiteSetup.sh

Thus will set up the `setupATLAS` alias and allow you to use `rucio`.
If you plan to use the grid, install your grid certificates in your `$HOME/.globus` directory following the instructions
[here](https://ca.cern.ch/ca/Help/?kbid=024010).

## Containers

Unlike lxplus, Cedar is not set up to natively run ATLAS software. To set up an lxplus-like environment, it is necessary
to run in a containerized environment. This is done by running

    setupATLAS -c centos7+batch

This will put you in a singularity container that will give you an environment similar to that of lxplus. You can then 
run all ATLAS software as you normally would.

### Submitting batch jobs

You can submit and access the batch queues from inside your interactive container session.  For example, if you type

    setupATLAS -c centos7+batch

you can next generate a script to submit to the batch system. eg.

    batchScript "source <somepath in container>/myJob.sh" -o submitMyJob.sh

(The above will create a file `submitMyJob.sh` that will run `myJob.sh` inside the same type of container you are on now
but on the batch queue.

## Storage

Cedar is co-located with the Tier2 site 'CA-SFU-T2', which allows you to access Tier2 storage directly from the Tier3.

### Requesting Rucio rules

Each user has a 5Tb quota on the `CA-SFU-T2_LOCALGROUPDISK` grid site. To request replication of a dataset to this site,
see [here](https://rucio-ui.cern.ch/r2d2/request) (note: requires installing your grid certificate in your browser).

### Finding the local files

A [script](https://github.com/jburzy01/SFUCedarDocs/blob/main/scripts/discoverLocalPaths.py) is provided to determine
the file paths using the rucio file checksum. Usage:

    python discoverLocalPaths.py dsidList1.txt ... dsidListN.txt

where `dsidListX.txt` is a text file containing a list of rucio datasets that you which to locate. For each
`dsidListX.txt`, this script will output a file `pathLists_dsidListX.txt` which contains the local paths to 
all of the files in the input datasets. 
