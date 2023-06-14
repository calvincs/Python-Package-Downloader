#!/usr/bin/env python3

####################################################################################################
# This script downloads Python packages and their dependencies specified in a requirements.txt file.
# It can automatically detect whether your system uses pip or pip3, and utilizes the appropriate command.
# It requires a Python version, a list of platforms and a directory to download the packages to be specified by the user.
# It downloads both the default packages (Cython, wheel, setuptools) and those specified in the requirements.txt file.
# The script also checks the existence of the requirements file and raises an error if it is not found.
#
# Usage:
# python3 main.py -r requirements.txt -d ./packages -t system.tags
#
# The above command will download the packages and dependencies specified in requirements.txt 
#  for any Python version and platform listed in system.tags file.
# and store them in the ./packages directory.
#
# In the download process, the script prioritizes binary packages for the specified Python version and platforms.
# If the binary packages are not found, it defaults to download the source packages.
#
# The script can also print out current system information, including platform, 
# Python version, pip version, and an example command to execute the script.
# 
# The script requires Python 3.6 or higher.
# May also require package 'packaging' to be installed.
#
####################################################################################################

import os
import subprocess
import glob
import argparse
import pip
import sys
import platform
from packaging import tags as otags


def get_pip_command():
    """
    Get the pip command to use. If pip is not found, try pip3.
    If neither is found, raise an exception.

    Returns:
        str: The pip command to use.
    """
    try:
        subprocess.check_call(['pip', '--version'])
        return 'pip'
    except FileNotFoundError:
        pass

    try:
        subprocess.check_call(['pip3', '--version'])
        return 'pip3'
    except FileNotFoundError:
        raise Exception("Neither pip nor pip3 was found on this system.")
    

