## First Time Configurations

To set up your environment for ATLAS-specific work, add the following lines to the file `$HOME/.bashrc`

    export RUCIO_ACCOUNT=<your lxplus username>
    source /home/atlas/Tier3/AtlasUserSiteSetup.sh

Thus will set up the `setupATLAS` alias and allow you to use `rucio`.
If you plan to use the grid, install your grid certificates in your `$HOME/.globus` directory following the instructions
[here](https://ca.cern.ch/ca/Help/?kbid=024010)

## Containers

Unlike lxplus, Cedar is not set up to natively run ATLAS software. To set up an lxplus-like environment, it is necessary
to run in a containerized environment. This is done by running

    setupATLAS -c centos7+batch

This will put you in a singularity container that will give you an environment similar to that of lxplus. You can then 
run all ATLAS software as you normally would.

## Storage

Cedar is co-located with the Tier2 site 'CA-SFU-T2', which allows you to access Tier2 storage directly from the Tier3.

