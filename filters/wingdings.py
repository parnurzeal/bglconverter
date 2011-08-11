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
#     * Neither the name of the <organization> nor the
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

import re

DEFAULT_FONT = "Lucida Sans Unicode"

# Buggy: It strips all but <font ...>. Moreover it cannot handle unclosed tags,
# as found in some dictionary.
def filter(s):
	"""This filter converts tags like <font face="Wingdings" ... > in order
	to have a different font"""
	match_font = re.compile(r"""(<font\s+[^>]*>)""", re.IGNORECASE)
	match_attrs = re.compile(r"""\w+\s*=\s*["'][^"']*["']""")
	tag = ''
	font_tag = match_font.search(s)
	if font_tag:
		tag = font_tag.group(0)
		ret = '<FONT'
		attrs = match_attrs.findall(tag)
		for attr in attrs:
			k, v = [e.strip("'") for e in attr.split('=', 1)]
			if k.lower() == "face" and v.lower() == "wingdings":
				v = DEFAULT_FONT
			ret += ''' %s="%s"''' % (k, v)
		ret += '>'
	else:
		ret = s
	return match_font.sub(ret, s)

