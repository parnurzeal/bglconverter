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
#
# This tool unpacks a BGL (babylon dictionary) file and converts it into OPF
# (keeping the resources), suitable for further conversion with 'mobigen_linux`
# or the corresponding Windows version. If you don't know what MobiPocket is,
# check http://www.mobipocket.com/.
#
# Some code based on tab2opf.py and the reversing located at
# http://www.woodmann.com/forum/archive/index.php/t-7028.html.
# Encoding detection by chardet (http://chardet.feedparser.org/).
#
# I usually prefer to use an XML library, but for the simplicity of the
# XML files I need to generate, I think it's better not to have an external
# dependancy such as lxml.
#
# TODO: Multithreading for all the conversion stages.
#

import os
import sys
import shutil
import getopt
import subprocess
from cStringIO import StringIO
import lib.utils
from lib.utils import *
from lib.languages import *
try:
	import psyco
	psyco.full()
except ImportError:
	pass


DEBUG = False
MAX_DEFS = 1000
VALID_CHARS = "abcdefghijklmnopqrstuvwxyz 0123456789!@#$%&8()_-+=|{}[]<>\"',.%%/\\:;!?"

class MakeDirsException(Exception):
	pass

def usage():
	print """Usage: %s [options] -o <ubgl|dic|opf|mobi> <file.bgl|file.dic|file.opf>
\tOptions:
\t-o\t\t\tOutput format. Can be one of ubgl, dic, opf or mobi.
\t--filters\t\tFilters to apply to the content. Valid only if the input file is a .bgl.
\t--list-filters\t\tShow all the available filters and their description.
\t--outdir\t\tOutput directory where to store the temporary and the final data. If omitted, fall back to CWD + dictionary name.
\t-n|--no-unicode\t\tDon't use Unicode for encoding. This option will preserve the original encoding.
\t--language\t\tSet the dictionary language.
\t--input-language\tSet the input language for the dictionary. It should be an international code
\t\t\t\t(e.g. en-us, it). Works with -o mobi or -o opf only.
\t--output-language\tSame as --input-language, but for the output language. For -o mobi and -o opf only.
\t--list-languages\tShow the list of supported languages.
 \t--cover\t\tSet the cover for the dictionary. Works only with -o mobi.
\t-c\t\t\tCompression. Set the compression level of the output dictionary. Can be 0, 1 or 2. Default is %s. Works only with -o mobi.
\t-s\t\t\tSecurity level. Can be 0, 1 or 2. Default is %s. Works only with -o mobi.
\t-h\t\t\tThis help.""" % (sys.argv[0], DEFAULT_COMPRESSION_LEVEL, DEFAULT_SECURITY_LEVEL)

	sys.exit(1)


def build_definitions(fd):
	"""Build a list of definitions, reading from the given file descriptor,
	where each element is a tuple like ('name', 'definition'). `filters' must
	be a list of function references."""
	fd.seek(0)
	buf = fd.read()
	ret = []
	lines = uncomment(buf)
	while len(lines) > 1:
		if len(lines) < 2:
			break
		term = lines.pop(0)
		definition = lines.pop(0)
		ret.append((dec(term, 'utf-8'), dec(definition, 'utf-8')))
	return ret


def create_html(definitions, options):
	"""Build an xml tree suitable for MobiPocket from the given definitions list"""
	HEAD = u"""<?xml version="1.0" encoding="%s"?>
<html xmlns:idx="www.mobipocket.com" xmlns:mbp="www.mobipocket.com" xmlns:xlink="http://www.w3.org/1999/xlink">
  <body>
    <mbp:pagebreak/>
    <mbp:frameset>
      <mbp:slave-frame display="bottom" device="all" breadth="auto" leftmargin="0" rightmargin="0" bottommargin="0" topmargin="0">
        <div align="center" bgcolor="yellow"/>
        <a onclick="index_search()">Dictionary Search</a>
        </div>
      </mbp:slave-frame>
      <mbp:pagebreak/>
""" % OUTPUT_ENCODING
	DEFINITION = u"""
      <idx:entry name="word" scriptable="yes">
        <h2>
          <idx:orth>%s</idx:orth><idx:key key="%s">
        </h2>
          %s
      </idx:entry>
      <mbp:pagebreak/>
"""
	TAIL = u"""
    </mbp:frameset>
  </body>
</html>
"""


	i = 0
	fd = False
	for term, definition in definitions:
		if i % MAX_DEFS == 0:
			if fd:
				fd.write(enc(TAIL))
				fd.close()
			outfile = dec(os.path.join(options['outdir'], options['basename'] + '.' + str(i/MAX_DEFS) + '.html'))
                        fd = open(outfile, 'wb')
			fd.write(enc(HEAD))
		entry = DEFINITION % (term, term, definition)
		fd.write(enc(entry))
		i += 1
	if fd:
		fd.write(enc(TAIL))
	return i/MAX_DEFS


