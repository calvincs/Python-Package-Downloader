# Python Package Downloader

Python Package Downloader is a command line tool that downloads Python packages and their dependencies specified in a `requirements.txt` file. The tool automatically detects whether your system uses pip or pip3, and uses the appropriate commands for package management to download the required packages. 

It requires the user to specify a tags file which is a list of system and a directory to download the packages. The tool not only downloads the packages specified in the `requirements.txt` file but also the default packages (Cython, wheel, setuptools) and packages dependencies.

The tool downloads binary packages for the specified Python version(s) and platform(s) listed in the `system.tags` file. If the binary packages are not found, it falls back to download the source packages. 

Python Package Downloader also has the ability to print out current system information, including platform, Python version, pip version, and an example command to execute the script.

This tool is especially useful for downloading Python packages for system(s) that are not connected to the internet. You can download the required packages and their dependencies on a system with internet access, and transfer them to the offline system and then install them.


**Requirements:**
- python >= 3.6
- packaging >= 23.1

## Usage

Here is how to use the script:

1. You need to have the tags for the given system(s) you are going to gather offline packages for. You can accomplish this by executing this script on that machine or a machine matching the python version, system archetecture, and OS version.

    ```bash
    user@desktop:~/$ ./main.py -i
    Your current system information is:
    Platform: linux
    Python version: 310
    Pip version: 23.1.2

    An example command to run this script could be:
    python3 main.py -r requirements.txt -d ./packages
    Number of filtered tags found:  105
    Attempting to write system tags to file system.tags...
    Writing to file completed.
    ```

2. You now can take the created `system.tags` file and the `requirements.txt` and execute the following:

    ```bash
    python3 main.py -r requirements.txt -d ./packages -t system.tags
    ```

    This command will download the packages and dependencies specified in `requirements.txt` for any Python version and platform listed in `system.tags` file and store them in the `./packages` directory.

    - This process may take some time to complete.


3. You will want to verify that all the packages you need for offline installation are present.  You can do this by simulating an offline installation.  

    - Create a virtual environment
    - Activate virtual environment
    - Do a pip install offline, using ony the packages in your ./package directory:

    ```bash
    pip install -r requirements.txt --find-links ./packages --no-index
    ```
    * Note that the machine where you are doing the test/validation should match the system.tags you used to initially build the packages


## Install Offline Requirements

After successfully downloading packages to a specified directory, use the following command to perform installation of local packages on the offline machine:

```bash
pip install -r requirements.txt --find-links ./packages --no-index
```

- The `--find-links` option in pip allows you to specify one or more directories or URLs where the package manager should look for package distributions instead of PyPI.

- The `--no-index` option in pip prevents the package manager from searching in remote indexes (PyPI) and only considers locally available packages.


## License

MIT License

Copyright (c) 2023 Calvin Schultz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
