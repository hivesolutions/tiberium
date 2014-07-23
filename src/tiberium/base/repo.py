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
import subprocess

VENV_PATHS = dict(
    nt = "venv\Scripts",
    default = "venv/bin"
)
""" The map defining the various paths for venv to
be used to start the venv environment """

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

def apply_venv(temp_path, exec_list):
    os_name = os.name
    if os_name == "nt": return

    path = os.environ.get("PATH", "")

    venv_path = VENV_PATHS.get("default", "")
    venv_path = VENV_PATHS.get(os_name, venv_path)

    venv_path_abs = os.path.join(temp_path, venv_path)
    exec_list.insert(0, "PATH=%s:%s" % (venv_path_abs, path))
    exec_list.insert(0, "env")