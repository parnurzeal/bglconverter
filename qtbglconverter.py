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
import time
from PyQt4 import QtGui, QtCore
from gui.QTbglconverter import Ui_QtBGLConverter
from gui.LogWindow import Ui_LogWindow
import bglconverter
import filters
import lib.utils
from lib.languages import get_languages


class UpdateThread(QtCore.QThread):
	widget = None
	def setWidget(self, widget):
		self.widget = widget

	def run(self):
		if self.widget is None:
			raise Exception("Widget is not set")
		while True:
			self.widget.emit(QtCore.SIGNAL("modificationChanged()"))
			time.sleep(1)

class Converter(QtCore.QThread):
	options = None
	def setOptions(self, options):
		self.options = options

	def run(self):
		if self.options is None:
			raise Exception("Options are not set")
		bglconverter.any2any(self.options)


#class LogWindow(QtGui.QDialog, Ui_LogWindow):
#	def __init__(self):
#		QtGui.QDialog.__init__(self)
#		self.setupUi(self)


# QLogViewer by Giuseppe Coviello <cjg@cruxppc.org>
class QLogViewer(QtGui.QTextEdit):
	def __init__(self, logger):
		QtGui.QTextEdit.__init__(self)
		logger.connect("logline", self.insertline)

	def insertline(self, emitter, args):
		self.append(args[0])

