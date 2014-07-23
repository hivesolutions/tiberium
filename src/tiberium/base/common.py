#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Tiberium System
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Tiberium System.
#
# Hive Tiberium System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Tiberium System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Tiberium System. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import sys
import json
import shutil
import getopt
import tarfile
import tempfile
import subprocess

from tiberium.base import build
from tiberium.base import format

SEPARATORS = dict(
    nt = ";",
    default = ":"
)
""" The map defining the various path separators to
be used to start the venv environment """

VENV_PATHS = dict(
    nt = "venv\Scripts",
    default = "venv/bin"
)
""" The map defining the various paths for venv to
be used to start the venv environment """

def create_repo(path):
    # in case the path to the repository path does not exists
    # must create the complete set of directories
    if not os.path.exists(path): os.makedirs(path)

    # retrieves the current path in order to be saved and then
    # changes the current directory into the repository path
    current_path = os.getcwd()
    os.chdir(path)
    try:
        return_value = subprocess.call("git init", shell = True)
        if return_value: raise RuntimeError("Problem initializing git repository")

        return_value = subprocess.call("git config core.worktree %s" % path, shell = True)
        if return_value: raise RuntimeError("Problem configuring git repository")

        return_value = subprocess.call("git config receive.denycurrentbranch ignore", shell = True)
        if return_value: raise RuntimeError("Problem configuring git repository")
    finally:
        os.chdir(current_path)

def execute_repo(path, deploy = True):
    path = os.path.abspath(path)
    build.process_repo(path)
    build.build_sun(path)
    if deploy: build.deploy_sun(path)

def execute_sun(sun_path, temp_path = None, env = {}, sync = True):
    temp_path = temp_path or tempfile.mkdtemp()
    _tar = tarfile.TarFile(sun_path, "r")
    try: _tar.extractall(temp_path)
    finally: _tar.close()

    sun_path = os.path.join(temp_path, "sun.json")
    sun_file = open(sun_path, "r")
    try: sun = json.load(sun_file)
    finally: sun_file.close()

    procfile_path = os.path.join(temp_path, "Procfile")
    procfile = format.read_procfile(procfile_path)

    venv = sun.get("venv", False)

    current_path = os.getcwd()
    os.chdir(temp_path)

    try:
        env = dict(os.environ.items() + env.items())

        web_exec = procfile["web"]
        web_exec_l = web_exec.split()

        venv and apply_venv(temp_path, web_exec_l)

        process = subprocess.Popen(web_exec_l, shell = False, env = env)
        sync and process.wait()
    finally:
        os.chdir(current_path)
        sync and shutil.rmtree(temp_path)

    return process, temp_path

def apply_venv(temp_path, exec_list):
    os_name = os.name
    if os_name == "nt": return

    path = os.environ.get("PATH", "")

    venv_path = VENV_PATHS.get("default", "")
    venv_path = VENV_PATHS.get(os_name, venv_path)

    venv_path_abs = os.path.join(temp_path, venv_path)
    exec_list.insert(0, "PATH=%s:%s" % (venv_path_abs, path))
    exec_list.insert(0, "env")

def run():
    try:
        options, _args = getopt.getopt(sys.argv[1:], "r:s:", ["repo=", "sun="])
    except getopt.GetoptError as exception:
        print(str(exception))
        sys.exit(2)

    repo_path = None
    sun_path = None

    for option, arg in options:
        if option in ("-r", "--repo"):
            repo_path = os.path.abspath(arg)
        elif option in ("-s", "--sun"):
            sun_path = os.path.abspath(arg)

    if not sun_path == None: execute_sun(sun_path)
    if not repo_path == None: execute_repo(repo_path)

if __name__ == "__main__":
    run()