def create_opf(options, count):
	"""Create the OPF file"""
	OPF_HEAD1 = u'''<?xml version="1.0" encoding="''' + OUTPUT_ENCODING + '''"?>
<!DOCTYPE package SYSTEM "oeb1.ent">

<!-- the command line instruction 'prcgen dictionary.opf' will produce the dictionary.prc file in the same folder-->
<!-- the command line instruction 'mobigen dictionary.opf' will produce the dictionary.mobi file in the same folder-->

<package unique-identifier="uid" xmlns:dc="Dublin Core">

<metadata>
        <dc-metadata>
                <dc:Identifier id="uid">%s</dc:Identifier>
                <!-- Title of the document -->
                <dc:Title><h2>%s</h2></dc:Title>
                <dc:Language>%s</dc:Language>
	</dc-metadata>
	<meta name="cover" content="cover-image" />
        <x-metadata>
'''

	OPF_HEAD2 = u"""
                <DictionaryInLanguage>%s</DictionaryInLanguage>
                <DictionaryOutLanguage>%s</DictionaryOutLanguage>
                <EmbeddedCover>%s</EmbeddedCover>
        </x-metadata>
</metadata>

<!-- list of all the files needed to produce the .prc file -->
<manifest>
"""

	OPF_THEAD = u"""              <output encoding="Windows-1252" flatten-dynamic-dir="yes"/>"""

	OPF_TLINE = u"""	<item id="dictionary%d" href="%s.%d.html" media-type="text/x-oeb1-document"/>
"""

	OPF_TMIDDLE = u"""</manifest>


<!-- list of the html files in the correct order  -->
<spine>
"""

	OPF_TLREF = u"""        <itemref idref="dictionary%d"/>
"""

	OPF_TEND = u"""</spine>

<tours/>
<guide> <reference type="search" title="Dictionary Search" onclick= "index_search()"/> </guide>
</package>
"""

	opf = OPF_HEAD1 % (options['basename'], options['basename'], options['language']['language'])
	opf += OPF_THEAD
	opf += OPF_HEAD2 % (options['language']['input_language'], options['language']['output_language'], options['cover'])
	for i in xrange(count+1):
		opf += OPF_TLINE % (i, options['basename'], i)
	opf += OPF_TMIDDLE
	for i in xrange(count+1):
		opf += OPF_TLREF % i
	opf += OPF_TEND
	outfile = dec(os.path.realpath(os.path.join(options['outdir'], options['basename'] + '.opf')))
	try:
                open(outfile, 'wb').write(enc(opf))
	except (OSError, IOError), msg:
		options['logger'].write(msg)
		raise Exception(msg)
	return outfile


