# encoding: utf-8

###########################################################################################################
#
#
#	File Format Plugin
#	Implementation for exporting fonts through the Export dialog
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/File%20Format
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import codecs
from os import path

@objc.python_method
def saveFileInLocation(content="", fileName="font.ps", filePath="~/Desktop"):
	saveFileLocation = "%s/%s" % (filePath, fileName)
	saveFileLocation = saveFileLocation.replace( "//", "/" )
	content=codecs.encode(content, encoding='utf-8')
	content=codecs.decode(content, encoding='ascii', errors='ignore')
	with codecs.open(saveFileLocation, "w", encoding="ascii", errors="ignore") as thisFile:
		# print("Exporting PS:", thisFile.name) # DEBUG
		thisFile.write(content)
		thisFile.close()
	return True

@objc.python_method
def commentOut(code):
	lines = code.splitlines()
	for i in range(len(lines)):
		lines[i] = "# %s" % lines[i]
	return "\n".join(lines)

class FEAExport(FileFormatPlugin):
	prefDomain = "com.mekkablue.ExportFeatures"
	prefDict = {
		"expandTokens": False,
		"includeInactive": False,
	}
	
	# Definitions of IBOutlets
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	checkboxExpandTokens = objc.IBOutlet()
	checkboxIncludeInactive = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'FEA Export',
			'de': 'Features-Export',
			})
		self.icon = 'ExportIcon'
		self.toolbarPosition = 100
		
		# Load .nib dialog (with .extension)
		self.loadNib('IBdialog', __file__)
		
	@objc.python_method
	def start(self):
		# Init user preferences if not existent and set default value
		for prefKey in self.prefDict.keys():
			domain = "%s.%s" % (self.prefDomain, prefKey)
			Glyphs.registerDefault(domain, self.prefDict[prefKey])
			getattr(self, "checkbox"+prefKey[0].upper()+prefKey[1:]).setState_(Glyphs.defaults[domain])
	
	@objc.IBAction
	def setExpandTokens_(self, sender):
		Glyphs.defaults[self.prefDomain+".expandTokens"] = bool(sender.intValue())
	
	@objc.IBAction
	def setIncludeInactive_(self, sender):
		Glyphs.defaults[self.prefDomain+".includeInactive"] = bool(sender.intValue())

	@objc.python_method
	def export(self, font):
		# Ask for export destination and write the file:
		title = "Choose export destination"
		exportFolder = GetFolder(message=title, allowsMultipleSelection=False, path=None)
		expandTokens = Glyphs.defaults[self.prefDomain+".expandTokens"]
		includeInactive = Glyphs.defaults[self.prefDomain+".includeInactive"]
		
		if exportFolder:
			feaPieces = []
			
			feaPieces.append("# CLASSES\n")
			for c in font.classes:
				if c.active or includeInactive:
					classCode = "# CLASS: %s\n" % c.name
					classCode += "%s=[%s];" % (c.name, c.code.strip())
					if not c.active:
						classCode = commentOut(classCode)
					classCode += "\n"
					feaPieces.append(classCode)
				
			feaPieces.append("\n\n# PREFIXES\n")
			for p in font.featurePrefixes:
				if p.active or includeInactive:
					prefixCode = "# PREFIX: %s\n%s\n" % (p.name, p.code.strip())
					if not p.active:
						prefixCode = commentOut(prefixCode)
					prefixCode += "\n"
					feaPieces.append(prefixCode)
				
			feaPieces.append("\n\n# FEATURES")
			for f in font.features:
				if f.active or includeInactive:
					featureCode = "feature %s {\n%s\n};" % (f.name, f.code.strip()) 
					if not f.active:
						featureCode = commentOut(featureCode)
					featureCode += "\n"
					feaPieces.append(featureCode)
			
			# file content:
			feaText = "\n".join(feaPieces)
			
			# file name:
			if font.filepath:
				fileName = font.filepath.lastPathComponent().stringByDeletingDotSuffix()
			else:
				fileName = font.familyName
			
			# save dialog
			saveFileInLocation(
				content=feaText,
				fileName="%s.fea" % fileName,
				filePath=exportFolder,
				)
			
			return (True, 'FEA file exported in ‘%s’.' % path.basename(exportFolder))
		else:
			return (False, 'No folder chosen.')

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
