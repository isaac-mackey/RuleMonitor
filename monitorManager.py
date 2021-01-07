from parser import Parser
from event import Event
from monitor import Monitor
from rule import Rule
from processatom import ProcessAtom
from gapatom import GapAtom
from assignment import Assignment

import pdb

class MonitorManager:

	def __init__(self, ruleTxtFile):
		self.monitor = Monitor("MyMonitor")
		parser = Parser()
		rule = parser.readRuleFromTxt(ruleTxtFile)
		self.monitor.ruleVector.append(rule)
		for r in self.monitor.ruleVector:
			print(r)

		self.eventStream = None
	
	def buildEventStream(self, eventStreamCSVFileName):
		self.eventStream = Parser().readEventStreamFromCSV(eventStreamCSVFileName)

		for e in self.eventStream:
			print(e)

	def monitoringLoop(self):
		i = 0
		eventStreamLength = len(self.eventStream)

		userInput = ''

		while ((userInput != 'q') and (i < eventStreamLength)):

			if userInput == 'q':
				break

			if userInput == 'a':
				self.monitor.printAssignments()

			if userInput == 'm':
				for r in self.monitor.ruleVector:
					self.monitor.findMatches(r)

			if userInput == 'n':
				if i == eventStreamLength:
					print("End of sequence")

				if self.eventStream[i].eventType == "process":
					self.monitor.handleProcessEvent(self.eventStream[i])

				for r in self.monitor.ruleVector:
					self.monitor.findMatches(r)

				self.monitor.removeExpiredData(self.eventStream[i])

				i += 1

			if userInput == 'f':
				while (i != eventStreamLength):
					print(self.eventStream[i])
					
					if self.eventStream[i].eventType == "process":
						self.monitor.handleProcessEvent(self.eventStream[i])					
					
					for r in self.monitor.ruleVector:
						self.monitor.findMatches(r)

					self.monitor.removeExpiredData(self.eventStream[i])

					i += 1

			if userInput == 'x':
				self.monitor.removeExpiredData(self.eventStream[i])

			print('\n\n\n')
			print('---------------------------------------------------')
			print('\n\n\n')

			#print ("Input: ", end='')
			#userInput = raw_input()
			userInput = 'f'

		print('\n'*40)

		print("Summary:\n")
		for a in self.monitor.assignmentVector:
			if a.typeOfAssignment == 'body':
				if a.complete:
					if len(a.missingProcessAtoms) == 0 or True:
						print("Body Assignment: ",end='')
						print(a)
		print('\n')

import sys

print('Argument List:', str(sys.argv))

exampleNumber = "4"

exampleName = "examples/example"+str(exampleNumber)

exampleDirectory = "examples/"

ruleFile = exampleDirectory+sys.argv[1]

eventStreamFile = exampleDirectory+sys.argv[2]

m = MonitorManager(ruleFile)

m.buildEventStream(eventStreamFile)

m.monitoringLoop()
