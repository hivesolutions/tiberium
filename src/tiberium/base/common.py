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

import sys

from . import api

def build(path = "."):
    api.build_sun(path)

def upload(path = None):
    api.upload_sun(path)

def run(path = None):
    api.run_sun(path)

def main():
    if len(sys.argv) < 2: raise RuntimeError("operation not defined")
    operation = sys.argv[1]
    function = globals().get(operation, None)
    if function: function(*sys.argv[2:])
    else: raise RuntimeError("invalid operation")

if __name__ == "__main__":
    main()
else:
    __path__ = []