def bgl2dic(bgl, options):
	"""Convert a bgl file into a dic file, save the dic file and return the
	file name."""
	ret = dec(os.path.join(options['outdir'], "%s.dic" % options['basename']))
	outfile = open(ret, 'wb')
	buf = unpack(bgl, options)
	fd = StringIO(buf)
	i = 0
	if type(options['filters']) == list and options['filters'] != []:
		options['logger'].write("Filters that will be applied:")
		for filter in options['filters']:
			options['logger'].write("* %s" % filter[1])
	options['logger'].write('Extracting definitions and resources..')
	defcount, rescount = 0, 0
	while True:
		firstbyte = fd.read(1)
		if len(firstbyte) == 0:
			break
		high = ord(firstbyte) >> 4
		low = ord(firstbyte) & 0xF
		if high >= 4:
			record_len = high - 4
		else:
			record_len = 0
			for i in xrange(0, high+1):
				record_len *= 256
				record_len += ord(fd.read(1))
		pos = fd.tell()

		if low == 0:
			if DEBUG:
				specifier = fd.read(1)
				data = fd.read(record_len)
				options['logger'].write("specifier: <%s>, data: <%s>" % (specifier, data))
		elif low == 1:
			# entry
			lenbyte = fd.read(1)
			if len(lenbyte) == 0:
				continue # let first lines of the while loop to do the real break
			entry_name = dec(fd.read(ord(lenbyte)))
			if entry_name[0] in dec(VALID_CHARS):
				lenmul = fd.read(1)
				lenadd = fd.read(1)
				lenword = ord(lenmul) * 256 + ord(lenadd)
				#if lenword > 1019:
				#	lenword = 1019
				tmp = dec(fd.read(lenword))
				if type(options['filters']) == list and options['filters'] != []:
					for filter, name in options['filters']:
						entry_name = filter(entry_name)
						tmp = filter(tmp)
				entry = u"%s\r\n%s\r\n" % (entry_name, tmp)
				outfile.write(enc(entry))
				defcount += 1
		elif low == 2:
			# resource
			name_len = ord(fd.read(1))
			data_len = record_len - name_len
			name = fd.read(name_len)
			data = fd.read(data_len)
			resfile = enc(dec(os.path.join(options['res_outdir'], name)))
                        open(resfile, 'wb').write(data)
			rescount += 1
		fd.seek(pos + record_len)
		i += 1
	options['logger'].write('%d definitions and %d resources extracted' % (defcount, rescount))
	options['logger'].write('Done.')
	return ret


def dic2opf(dic, options):
	"""Convert dic into opf from the given file descriptor. Saves the HTML
        file structure and the opf file in the outdir. Returns the opf file name"""
	if options['cover'] is not None:
	        if os.path.isfile(options['cover']):
	                cover_name = os.path.basename(options['cover'])
			options['logger'].write('Copying cover image to the output dir..')
	                shutil.copy(options['cover'], os.path.join(options['outdir'], cover_name))
	                options['cover'] = cover_name
		else:
			options['logger'].write('Warning: the specified image is not a regular file')
			options['cover'] = ''
	else:
		options['cover'] = ''
	options['logger'].write('Building file definitions..')
	definitions = build_definitions(dic)
	options['logger'].write('Creating HTML structure..')
	i = create_html(definitions, options)
	options['logger'].write('Creating OPF file..')
	outfile = create_opf(options, i)
	options['logger'].write('Done.')
	return outfile


def opf2mobi(opf, options):
	"""Convert an opf file (and the related HTML files structure) into a mobi
	file, relying on thecall to an external opf-to-mobi converter"""
	options['logger'].write('Converting from OPF to MOBI..')
	if options['compression_level'] is None:
		options['compression_level'] = u'0'
	if options['security_level'] is None:
		options['security_level'] = u'0'
	if sys.platform == 'linux2':
		mobigen = 'mobigen_linux'
	elif sys.platform == 'win32':
		mobigen = 'mobigen.exe'
	else:
		msg = "Platform not supported while converting from opf to mobi"
		options['logger'].write(msg)
		raise Exception(msg)
	if options['compression_level'] not in [u'0', u'1', u'2']:
		msg ="Invalid compression level while converting .opf to .mobi: %s" % options['compression_level']
		options['logger'].write(msg)
		raise Exception(msg)
	if options['security_level'] not in [u'0', u'1', u'2']:
		msg = "Invalid security level while converting .opf to .mobi: %s" % options['security_level']
		options['logger'].write(msg)
		raise Exception(msg)
	mobigen_cmd = os.path.join(os.path.dirname(os.path.realpath(__file__)), mobigen)
	cmd = [mobigen_cmd, "\"%s\"" % opf, '-c' + options['compression_level'], '-s' + options['security_level'], '-gif', '-unicode']
	options['logger'].write("Entering %s" % os.path.dirname(opf))
	try:
		os.chdir(os.path.dirname(opf))
	except OSError, msg:
		options['logger'].write(str(msg))
		raise
	options['logger'].write("Executing %s" % ' '.join(cmd))
	fd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
	fd.wait()
	options['logger'].write(fd.stdout.read())
	ret = fd.returncode
	if ret == 0:
		options['logger'].write('Conversion successful')
	else:
		options['logger'].write('Conversion terminated with error code %d' % ret)
	options['logger'].write('Done.')


