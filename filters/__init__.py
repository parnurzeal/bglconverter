#!/usr/bin/env python
#coding: utf-8
#

def get_filters_list():
	import os

	filters = []
	curdir = os.path.realpath(os.path.dirname(os.path.join(os.getcwd(), __file__)))
	for entry in os.listdir(curdir):
		curfile = os.path.join(curdir, entry)
		if os.path.isfile(curfile) and entry != '__init__.py' and entry.endswith('.py'):
			filters.append(os.path.splitext(entry)[0])
	return filters