class QtBGLConverter(QtGui.QDialog, Ui_QtBGLConverter):
	def __init__(self):
		QtGui.QDialog.__init__(self)

		# Set up the user interface from Designer.
		self.setupUi(self)

		# Set up language boxes
		self.languages = get_languages()
		langs = [str(l[1]) for l in self.languages]
		self.dictionaryLanguageBox.addItems(QtCore.QStringList(langs))
		self.inputLanguageBox.addItems(QtCore.QStringList(langs))
		self.outputLanguageBox.addItems(QtCore.QStringList(langs))
		self.filtersList.addItems(QtCore.QStringList(filters.get_filters_list()))
		#self.connect(self.console, QtCore.SIGNAL("modificationChanged()"), self.updateConsole)

		# Waiting to improve the console support...
		self.consoleBox.hide()

		size = self.size()
		size.setHeight(0)
		self.resize(size)

		# Initialize the logger
                self.logger = lib.utils.Logger()
		lib.utils.LogDumper(self.logger)
		lib.utils.LogWriter(self.logger, lib.utils.LOGFILE)

	def updateConsole(self):
		self.console.insertPlainText(QtCore.QString(self.logger.read()))

	def on_inputBrowseButton_released(self):
		self.inputFileText.setText(QtGui.QFileDialog.getOpenFileName(
			self,
			"Pick a dictionary file",
			os.getcwd(),
			"All supported dictionary types (*.opf *.dic *.bgl)"))
	
	def on_outputBrowseButton_released(self):
		self.outputDirectoryText.setText(
			QtGui.QFileDialog.getExistingDirectory(self))

	def on_coverImageBrowseButton_released(self):
		self.coverImageText.setText(QtGui.QFileDialog.getOpenFileName(
			self,
			"Pick a cover image",
			os.getcwd(),
			"JPEG files (*.jpeg *.jpg)"))

	def on_mobiRadio_toggled(self, toggled):
		self.mobiOptions.setEnabled(toggled)
	
	def on_exitButton_released(self):
		self.close()

	def get_languageCode(self, langname):
		"""Return the language code of the given language name. Otherwise return None"""
		for code, name in self.languages:
			if name == langname:
				return code
		return None

	def on_generateButton_released(self):
		options = {}
		options['logger'] = self.logger
		options['language'] = {}
		options['infile'] = str(self.inputFileText.text())
		options['outdir'] = str(self.outputDirectoryText.text())
		if options['infile'] == '':
			QtGui.QMessageBox.critical(
				self,
				"Error",
				"The input file was not specified",
				QtGui.QMessageBox.Ok)
			return
		if options['outdir'] == '':
			QtGui.QMessageBox.critical(
				self,
				"Error",
				"The output directory was not specified",
				QtGui.QMessageBox.Ok)
			return
		options['outdir'] = os.path.abspath(options['outdir'])
		if self.ubglRadio.isChecked():
			options['output_format'] = u'ubgl'
		elif self.dicRadio.isChecked():
			options['output_format'] = u'dic'
		elif self.opfRadio.isChecked():
			options['output_format'] = u'opf'
		elif self.mobiRadio.isChecked():
			options['output_format'] = u'mobi'
		else:
			options['output_format'] = None 
		filters = [str(f.text()) for f in self.filtersList.selectedItems()]
		options['filters'], options['bad_filters'] = lib.utils.get_filters(filters)
		options['bad_filters'] = [str(f) for f in options['bad_filters']]
		options = bglconverter.setup_vars(options)
		options['cover'] = str(self.coverImageText.text())
		options['language']['language'] = self.get_languageCode(
				str(self.dictionaryLanguageBox.currentText()))
		options['language']['input_language'] = self.get_languageCode(
				str(self.inputLanguageBox.currentText()))
		options['language']['output_language'] = self.get_languageCode(
				str(self.outputLanguageBox.currentText()))
		if not os.path.isfile(options['infile']):
			QtGui.QMessageBox.critical(
				self,
				"Error",
				"The input file is invalid or doesn't exist",
				QtGui.QMessageBox.Ok)
			return
		if not os.path.isdir(options['outdir']):
			QtGui.QMessageBox.critical(
				self,
				"Error",
				"The output directory is invalid or doesn't exist",
				QtGui.QMessageBox.Ok)
			return
		for key in options['language'].keys():
			if options['language'][key] is None:
				QtGui.QMessageBox.critical(
					self,
					"Error",
					"The language %s is invalid" % key,
					QtGui.QMessageBox.Ok)
				return
		if options['output_format'] is None:
			QtGui.QMessageBox.critical(
				self,
				"Error",
				"You must choose the output format",
				QtGui.QMessageBox.Ok)
			return
		if options['output_format'] in [u'opf', u'mobi']:
			if not os.path.isfile(options['cover']):
				reply = QtGui.QMessageBox.question(
					self,
					"Warning",
					"The cover image file is invalid, was not specified, or doesn't exist. Continue anyway?",
					QtGui.QMessageBox.Yes,
					QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.Yes:
					options['cover'] = ''
				else:
					return
		else:
			if options['cover'] != '':
				reply = QtGui.QMessageBox.warning(
					self,
					"Warning",
					"The cover image file was specified, but the output format is neither 'opf' or 'mobi'. The image file will be ignored.",
					QtGui.QMessageBox.Ok)
		try:
			bglconverter.makedirs(options)
		except bglconverter.MakeDirsException, msg:
			QtGui.QMessageBox.critical(
				self,
				"Error",
				str(msg),
				QtGui.QMessageBox.Ok)
			return
		if options['output_format'] == u'mobi':
			options['compression_level'] = str(self.compressionComboBox.currentIndex())
			options['security_level'] = str(self.securityComboBox.currentIndex())
		self.t1 = Converter()
		self.t1.setOptions(options)
		self.t1.start()
		#self.t2 = UpdateThread()
		#self.t2.setWidget(self.console)
		#self.t2.start()
		self.connect(self.t1, QtCore.SIGNAL("finished()"), self.cleanUp)
		self.waitBox = QtGui.QMessageBox(self)
		self.waitBox.addButton(QtGui.QMessageBox.Cancel)
		self.waitBox.setText("Please wait, the conversion process may take from seconds up to hours, depending on the dictionary size and the compression level. Click Cancel or press ESC to stop.")
		reply = self.waitBox.exec_()
		if reply == QtGui.QMessageBox.Cancel:
			self.t1.terminate()
			QtGui.QMessageBox.warning(
			self,
			"Warning",
			"The conversion process has been interrupted. Check the log file for details",
			QtGui.QMessageBox.Ok)

	def cleanUp(self):
		#self.t2.terminate()
		self.waitBox.hide()
		del self.waitBox
		#window = LogWindow()
		window = QLogViewer(self.logger)
		#try:
		#	buf = self.logger.readAll()
		#except Exception, msg:
		#	buf = str(msg) + '\n'
		#window.logText.insertPlainText(buf)
		window.show()
#		window.exec_()


	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(
			self,
			'Really exit?',
			"Are you sure want to quit?",
			QtGui.QMessageBox.Yes,
			QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

def main():
	app = QtGui.QApplication(sys.argv)
	window = QtBGLConverter()
	window.show()
	return app.exec_()

if __name__ == '__main__':
	sys.exit(main())

