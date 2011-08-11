from cx_Freeze import setup, Executable

setup(
        name = "bglconverter",
        version = "0.1",
        description = "A tool to convert Babylon dictionaries into other formats",
        executables = [
			Executable("bglconverter.py", includes=['getopt', 'subprocess', 'cStringIO', 'codecs', 'lib', 'Exception']),
			Executable("qtbglconverter.py", includes=['codecs', 'subprocess', 'sip', 'PyQt4', 'bglconverter', 'lib', 'filters', 'cStringIO', 'Exception'])
		]
	)

