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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
      for var in self.domains:
         for word in set(self.domains[var]):
            if len(word) != var.length:
                self.domains[var].remove(word)
    
    def revise(self, x, y):
      revised = False
      overlap = self.crossword.overlaps.get((x, y))
      if overlap is not None:
        i, j = overlap
        for word_x in set(self.domains[x]):
            if all(word_x[i] != word_y[j] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True
                
      return revised
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
          arcs = [(x, y) for x in self.domains for y in self.crossword.neighbors(x)]
    
        queue = arcs[:]
        while queue:
          (x, y) = queue.pop(0)
          if self.revise(x, y):
            if not self.domains[x]:
                return False
            for z in self.crossword.neighbors(x) - {y}:
                queue.append((z, x))
        return True
        

    def assignment_complete(self, assignment):
       
       
        return set(assignment.keys()) == set(self.crossword.variables)

        

    def consistent(self, assignment):
      
   
        if len(set(assignment.values())) != len(assignment):
          return False
    
   
        for var, word in assignment.items():
         if len(word) != var.length:
            return False

     
        for var in assignment:
          for neighbor in self.crossword.neighbors(var):
             if neighbor in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                if assignment[var][i] != assignment[neighbor][j]:
                    return False

        return True


    def order_domain_values(self, var, assignment):
      
     def count_conflicts(value):
        conflicts = 0
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                for neighbor_value in self.domains[neighbor]:
                    if value[i] != neighbor_value[j]:
                        conflicts += 1
        return conflicts

     return sorted(self.domains[var], key=count_conflicts)


    def select_unassigned_variable(self, assignment):
     
     unassigned = [v for v in self.crossword.variables if v not in assignment]

     def mrv(v):
        return len(self.domains[v])

     def degree(v):
        return len(self.crossword.neighbors(v))

     return min(unassigned, key=lambda var: (mrv(var), -degree(var)))


    def backtrack(self, assignment):
        
     if self.assignment_complete(assignment):
        return assignment

     var = self.select_unassigned_variable(assignment)
     for value in self.order_domain_values(var, assignment):
        assignment[var] = value
        if self.consistent(assignment):
            result = self.backtrack(assignment)
            if result:
                return result
        del assignment[var]

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