def any2any(options):
	"""Convert any format to any other format. Sounds magic."""
	options['infile_ext'] = options['infile_ext'].lower()
	# Call the right functions
	if options['output_format'] == u'ubgl':
		bgl = open(options['infile'], 'rb')
		buf = unpack(bgl, options)
		open(os.path.join(options['outdir'], options['basename'] + '.ubgl'), 'wb').write(buf)
		bgl.close()
	elif options['output_format'] == u'dic':
		bgl = open(options['infile'], 'rb')
		dic = bgl2dic(bgl, options)
		bgl.close()
	elif options['output_format'] == u'opf':
		if options['infile_ext'] == u'bgl':
                        bglfd = open(options['infile'], 'rb')
			dic = bgl2dic(bglfd, options)
                        dicfd = open(dic, 'rb')
			opf = dic2opf(dicfd, options)
			dicfd.close()
			bglfd.close()
		elif options['infile_ext'] == u'dic':
                        dicfd = open(options['infile'], 'rb')
			opf = dic2opf(dicfd, options)
			dicfd.close()
	elif options['output_format'] == u'mobi':
		if options['infile_ext'] == u'bgl':
                        bgl = open(options['infile'], 'rb')
			dic = bgl2dic(bgl, options)
                        dicfd = open(dic, 'rb')
			opf = dic2opf(dicfd, options)
			mobi = opf2mobi(opf, options)
			dicfd.close()
			bgl.close()
		elif options['infile_ext'] == 'dic':
                        dicfd = open(options['infile'], 'rb')
			opf = dic2opf(dicfd, options)
			mobi = opf2mobi(opf, options)
			dicfd.close()
		elif options['infile_ext'] == 'opf':
			mobi = opf2mobi(opf, options)


def setup_vars(options):
	"""Return the required variables suitable to call any2any()"""	
	# Set up input and output resources
	options['basename'] = os.path.basename(os.path.realpath(options['infile']))
	options['basename'], options['infile_ext'] = os.path.splitext(options['basename'])
	options['dirname'] = os.path.dirname(options['infile'])
	options['infile_ext'] = options['infile_ext'].lstrip(u'.').lower()
	if options['outdir'] is None:
		options['outdir'] = dec(os.path.join(os.getcwd(), options['basename']))
	options['res_outdir'] = options['outdir'] # Must be unicode for Windows portability. If you change this, use dec(new_outdir)
	return options


def makedirs(options):
	"""Create output directories"""
	if os.path.exists(options['outdir']) and os.path.isdir(options['outdir']) \
		and os.listdir(options['outdir']):
			raise MakeDirsException("Error: the output directory (%s) already exists and is not empty, remove it or delete the files within" % options['outdir'])
	if not os.path.isdir(options['outdir']):
		try:
			os.makedirs(options['outdir'])
			if options['outdir'] != options['res_outdir']:
				os.makedirs(options['res_outdir'])
		except OSError, msg:
			raise MakeDirsException(msg)


