import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        removeList = []
        for variable, valueList in self.domains.items():
            for value in valueList:
                if not len(value) == variable.length:
                    removeList.append((variable, value))
        for removeTuple in removeList:
            self.domains[removeTuple[0]].remove(removeTuple[1])

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revise = False
        removeList = []
        overlap = self.crossword.overlaps[x,y]
        if overlap:
            xOverlap = overlap[0]
            yOverlap = overlap[1]
        else:
            return revise
        for xValue in self.domains[x]:
            condSatisfied = False
            for yValue in self.domains[y]:
                if xValue[xOverlap] == yValue[yOverlap]:
                    condSatisfied = True
                    break
            if condSatisfied:
                continue #go to next X value
            else: # no satisfying y value
                removeList.append(xValue)
                revise = True
        for xValue in removeList:
            self.domains[x].remove(xValue)

        return revise        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []#append and pop(0)
        if not arcs:
            for variable in self.domains:
                for neighbor in self.crossword.neighbors(variable):
                    if (variable, neighbor) not in queue and (neighbor, variable) not in queue:
                        queue.append((variable, neighbor))
        else:
            queue = arcs
        while queue:
            tupleVar = queue.pop(0)
            x = tupleVar[0]
            y = tupleVar[1]
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for n in self.crossword.neighbors(x):
                    if not n == y and (x, n) not in queue and (n, x) not in queue:
                        queue.append((x, n))
        return True
        
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if not variable in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = []
        
        for variable, value in assignment.items():
            #check for unary constraints
            if not variable.length == len(value):
                return False
            #check for binary constraints: duplicate words, overlap
            if value in words:
                return False
            else:
                words.append(value)
            for n in self.crossword.neighbors(variable):
                if n in assignment:
                    overlapTuple = self.crossword.overlaps[variable, n]
                    if not value[overlapTuple[0]] == assignment[n][overlapTuple[1]]:
                        return False
        return True
                    

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        valList = []
        for val in self.domains[var]:
            valScore = 0
            for n in self.crossword.neighbors(var):
                if n not in assignment:
                    overlap = self.crossword.overlaps[var, n]
                    for nVal in self.domains[n]:
                        if not val[overlap[0]] == nVal[overlap[1]]:
                            valScore += 1
            valList.append((valScore, val))
        orderedList = []
        valList.sort()
        for tupleVar in valList:
            orderedList.append(tupleVar[1])
        return orderedList


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        tupleList = []
        varList = []
        for var in self.domains:
            if not var in assignment:
                tupleList.append((len(self.domains[var]), -1*len(self.crossword.neighbors(var)), len(varList)))
                #tuple(nb_values, nb_neighbors, variable_index)
                varList.append(var)
        tupleList.sort()

        return varList[tupleList[0][2]]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            ###add inference
            #save the current values for neighbors and var
            
            originalVals = {}
            originalVals[var] = self.domains[var]
            arcs = []
            for n in self.crossword.neighbors(var):
                originalVals[n] = self.domains[n]
                arcs.append((var, n))
            
            #change var values to only be selected value
            self.domains[var] = [value]
            
            #apply ac3 on the neighbors of var
      
            if self.ac3(arcs) and self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            assignment.pop(var, None)
            
            ###remove inference
            #restore previous values for neighbors and var
            for originalVar, originalVal in originalVals.items():
                self.domains[originalVar] = originalVal
                
        return None
    
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
