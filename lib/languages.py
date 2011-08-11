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


# List of supported languages, as stated in MobiPocket Creator/rsrc/html/main.js
languages_list = [ 
  ["af", "Afrikaans"],
  ["sq", "Albanian"],
  ["ar", "Arabic"],
  ["ar-dz", "Arabic (Algeria)"],
  ["ar-bh", "Arabic (Bahrain)"],
  ["ar-eg", "Arabic (Egypt)"],
  ["ar-eg", "Arabic (Iraq)"],
  ["ar-jo", "Arabic (Jordan)"],
  ["ar-kw", "Arabic (Kuwait)"],
  ["ar-lb", "Arabic (Lebanon)"],
  ["ar-lb", "Arabic (Libya)"],
  ["ar-ma", "Arabic (Morocco)"],
  ["ar-om", "Arabic (Oman)"],
  ["ar-qa", "Arabic (Qatar)"],
  ["ar-sa", "Arabic (Saudi Arabia)"],
  ["ar-sy", "Arabic (Syria)"],
  ["ar-tn", "Arabic (Tunisia)"],
  ["ar-ae", "Arabic (U.A.E.)"],
  ["ar-ye", "Arabic (Yemen)"],
  ["hy", "Armenian"],
  ["az", "Azeri (Cyrillic)"],
  ["az", "Azeri (Latin)"],
  ["eu", "Basque"],
  ["be", "Belarusian"],
  ["bn", "Bengali"],
  ["bg", "Bulgarian"],
  ["ca", "Catalan"],
  ["zh", "Chinese"],
  ["zh-hk", "Chinese (Hong Kong)"],
  ["zh-cn", "Chinese (PRC)"],
  ["zh-sg", "Chinese (Singapore)"],
  ["zh-tw", "Chinese (Taiwan)"],
  ["hr", "Croatian"],
  ["cs", "Czech"],
  ["da", "Danish"],
  ["nl", "Dutch"],
  ["nl-be", "Dutch (Belgium)"],
  ["en", "English"],
  ["en-au", "English (Australia)"],
  ["en-bz", "English (Belize)"],
  ["en-ca", "English (Canada)"],
  ["en-ie", "English (Ireland)"],
  ["en-jm", "English (Jamaica)"],
  ["en-nz", "English (New Zealand)"],
  ["en-ph", "English (Philippines)"],
  ["en-za", "English (South Africa)"],
  ["en-tt", "English (Trinidad)"],
  ["en-gb", "English (United Kingdom)"],
  ["en-us", "English (United States)"],
  ["en-zw", "English (Zimbabwe)"],
  ["et", "Estonian"],
  ["fo", "Faeroese"],
  ["fa", "Farsi"],
  ["fi", "Finnish"],
  ["fr-be", "French (Belgium)"],
  ["fr-ca", "French (Canada)"],
  ["fr", "French"],
  ["fr-lu", "French (Luxembourg)"],
  ["fr-mc", "French (Monaco)"],
  ["fr-ch", "French (Switzerland)"],
  ["ka", "Geogian"],
  ["de", "German"],
  ["de-at", "German (Austria)"],
  ["de-li", "German (Liechtenstein)"],
  ["de-lu", "German (Luxembourg)"],
  ["de-ch", "German (Switzerland)"],
  ["el", "Greek"],
  ["gu", "Gujarati"],
  ["he", "Hebrew"],
  ["hi", "Hindi"],
  ["hu", "Hungarian"],
  ["is", "Icelandic"],
  ["id", "Indonesian"],
  ["it", "Italian"],
  ["it-ch", "Italian (Switzerland)"],
  ["ja", "Japanese"],
  ["kn", "Kannada"],
  ["kk", "Kazakh"],
  ["x-kok", "Konkani"],
  ["ko", "Korean"],
  ["lv", "Latvian"],
  ["lt", "Lithuanian"],
  ["mk", "Macedonian"],
  ["ms", "Malay (Brunei Darussalam)"],
  ["ms", "Malay (Malaysia)"],
  ["ml", "Malayalam"],
  ["mt", "Maltese"],
  ["mr", "Marathi"],
  ["ne", "Nepali"],
  ["no", "Norwegian (Bokmal)"],
  ["no", "Norwegian (Nynorsk)"],
  ["or", "Oriya"],
  ["pl", "Polish"],
  ["pt", "Portuguese"],
  ["pt-br", "Portuguese (Brazil)"],
  ["pa", "Punjabi"],
  ["rm", "Rhaeto-Romanic"],
  ["ro", "Romanian"],
  ["ro-mo", "Romanian (Moldova)"],
  ["ru", "Russian"],
  ["ru-mo", "Russian (Moldova)"],
  ["sz", "Sami (Lappish)"],
  ["sa", "Sanskrit"],
  ["sr", "Serbian (Cyrillic)"],
  ["sr", "Serbian (Latin)"],
  ["sk", "Slovak"],
  ["sl", "Slovenian"],
  ["sb", "Sorbian"],
  ["es", "Spanish"],
  ["es-ar", "Spanish (Argentina)"],
  ["es-bo", "Spanish (Bolivia)"],
  ["es-cl", "Spanish (Chile)"],
  ["es-co", "Spanish (Colombia)"],
  ["es-cr", "Spanish (Costa Rica)"],
  ["es-do", "Spanish (Dominican Republic)"],
  ["es-ec", "Spanish (Ecuador)"],
  ["es-sv", "Spanish (El Salvador)"],
  ["es-gt", "Spanish (Guatemala)"],
  ["es-hn", "Spanish (Honduras)"],
  ["es-mx", "Spanish (Mexico)"],
  ["es-ni", "Spanish (Nicaragua)"],
  ["es-pa", "Spanish (Panama)"],
  ["es-py", "Spanish (Paraguay)"],
  ["es-pe", "Spanish (Peru)"],
  ["es-pr", "Spanish (Puerto Rico)"],
  ["es-uy", "Spanish (Uruguay)"],
  ["es-ve", "Spanish (Venezuela)"],
  ["sx", "Sutu"],
  ["sw", "Swahili"],
  ["sv", "Swedish"],
  ["sv-fi", "Swedish (Finland)"],
  ["ta", "Tamil"],
  ["tt", "Tatar"],
  ["te", "Telugu"],
  ["th", "Thai"],
  ["ts", "Tsonga"],
  ["tn", "Tswana"],
  ["tr", "Turkish"],
  ["uk", "Ukranian"],
  ["ur", "Urdu"],
  ["uz", "Uzbek (Cyrillic)"],
  ["uz", "Uzbek (Latin)"],
  ["vi", "Vietnamese"],
  ["xh", "Xhosa"],
  ["zu", "Zulu"]
]


def checklang(lang):
	"""This function returns the full name of the language, if it's code is valid, None otherwise"""
	for l in languages_list:
		if lang == l[0]:
			return l[1]
	return None
 

def list_languages(logger):
	logger.write("Supported languages:\n")
	for l in languages_list:
		logger.write("* %s (%s)" % (l[0], l[1]))

def get_languages():
	return languages_list