def main():
	if len(sys.argv) == 1:
		usage()
	_filters = ''
	options = {}
	options['logger'] = lib.utils.Logger()
	dumper = LogDumper(options['logger'])
	options['outfile'] = None
	options['outdir'] = None
	options['output_format'] = None
	options['compression_level'] = None
	options['security_level'] = None
	options['cover'] = None
	options['language'] = {}
	options['language']['language'] = DEFAULT_LANGUAGE
	options['language']['input_language'] = DEFAULT_INPUT_LANGUAGE
	options['language']['output_language'] = DEFAULT_OUTPUT_LANGUAGE

	lang_names = {
			'language':checklang(DEFAULT_LANGUAGE),
			'input_language':checklang(DEFAULT_INPUT_LANGUAGE),
			'output_language':checklang(DEFAULT_OUTPUT_LANGUAGE)
			}
	# Check commandline arguments
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], 'o:c:s:uh',
                                ['filters=', 'outdir=', 'language=', 'unicode', 'cover'
					'input-language=', 'output-language=', 'list-languages'])
	except getopt.GetoptError, msg:
		options['logger'].write(str(msg))
		return 1
	for o, a in opts:
		if o == '-h':
			usage()
		if o == '-o':
			options['output_format'] = dec(a)
		elif o == '-c':
			options['compression_level'] = dec(a)
		elif o == '-s':
			options['security_level'] = dec(a)
		elif o == '--filters':
			_filters = a
		elif o == '--outdir':
			options['outdir'] = a
		elif o in ['-n', '--no-unicode']:
			lib.utils.use_unicode = False
		elif o == '--cover':
			options['cover'] = a
		elif o == '--language':
			options['language']['language'] = a
		elif o == '--input-language':
			options['language']['input_language'] = a
		elif o == '--output-language':
			options['language']['output_language'] = a
		elif o == '--list-languages':
			list_languages(options['logger'])
			return 0
	if options['output_format'] is None or len(args) != 1:
		usage()
	if options['output_format'] not in [u'ubgl', u'dic', u'opf', u'mobi']:
		options['logger'].write("Output format (`-o' switch) must be one of 'ubgl', 'dic', 'html' or 'mobi'")
		return 1
	if options['output_format'] != u'mobi' and options['compression_level'] != None:
		options['logger'].write("Compression level (`-c' switch) is valid only when the output format is 'mobi'")
		return 1
	if options['compression_level'] not in [None, u'0', u'1', u'2']:
		options['logger'].write("Compression level (`-c' switch) must be either 0, 1 or 2")
	if options['output_format'] != u'mobi' and options['security_level'] != None:
		options['logger'].write("Security level (`-s' switch) is valid only when the output format is 'mobi'")
		return 1
	if options['security_level'] not in [None, u'0', u'1', u'2']:
		options['logger'].write("Security level (`-c' switch) must be either 0, 1 or 2")
	if options['security_level'] is None:
		options['security_level'] = DEFAULT_SECURITY_LEVEL
	if options['cover'] is not None and options['output_format'] not in [u'opf', u'mobi']:
		options['logger']("Cover (`--cover' switch is valid only when the output format is 'opf' or 'mobi'")
		return 1
	if options['cover'] is not None and options['output_format'] == u'mobi':
		if not os.path.isfile(options['cover']):
			options['logger'].write("Cover must be a valid file")
			return 1
	options['logger'].write("Languages used in the dictionary:")
	for lang in options['language'].keys():
		lang_names[lang] = checklang(options['language'][lang])
		if lang_names[lang] is None:
			options['logger'].write('Error: language "%s" is not valid' % options['language'][lang])
			return 1
		options['logger'].write("* %s: %s (%s)" % (lang, options['language'][lang], lang_names[lang]))

	options['infile'] = dec(args[0])
	options['filters'], options['bad_filters'] = get_filters(_filters.split(','))
	options = setup_vars(options)

	# Check input validity
	if options['output_format'] in [u'dic', u'bgl'] and options['infile_ext'] != u'bgl':
		options['logger'].write("To convert into .%s, you must feed a .bgl file" % options['output_format'])
		return 1
	if options['output_format'] == u'opf' and options['infile_ext'] not in [u'bgl', u'dic']:
		options['logger'].write("To convert into .opf, you must feed a .bgl or a .dic file")
		return 1
	if options['output_format'] == u'mobi' and options['infile_ext'] not in [u'bgl', u'dic', u'opf']:
		options['logger'].write("To convert into .mobi, you must feed a .bgl, a .dic or a .opf file")
		return 1

	# Create output directories
	try:
		makedirs(options)
	except MakeDirsException, msg:
		options['logger'].write(str(msg))
		return 1

	# Do the dirty work
	any2any(options)

if __name__ == '__main__':
	ret = 1
	try:
		ret = main()
	except Exception, msg:
		print str(msg)
	sys.exit(ret)

