from monitor import Monitor
from event import Event
from rule import Rule
from assignment import Assignment
from processatom import ProcessAtom
from gapatom import GapAtom

import csv

class Parser:
	def __init__(self):
		pass

	def readEventStreamFromCSV(self, eventStreamCSVFileName):
		eventStream = []

		with open(eventStreamCSVFileName, newline='') as f:
			reader = csv.reader(f)
			for d in list(reader):
				if not d:
					continue
				eventType = d[0]
				eventName = d[1]
				eventData = list(map(lambda y: y.strip(), d[2:]))
				eventData[-1] = int(eventData[-1])
				eventStream.append(Event(eventType, eventName, eventData))

		return eventStream

	def readRuleFromTxt(self, ruleTxtFile):
		file1 = open(ruleTxtFile, 'r')
		
		lines = file1.read().splitlines()

		file1.close()

		lines.pop(0) # consume "Rule"

		ruleName = lines.pop(0) # get rule name

		lines.pop(0) # consume "if"		
		
		line = lines.pop(0) # get first line after if
		
		bodyProcessAtoms = []
		bodyGapAtoms = []
		headProcessAtoms = []
		headGapAtoms = []

		while(line != 'then'):
			if ("<" in line or "=" in line or ">" in line):
				bodyGapAtoms.append(self.parseGapAtomString(line))
			else:
				bodyProcessAtoms.append(self.parseProcessAtomString(line))
			line = lines.pop(0)

		lines.pop() # remove "end"

		for line in lines:
			if ("<" in line or "=" in line or ">" in line):
				headGapAtoms.append(self.parseGapAtomString(line))
			else:
				headProcessAtoms.append(self.parseProcessAtomString(line))

		r = Rule(ruleName, bodyProcessAtoms, bodyGapAtoms, headProcessAtoms, headGapAtoms)
		return r

	def parseProcessAtomString(self, s):
		name = s[:s.find("(")]
		dataString = s[s.find('(')+1:s.find(')')]
		attributes = []
		variables = []
		for d in dataString.split(','):
			data = d.strip().split(" ")
			attributes.append(data[0])
			variables.append(data[1])
		attributes.append('time')
		variables.append(s[s.find('@')+1:])

		return ProcessAtom(name, attributes, variables)


	def parseGapAtomString(self, s):
		lhs = ''
		rhs = ''
		gap = 0
		direction = ''
		offset = 0

		if '<=' in s:
			direction = '<='
			offset = 1
		elif '>=' in s:
			direction = '>='
			offset = 1
		elif '>' in s:
			direction = '>'
		elif '<' in s:
			direction = '<'
		elif "=" in s:
			direction = '='
		else:
			print("Operator not recognized")

		rhs = s[s.find(direction)+offset+1:].strip()

		if (s.find('+') != -1):
			lhs = s[:s.find('+')][:s.find(direction)].strip()
			gap = s[s.find('+')+1:s.find(direction)-1]
		else:
			lhs = s[:s.find(direction)].strip()

		return GapAtom(lhs, rhs, direction, 'days', int(gap))




