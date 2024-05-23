#!/usr/bin/env python3
import io
import os
import subprocess
from setuptools import setup, find_packages, Command
from distutils.dir_util import remove_tree
import sys

MODULE_NAME = "binwalk"
MODULE_VERSION = "2.3.2"
SCRIPT_NAME = MODULE_NAME
MODULE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# If this version of binwalk was checked out from the git repository,
# include the git commit hash as part of the version number reported by binwalk.
try:
    label = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
    ).decode("utf-8")
    MODULE_VERSION = "%s+%s" % (MODULE_VERSION, label.strip())
except KeyboardInterrupt as e:
    raise e
except Exception:
    pass


def which(command):
    # Handling for different platforms
    usr_local_bin = os.path.join(os.path.sep, "usr", "local", "bin", command)
    location = None
    try:
        location = (
            subprocess.Popen(
                ["where" if os.name == "nt" else "which", command],
                shell=False,
                stdout=subprocess.PIPE,
            )
            .communicate()[0]
            .strip()
            .decode("utf-8")
        )
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        pass

    if not location and os.path.exists(usr_local_bin):
        location = usr_local_bin

    return location


def find_binwalk_module_paths():
    paths = []
    try:
        import binwalk

        paths = binwalk.__path__
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        pass
    return paths


def remove_binwalk_module(pydir=None, pybin=None):
    if pydir:
        module_paths = find_binwalk_module_paths()
        for path in module_paths:
            if path.startswith(pydir):
                print(f"removing '{path}'")
                remove_tree(path)

    if pybin:
        script_path = os.path.join(pybin, SCRIPT_NAME)
        if os.path.exists(script_path):
            print(f"removing '{script_path}'")
            os.remove(script_path)


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system(
            "rd /s /q build dist *.pyc *.tgz *.egg-info"
            if os.name == "nt"
            else "rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info"
        )


class UninstallCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        remove_binwalk_module(pydir=sys.prefix, pybin=os.path.dirname(sys.executable))


# The data files to install along with the module
install_data_files = [
    f"{data_dir}{os.path.sep}*"
    for data_dir in ["magic", "config", "plugins", "modules", "core"]
]

this_directory = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=MODULE_NAME,
    version=MODULE_VERSION,
    description="Firmware analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Craig Heffner",
    url=f"https://github.com/dspencej/{MODULE_NAME}",  # Updated URL
    python_requires="==3.11.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={MODULE_NAME: install_data_files},
    scripts=[os.path.join("src", "scripts", SCRIPT_NAME)],
    cmdclass={"clean": CleanCommand, "uninstall": UninstallCommand},
)
