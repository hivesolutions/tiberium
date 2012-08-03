#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Hive Tiberium System
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of  Hive Tiberium System.
#
#  Hive Tiberium System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  Hive Tiberium System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  Hive Tiberium System. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess

def create_repo(path):
    pass

def process_repo(path):
    names = os.listdir(path)

    if "requirements.txt" in names:
        current_path = os.getcwd()
        os.chdir(path)
        try:
            return_value = subprocess.call("virtualenv venv --distribute", shell = True)
            if return_value: raise RuntimeError("Problem setting the virtual environment")

            if os.name == "nt": install_command = "venv/Scripts/pip install -r requirements.txt"
            else: install_command = "venv/bin/pip install -r requirements.txt"
            return_value = subprocess.call(install_command, shell = True)
            if return_value: raise RuntimeError("Problem installing pip requirements")
        finally:
            os.chdir(current_path)

def generate_sun(path):
    """
    Generates a sun file for the provided repository
    path, the resulting file should be able to be
    distributed across nodes transparently.

    @type path: String
    @param path: The path to the repository directory to
    be used in the construction of the sun file.
    """

    base = os.path.basename(path)

    tiberium_path = os.path.join(path, "tiberium")
    sun_path = os.path.join(path, "tiberium", "%s.sun" % base)
    if os.path.exists(tiberium_path): os.remove(sun_path)
    else: os.makedirs(tiberium_path)

    _zip = zipfile.ZipFile(sun_path, "w")

    try:
        def add_sun(arg, dirname, names):
            if ".git" in names: names.remove(".git")
            if "tiberium" in names: names.remove("tiberium")

            for name in names:
                _path = os.path.join(dirname, name)
                if os.path.isdir(_path): continue
                relative_path = os.path.relpath(_path, path)
                _zip.write(_path, relative_path)

        os.path.walk(path, add_sun, None)
    finally:
        _zip.close()

def execute_sun(sun_path):
    temp_path = tempfile.mkdtemp()
    _zip = zipfile.ZipFile(sun_path, "r")
    try: _zip.extractall(temp_path)
    finally: _zip.close()

    procfile_path = os.path.join(temp_path, "Procfile")
    procfile = _read_procfile(procfile_path)

    current_path = os.getcwd()
    os.chdir(temp_path)

    try:
        web_exec = procfile["web"]
        subprocess.call(web_exec, stdout = sys.stdout, stderr = sys.stderr, shell = True)
    finally:
        os.chdir(current_path)
        shutil.rmtree(temp_path)

def _read_procfile(path):
    file = open(path, "r")
    try: contents = file.read()
    finally: file.close()

    procfile = {}

    lines = contents.split("\n")
    for line in lines:
        line = line.strip()
        if not line: continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        procfile[key] = value

    return procfile

def run():
    execute_sun("C:/tiberium.sun")

    #arg_len = len(sys.argv)
    #path = os.path.abspath(sys.argv[1]) if arg_len > 1 else os.getcwd()
    #process_repo(path)
    #generate_sun(path)

if __name__ == "__main__":
    run()
