#!/usr/bin/env python
#coding: utf-8
#
# Copyright (c) 2009, Andrea Barberio <insomniac@slackware.it>
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Slackware Linux Project Italia nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

import os
import sys
import re
import gzip
import tempfile
try:
	import chardet
except ImportError:
	print "You need python-chardet in order to use charset detection"
	sys.exit(1)


_use_unicode = True
INPUT_ENCODING = 'iso-8859-15'		# Default input (.bgl) encoding
DEFAULT_OUTPUT_ENCODING = 'utf-8'	# Default output encoding
OUTPUT_ENCODING = 'utf-8'		# Output encoding
ERRORS = 'xmlcharrefreplace'		# what to do when a decoding error occurs
DEFAULT_LANGUAGE = 'en-us'		# Default language for the dictionary for opf/mobi files
DEFAULT_INPUT_LANGUAGE = 'en-us'	# Default input language for opf/mobi files
DEFAULT_OUTPUT_LANGUAGE = 'en-us'	# Default output language for opf/mobi files
DEFAULT_COMPRESSION_LEVEL = u'0'	# Default compression level for mobi files
DEFAULT_SECURITY_LEVEL = u'0'		# Default security level for mobi files


LOGFILE = os.path.join(os.getcwd(), 'qtbglconverter.log')

# EventEmitter, Logger, LogDumper and QLogViewer by Giuseppe Coviello <cjg@cruxppc.org>
class EventEmitter(object):
	def __init__(self, signals):
		self._signals = signals
		self._handlers = {}

	def connect(self, signal, handler):
		try:
			handlers = self._handlers[signal]
		except KeyError:
			self._handlers[signal] = []
			handlers = self._handlers[signal]
		handlers.append(handler)

	def disconnect(self, signal, handler):
		self._handlers[signal].remove(handler)

	def emit(self, signal, *args):
		for i in self._handlers[signal]:
			i(self, args)

class Logger(EventEmitter):
	def __init__(self):
		EventEmitter.__init__(self, ["logline"])

	def write(self, line):
		self.emit("logline", line)

class LogDumper:
	def __init__(self, logger):
		logger.connect("logline", self.dumpline)

	def dumpline(self, emitter, args):
		print args[0]

class LogWriter:
	def __init__(self, logger, filename):
		logger.connect("logline", self.writeline)
		self._file = file(filename, "w")

	def __del__(self):
		self._file.close()

	def writeline(self, emitter, args):
		self._file.write("%s\n" % args[0])


@property
def use_unicode(value=None):
	"""Setter/Getter for the `use_unicode' pseudovariable"""
	if value is None:
		return _use_unicode
	else:
		_use_unicode = value
		if value == True:
			OUTPUT_ENCODING = 'utf-8'
		else:
			OUTPUT_ENCODING = INPUT_ENCODING


def dec(buf, encoding=None):
	"""Decode any buffer into unicode"""
	if not use_unicode:
		return buf
	if isinstance(buf, unicode):
		return buf
	if encoding is None:
		enc = INPUT_ENCODING
	elif encoding == 'detect':
		enc = chardet.detect(buf)['encoding']	# use this for autodetection. Not deterministic
	else:
		enc = encoding
	return unicode(buf, encoding=enc, errors=ERRORS)


def enc(buf, encoding='utf-8'):
	"""Encode any buffer into the given encoding"""
	if not use_unicode:
		return buf
	if isinstance(buf, unicode):
		return buf.encode(encoding)
	return buf

def uncomment(buf):
	"""Strip blank lines and comments from a string representing the content of
	a file, and return a list of meaningful and delightful lines"""
	lines = []
	pattern = re.compile('^ *#|^ *$')
	for line in buf.splitlines():
		if not re.match(pattern, line):
			lines.append(line)
	return lines


def unpack(bglfd, options):
	"""Extract the .gzip file reading from the given file descriptor (which
	represents the BGL file), save it and return the uncompressed buffer"""
	options['logger'].write('Unpacking BGL file..')
        gzipfile = tempfile.mktemp()
	try:
		buf = bglfd.read()
		offset = (ord(buf[4]) << 16) + ord(buf[5])
                open(gzipfile, 'wb').write(buf[offset:])
		compressed = gzip.open(gzipfile)
		buf = compressed.read()
		compressed.close()
	except (OSError, IOError), msg:
		options['logger'].write(str(msg))
	return buf


def get_filters(filter_names):
	"""Build up filters list containing filter function references, given a list
	of strings with the names of the filters. The method returns both a list of
	valid filters, and a list of invalid ones"""
	filters = []
	bad_filters = []
	if filter_names is not None:
		for filter in filter_names:
			try:
				f = getattr(__import__('filters.%s' % filter, fromlist=['filter']), 'filter')
				if callable(f):
					filters.append((f, filter))
				else:
					bad_filters.append(filter)
			except (ImportError, AttributeError):
				bad_filters.append(filter)
	return filters, bad_filters


