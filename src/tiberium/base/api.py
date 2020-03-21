#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Tiberium System
# Copyright (c) 2008-2020 Hive Solutions Lda.
#
# This file is part of Hive Tiberium System.
#
# Hive Tiberium System is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Tiberium System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Tiberium System. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import json
import shutil
import legacy
import tarfile
import tempfile
import subprocess

import tiberium.utils

from . import repo
from . import format

SOUL_URL = "http://admin.tiberium"
""" The default URL to be used to access the
tiberium soul repository for the tiberium actions """

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

def build_sun(path):
    """
    Generates/builds a sun file for the provided repository
    path, the resulting file should be able to be distributed
    across nodes transparently.

    This building operation will start by processing the repo
    directory so that the files are ready for building.

    :type path: String
    :param path: The path to the repository directory to
    be used in the construction of the sun file.
    :rtype: String
    :return: The path of the sun file that has just been generated
    from the provided repository (ready for usage).
    """

    repo.process_repo(path)

    path = os.path.abspath(path)
    base = os.path.basename(path)
    base = base.rstrip(".git")
    tiberium_path = os.path.join(path, "tiberium")
    sun_path = os.path.join(tiberium_path, "%s.sun" % base)
    if os.path.exists(tiberium_path): os.path.exists(sun_path) and os.remove(sun_path)
    else: os.makedirs(tiberium_path)

    _tar = tarfile.TarFile(sun_path, "w")

    sun = dict(
        name = base,
        venv = repo.has_requirements(path)
    )

    buffer = legacy.StringIO()
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

        legacy.walk(path, add_sun, None)
    finally:
        _tar.close()

    repo.cleanup_repo(path)

    return sun_path

def upload_sun(path = None, base_url = SOUL_URL):
    if path == None: path = tiberium.utils.local_sun()
    path = os.path.abspath(path)
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

def run_sun(path = None, temp_path = None, env = {}, sync = True):
    if path == None: path = tiberium.utils.local_sun()

    temp_path = temp_path or tempfile.mkdtemp()
    _tar = tarfile.TarFile(path, "r")
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

        venv and repo.apply_venv(web_exec_l, env)

        process = tiberium.utils.command(
            web_exec_l,
            shell = True,
            env = env,
            wait = sync
        )
    finally:
        os.chdir(current_path)
        sync and shutil.rmtree(temp_path)

    return process, temp_path
