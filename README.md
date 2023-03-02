# Directory Cleanup

An easy-to-setup docker image that automatically removes files in a mounted directory that are too old. 

## Get Started

Pull and run the image usnig:

```shell
docker run -d \
	-v {WATCH_DIR}:/watch `# Required` \
	-v {TRASH_DIR}:/trash `# Optional if "move_to_trash" is set to false` \
	-v {DATA_DIR}:/app/data `# For configuration` \
	--name="directory-cleanup" \
	--restart=unless-stopped \
	ykozxy/directory-cleanup
```

Once started, the image will start monitor all files/directories in the provided `WATCH_DIR`, and delete files/directories if it exists in the folder too long (default is 45 days). 

A possible usage is to automatically keep your download folder clean by removing old files. 

## Configuration

The configuration file can be found in the `DATA_DIR` directory: `{DATA_DIR}/config.json`. 

* `move_to_trash` (default = `false`): When set to true, old files will be moved to `TRASH_DIR` instead of calling `rm`. This is useful if `TRASH_DIR` is mounted to the trash folder of the host machine. A caveat here is: the `TRASH_DIR` must be mounted when this field is set to true, or the outdated files will NOT BE DELETED but KEEP IN THE IMAGE for eternal. 
* `max_keep_days` (default = `45`): The max number of the days to keep a file/directory before automatically deleting them.  
* `exclude`: A list of files/directories to be excluded from monitering and deletion. 
