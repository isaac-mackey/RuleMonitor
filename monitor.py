from event import Event
from rule import Rule
from assignment import Assignment
import pdb
import copy

class Monitor:
	def __init__(self, monitorName: str):
		self.monitorName = monitorName
		self.ruleVector = []
		self.assignmentVector = []
		self.currentTime = 0

	def handleProcessEvent(self, e: Event):
		print("Handle process event")
		print(e)
		print()

		newAssignments = []

		for rule in self.ruleVector:
			print("Check if event creates new body assignment\n")

			for bodyProcessAtom in rule.bodyProcessAtoms:
				if (e.eventName == bodyProcessAtom.processName):
					print("Create new body assignment\n")
					variablesDefinedFlags = {x:False for x in rule.bodyVariables}

					values = {}
					for i,v in enumerate(bodyProcessAtom.variables):
						values[v] = e.values[i]
						variablesDefinedFlags[v]=True

					seenProcessAtoms = [];
					seenProcessAtoms.append(bodyProcessAtom)

					missingProcessAtoms = []
					for ruleBodyProcessAtom in rule.bodyProcessAtoms:
						if bodyProcessAtom != ruleBodyProcessAtom:
							missingProcessAtoms.append(ruleBodyProcessAtom)

					matchingAssignments = []

					a = Assignment(rule.bodyVariables,
					values,variablesDefinedFlags,"body",
					rule, missingProcessAtoms,seenProcessAtoms,[],[e])

					print("Newly created body assignment:\n")
					print(a)

					self.assignmentVector.append(a)
					newAssignments.append(a)

			print("Check if event creates new head assignment\n")

			for headProcessAtom in rule.headProcessAtoms:
				if (e.eventName == headProcessAtom.processName):
					print("Create new head assignment\n")
					variablesDefinedFlags = {x:False for x in rule.headVariables}

					values = {}
					for i,v in enumerate(headProcessAtom.variables):
						values[v] = e.values[i]
						variablesDefinedFlags[v]=True

					seenProcessAtoms = [];
					seenProcessAtoms.append(headProcessAtom)

					missingProcessAtoms = []
					for ruleHeadProcessAtom in rule.headProcessAtoms:
						if headProcessAtom != ruleHeadProcessAtom:
							missingProcessAtoms.append(ruleHeadProcessAtom)

					matchingAssignments = []

					a = Assignment(rule.headVariables,
					values,variablesDefinedFlags,"head",
					rule, missingProcessAtoms,seenProcessAtoms,[],[e])

					print("Newly created head assignment\n")
					print(a)

					self.assignmentVector.append(a)
					newAssignments.append(a)

			print("Search for assignments this event will extend\n")

			# loop through existing assignment vector
			for a in self.assignmentVector:
				assignmentDefinedVariables = []

				for v in a.variables:
					if a.variablesDefinedFlags[v]:
						assignmentDefinedVariables.append(v)

				for m in a.missingProcessAtoms:
					if (e.eventName == m.processName):
						eventValuesForVariables = {}

						for i,v in enumerate(m.variables):
							eventValuesForVariables[v] = e.values[i]

						match = True

						for v in m.variables:
							if a.variablesDefinedFlags[v]:
								if (a.values[v] != eventValuesForVariables[v]):
									print("Disagreement with "+v+" variable") 
									match = False;
									break;
						
						if not match:
							continue;

						if a.typeOfAssignment == "body":
							constraints = a.rulePointer.bodyGapAtoms
						else:
							constraints = a.rulePointer.headGapAtoms

						mergedMap = a.values.copy()
						for v in eventValuesForVariables.keys():
							if not v in assignmentDefinedVariables:
								assignmentDefinedVariables.append(v)
							mergedMap[v] = eventValuesForVariables[v]

						print("New mapping for variables:")

						print(mergedMap)

						print('Check if new assignment is consistent with ' + a.typeOfAssignment +' gap atoms\n')

						consistentWithGapAtoms = True

						for c in constraints:
							if ((c.lhs in mergedMap.keys()) and
							(c.rhs in mergedMap.keys())):
								print("Check gap atom")
								print(c)
								if not c.checkTruthValueWithAssignment(mergedMap):
									print("disagreement\n")
									consistentWithGapAtoms = False

						if consistentWithGapAtoms:
							print("Create a new assignment\n")

							b = copy.deepcopy(a)
							
							for v in mergedMap.keys():
								b.values[v] = mergedMap[v]
								b.variablesDefinedFlags[v] = True

							for x in b.missingProcessAtoms:
								if str(x)==str(m):
									b.missingProcessAtoms.remove(x) 

							b.seenProcessAtoms.append(m)

							b.seenEvents.append(e)

							b.complete = len(b.missingProcessAtoms)==0

							b.expirationTime = b.computeExpirationTime()

							self.assignmentVector.append(b)
		
		return newAssignments

	def findMatches(self, r: Rule):
		
		for b in self.assignmentVector:
			if ((b.rulePointer.ruleName == r.ruleName) and (b.complete) and b.typeOfAssignment == 'body'):
				
				for h in self.assignmentVector:
					if ((h.rulePointer.ruleName == r.ruleName) and (h.typeOfAssignment == 'head') and (h.complete) and h not in b.matchingAssignments):
						if(self.doAssignmentsMatch(b,h)):
							print("Found a match\n")
							b.matchingAssignments.append(h)

	def expired(self, a: Assignment):
		return a.expirationTime < self.currentTime
		
	def removeExpiredData(self, e: Event):
		return
		print("Removing data that expires before time "+str(e.values[-1])+"\n")

		latestEventTime = int(e.values[-1])

		unexpiredData = []
		expiredData = []

		for a in self.assignmentVector:
			if a.expirationTime < latestEventTime:
				unexpiredData.append(a)
			else:
				expiredData.append(a)

		self.assignmentVector = unexpiredData

	def printAssignments(self):
		for i,a in enumerate(self.assignmentVector):
			print("assignmentVector["+str(i)+"]")
			print(a)

	def doAssignmentsMatch(self, a, b):
		for v in a.variables:
			if v in b.variables:
				print("Check agreement with variable "+v)
				if (a.values[v] != b.values[v]):
					print("Disagreement between a: "+a.values[v]+" and b: "+b.values[v])
					return False

		mergedMap = a.values.copy()

		for k,v in b.values.items():
			mergedMap[k] = v

		constraints = []

		if (a.typeOfAssignment == 'body'):
			constraints += a.rulePointer.bodyGapAtoms
			constraints += b.rulePointer.headGapAtoms
		else:
			constraints += a.rulePointer.headGapAtoms
			constraints += b.rulePointer.bodyGapAtoms
		
		for x in constraints:
			if (not x.checkTruthValueWithAssignment(mergedMap)):
				return False

		return True