def read_tags_and_versions(tags_file='system.tags'):
    """
    Read system tags from file and convert interpreters into version numbers.

    Returns:
        list: List of system tags as (version, abi, platform) tuples.
    """
    try:
        with open(tags_file, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            tags = []
            for line in lines:
                parts = line.split('-')
                if len(parts) == 3:
                    interpreter, abi, platform = parts
                    if interpreter.startswith("cp") or interpreter.startswith("py"):
                        version = interpreter[2:]
                    else:
                        raise ValueError(f"Unexpected interpreter format: {interpreter}")
                    tags.append((version, abi, platform))
                else:
                    print(f"Failed to parse line {line} as a tag.")
            return tags
    except FileNotFoundError:
        print("System tags file not found. Please run with -i flag first to generate it.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to read system tags. Error: {e}")
        sys.exit(1)


def download_package(package, tags, pip_command, download_folder):
    """
    Attempt to download the package for each tag. If unsuccessful, log the error and continue.

    Args:
        package (str): Name of the package to download.
        tags (list): List of system tags as (version, abi, platform) tuples.
        pip_command (str): Command for pip.
        download_folder (str): Directory to download the packages to.
    """
    for tag in tags:
        version, abi, platform = tag
        command = [
            pip_command, 'download',
            package,
            '--python-version', version,
            '--platform', platform,
            '--abi', abi,
            '--only-binary=:all:',
            '-d', download_folder,
        ]
        try:
            subprocess.check_call(command)
            return
        except subprocess.CalledProcessError:
            print(f"Failed to download binary for package {package} with tag {tag}, trying next tag.")
            continue  # If package download failed, try the next tag

    # If failed to download binary, try to download source without tag filters
    command = [pip_command, 'download', package, '-d', download_folder]
    try:
        subprocess.check_call(command)
        return
    except subprocess.CalledProcessError:
        pass  # If still failed, log it and continue

    # Log the failed package
    with open('download_errors.log', 'a') as log_file:
        log_file.write(f"Failed to download binary and source for package {package}.\n")


def download_packages(requirements_file, download_folder, tags_file='system.tags'):
    """
    Download packages and dependencies specified in a requirements.txt file.

    Args:
        requirements_file (str): Path to the requirements.txt file.
        download_folder (str): Directory to download the packages to.

    Returns:
        None
    """
    pip_command = get_pip_command()
    default_packages = ["Cython", "wheel", "setuptools"]

    # Read system tags and versions
    system_tags = read_tags_and_versions(tags_file=tags_file)

    for package in default_packages:
        download_package(package, system_tags, pip_command, download_folder)

    # Download packages specified in the requirements file.
    with open(requirements_file, 'r') as req_file:
        packages = req_file.readlines()

    for package in packages:
        package = package.strip()
        download_package(package, system_tags, pip_command, download_folder)


def create_local_requirements_file(download_folder):
    """
    Create a local_requirements.txt file that can be used to install the downloaded packages.

    Args:
        download_folder (str): Directory where the packages were downloaded to.

    Returns:
        None
    """
    try:
        wheels = glob.glob(os.path.join(download_folder, '*.whl'))
        with open('local_requirements.txt', 'w') as f:
            for wheel in wheels:
                line = './' + os.path.relpath(wheel) + '\n'
                f.write(line)

    except Exception as e:
        print(f"Failed to create local_requirements.txt file. Error: {e}")
        sys.exit(1)


def get_current_system_info():
    """
    Get the current system information and print it to the console.
    Also generates a system.tags file that can be used to download packages matching the current system.

    Returns:
        None
    """
    try:
        system_platform = platform.system().lower()
        python_version = "".join(map(str, sys.version_info[:2]))
        pip_version = pip.__version__

        print(f"Your current system information is:")
        print(f"Platform: {system_platform}")
        print(f"Python version: {python_version}")
        print(f"Pip version: {pip_version}")

        print("\nAn example command to run this script could be:")
        print(f"python3 main.py -r requirements.txt -d ./packages")

        # Get the current system tags
        python_version_interpreter = f"cp{sys.version_info.major}{sys.version_info.minor}"
        python_version_abi = f"cp{sys.version_info.major}{sys.version_info.minor}m" if sys.version_info.major == 2 else f"cp{sys.version_info.major}{sys.version_info.minor}"
        system_arch = platform.machine()
        filtered_tags = set()

        for tag in otags.sys_tags():
            if (python_version_interpreter in str(tag) or python_version_abi in str(tag)) and system_arch in str(tag):
                filtered_tags.add(tag)

        print("Number of filtered tags found: ", len(filtered_tags))

        # Write tags to a file
        print("Attempting to write system tags to file system.tags...")
        with open('system.tags', 'w') as f:
            for tag in list(filtered_tags):
                f.write(str(tag) + '\n')

        print("Writing to file completed.")

    except Exception as e:
        print(f"Failed to get current system information. Error: {e}")
        sys.exit(1)


def main():
    """
    Main function.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Download packages and dependencies specified in a requirements.txt file.')
    parser.add_argument('-r', '--requirements', help='Path to the requirements.txt file.')
    parser.add_argument('-d', '--directory', help='Directory to download the packages to.')
    parser.add_argument('-i', '--info', action='store_true', help='Get current system information, generate system.tags file, and print an example command for use.')
    parser.add_argument('-t', '--tags', help="Path to the system.tags file. If not specified, the 'system.tags' file in the current directory will be used.")

    args = parser.parse_args()

    if args.info:
        get_current_system_info()
        return

    if not all([args.requirements, args.directory]):
        parser.error("The -r, and -d options are required unless using the -i option.")
    
    # Validate that the requirements file exists
    if not os.path.isfile(args.requirements):
        parser.error(f"The file {args.requirements} does not exist.")

    os.makedirs(args.directory, exist_ok=True)

    if args.tags:
        tags_file = 'system.tags' if not args.tags else args.tags
        if not os.path.isfile(tags_file):
            parser.error(f"The file {tags_file} does not exist.")
    download_packages(args.requirements, args.directory)
    create_local_requirements_file(args.directory)
    print(f"Successfully downloaded packages to {args.directory}.")
    print("Example usage to perform installation of local packages:")
    print(f"\tpip install -r requirements.txt --find-links {args.directory} --no-index")
    print("The '--find-links' option in pip allows you to specify one or more directories or URLs where the package manager should look for package distributions instead of PyPI.")
    print("The '--no-index' option in pip prevents the package manager from searching in remote indexes (PyPI) and only considers locally available packages.")


if __name__ == '__main__':
    main()