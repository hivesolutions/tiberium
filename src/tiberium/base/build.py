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
import json
import tarfile
import cStringIO
import subprocess

import tiberium.utils

SOUL_URL = "http://admin.tiberium"
""" The default url to be used to access the
tiberium soul repository for the tiberium actions """

def build_sun(path):
    """
    Generates/builds a sun file for the provided repository
    path, the resulting file should be able to be distributed
    across nodes transparently.

    @type path: String
    @param path: The path to the repository directory to
    be used in the construction of the sun file.
    """

    base = os.path.basename(path)
    base = base.rstrip(".git")
    tiberium_path = os.path.join(path, "tiberium")
    sun_path = os.path.join(tiberium_path, "%s.sun" % base)
    if os.path.exists(tiberium_path): os.path.exists(sun_path) and os.remove(sun_path)
    else: os.makedirs(tiberium_path)

    _tar = tarfile.TarFile(sun_path, "w")

    sun = dict(
        name = base,
        venv = has_requirements(path)
    )

    buffer = cStringIO.StringIO()
    json.dump(sun, buffer)
    buffer_size = buffer.tell()
    buffer.seek(0)

    tar_info = tarfile.TarInfo("sun.json")
    tar_info.size = buffer_size
    _tar.addfile(tar_info, buffer)

    try:
        def add_sun(arg, dirname, names):
            if ".git" in names: names.remove(".git")
            if "tiberium" in names: names.remove("tiberium")

            for name in names:
                _path = os.path.join(dirname, name)
                if os.path.isdir(_path): continue
                relative_path = os.path.relpath(_path, path)
                _tar.add(_path, relative_path)

        os.path.walk(path, add_sun, None)
    finally:
        _tar.close()

def deploy_sun(path, base_url = SOUL_URL):
    base = os.path.basename(path)
    base = base.rstrip(".git")
    tiberium_path = os.path.join(path, "tiberium")
    sun_path = os.path.join(tiberium_path, "%s.sun" % base)
    sun_file = open(sun_path, "rb")
    try: sun_contents = sun_file.read()
    finally: sun_file.close()
    tiberium.utils.post_multipart(
        base_url + "/deploy",
        (("name", base),),
        (("file", base, sun_contents),)
    )

def process_repo(path):
    if has_requirements(path): process_requirements(path)

def process_requirements(path):
    current_path = os.getcwd()
    os.chdir(path)
    try:
        _has_venv = has_venv(path)
        return_value = subprocess.call("virtualenv venv --distribute", shell = True) if not _has_venv else 0
        if return_value: raise RuntimeError("Problem setting the virtual environment")

        if os.name == "nt": install_command = "venv/Scripts/pip install -r requirements.txt"
        else: install_command = "venv/bin/pip install -r requirements.txt"
        return_value = subprocess.call(install_command, shell = True)
        if return_value: raise RuntimeError("Problem installing pip requirements")
    finally:
        os.chdir(current_path)
        
def has_requirements(path):
    names = os.listdir(path)
    return "requirements.txt" in names

def has_venv(path):
    names = os.listdir(path)
    return "venv" in names
