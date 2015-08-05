#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Tiberium System
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import legacy
import mimetypes

BOUNDARY = "----------BnB31YzM9ukx7cEMCbBbEPUPR8Dwek8LEYyK7xVxm2zbixgeqQS8d7WkXYNUsUWM_$"
""" The boundary value to be used in the multipart
message as the separator between items """

def post_multipart(url, fields = (), files = ()):
    url_parsing = legacy.urlparse(url)
    host = url_parsing.hostname
    port = url_parsing.port
    path = url_parsing.path
    return _post_multipart(host, port, path, fields, files)

def _post_multipart(host, port = 80, path = "/", fields = (), files = ()):
    content_type, body = _encode_multipart(fields, files)
    http_client = legacy.HTTPConnection(host, port)
    http_client.putrequest("POST", path)
    http_client.putheader("content-type", content_type)
    http_client.putheader("content-length", str(len(body)))
    http_client.endheaders()
    http_client.send(body)
    http_client.getreply()
    return http_client.file.read()

def _encode_multipart(fields, files):
    buffer = []
    for (key, value) in fields:
        buffer.append("--" + BOUNDARY)
        buffer.append("Content-Disposition: form-data; name=\"%s\"" % key)
        buffer.append("")
        buffer.append(value)
    for (key, filename, value) in files:
        buffer.append("--" + BOUNDARY)
        buffer.append("Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" % (key, filename))
        buffer.append("Content-Type: %s" % _get_content_type(filename))
        buffer.append("")
        buffer.append(value)
    buffer.append("--" + BOUNDARY + "--")
    buffer.append("")
    body = "\r\n".join(buffer)
    content_type = "multipart/form-data; boundary=%s" % BOUNDARY
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"
