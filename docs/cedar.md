## Logging in to Cedar

To ssh into the Cedar login node, run

    ssh -Y [username]@cedar.computecanada.ca

where `[username]` is your SFU computing ID.

## Directories

Cedar has several storage spaces or filesystems and you should ensure that you are using the right space for the right
task. 

* HOME: While your home directory may seem like the logical place to store all your files and do all your work, in general this isn't the case - your home normally has a relatively small quota and doesn't have especially good performance for the writing and reading of large amounts of data. The most logical use of your home directory is typically source code, small parameter files and job submission scripts.
* PROJECT: The project space has a significantly larger quota and is well-adapted to sharing data among members of a research group since it, unlike the home or scratch, is linked to a professor's account rather than an individual user. The data stored in the project space should be fairly static, that is to say the data are not likely to be changed many times in a month. Otherwise, frequently changing data - including just moving and renaming directories - in project can become a heavy burden on the tape-based backup system.
* SCRATCH: For intensive read/write operations on large files (> 100 MB per file), scratch is the best choice. Remember however that important files must be copied off scratch since they are not backed up there, and older files are subject to purging. The scratch storage should therefore be used for temporary files: checkpoint files, output from jobs and other data that can easily be recreated.

See [here](https://docs.alliancecan.ca/wiki/Storage_and_file_management#Storage_types) and
[here](https://docs.alliancecan.ca/wiki/Cedar#Storage) for more details.

## Resource intensive work

The interactive login nodes (and containers started from them) are meant for light work such as compiling and running a
quick test job and for submitting to the batch system. Performing resource intensive tasks on these nodes can cause
issues for other users and is forbidden. All resource intensive tasks must use the batch system.

### Submitting batch jobs

Cedar uses the [SLURM](https://slurm.schedmd.com/documentation.html) job scheduler to manage batch jobs. See
[here](https://docs.alliancecan.ca/wiki/Running_jobs) for a guide.

### Interactive work

If you need to do resource-intensive interactive work, you will need to get a resource allocation using the schedule.
To do this, you can run (for example)

    salloc --time=16:0:0 --mem-per-cpu=32G --cpus-per-task=1 --account=ctb-stelzer --nodelist=cdr1642

This will request a single CPU for 16 hours, with 32Gb of memory. You may need to replace `ctb-stelzer` with the name 
of the user that sponsored your account.


