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
	expandTokensPrefKey = "com.mekkablue.ExportFeatures.expandTokens"
	includeInactivePrefKey = "com.mekkablue.ExportFeatures.includeInactive"

	# Definitions of IBOutlets
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	titleLabel = objc.IBOutlet()
	checkboxExpandTokens = objc.IBOutlet()
	checkboxIncludeInactive = objc.IBOutlet()
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'OT Features',
			'de': 'OT-Features',
			})
		self.icon = 'feaTemplate'
		self.toolbarPosition = 100

		# Load .nib dialog (with .extension)
		self.loadNib('IBdialog', __file__)
		self.titleLabel.setStringValue_(Glyphs.localize({
			'en': 'Export fea feature file',
			'de': 'fea-Datei exportieren',
			}))
		self.checkboxExpandTokens.setEnabled_(False)
		self.checkboxExpandTokens.setTitle_(Glyphs.localize({
			'en': 'Expand tokens',
			'de': 'Token ersetzen',
			}))
		self.checkboxIncludeInactive.setTitle_(Glyphs.localize({
			'en': 'Include inactive code',
			'de': 'Deativierte Feature/Klassen einbeziehen',
			}))

	@objc.python_method
	def start(self):
		# Init user preferences if not existent and set default value
		self.toolbarIcon.setTemplate_(True)

	@objc.python_method
	def export(self, font):
		# Ask for export destination and write the file:
		title = "Choose export destination"
		exportFolder = GetFolder(message=title, allowsMultipleSelection=False, path=None)
		if not exportFolder:
			return (False, 'No folder chosen.')

		expandTokens = Glyphs.defaults[self.expandTokensPrefKey]
		includeInactive = Glyphs.defaults[self.includeInactivePrefKey]

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


	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
