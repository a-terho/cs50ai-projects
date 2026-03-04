import sys
import random

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """

        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
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
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """

        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    ######
    ## Implementation

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Loop through all the variables in current crossword
        for var in self.domains:

            # Create a set containing words not following variable's unary constraints
            discard = {word for word in self.domains[var] if len(word) != var.length}

            # Remove those words from variable's domain
            self.domains[var] -= discard

            # Alternative way...
            # # Create a list copy for looping (and safely modifying) the domain
            # for word in list(self.domains[var]):

            #     # Remove words from the domain that don't fit unary constraints
            #     if len(word) != var.length:
            #         self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Binary constraints for any variables x and y in a crossword puzzle are:
        # 1. Words representing x and y must be different (word_x != word_y)
        # 2. Those two words, when overlapping, must overlap with same letters

        # Find possible overlap for these variables
        overlap = self.crossword.overlaps[x, y]

        revised = False

        # Loop through a list copy of words in the domain (for safe removals)
        for word_x in list(self.domains[x]):
            if overlap:
                # overlap is a tuple where [0] is the location of overlapping
                #  char in var x and [1] is the location of that char in var y

                # If there aren't any words in y's domain where the overlapping
                #  chars aren't equal when the words for x and y are different,
                #  there is no word_y that satisfies constraints for current word_x
                if not any(
                    word_x != word_y and word_x[overlap[0]] == word_y[overlap[1]]
                    for word_y in self.domains[y]
                ):
                    self.domains[x].remove(word_x)
                    revised = True
            else:

                # If there is no overlap, constraint for (x, y) pair is narrower
                if not any(word_x != word_y for word_y in self.domains[y]):
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
            arcs = []

            # Any arc within the crossword puzzle is formed from an overlap of two
            #  variables. These overlaps are stored in keys of crossword.overlaps
            for v1, v2 in self.crossword.overlaps.keys():
                arcs.append((v1, v2))

        # Start iterating the list of arcs
        while arcs:

            # Grab first arc from the list and shift it (implements queue structure)
            (x, y) = arcs[0]
            arcs = arcs[1:]

            # Ensure arc consistency for edge x-y. If revisions are made, do evaluation.
            if self.revise(x, y):

                # If due to revision, x's domain was completely cleared, there
                #  is no solution for this crossword and we may stop iteration
                if len(self.domains[x]) == 0:
                    return False

                # Otherwise, for each neighbor of x (that is, any variable that
                #  overlaps with x), excluding y that was already checked...
                for z in self.crossword.neighbors(x) - {y}:

                    # Add edge z-x to the queue for revision
                    arcs.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Assigment is complete when for every variable in crossword, there is
        #  some value assigned. All crossword variables are stored in self.domains

        if len(assignment) != len(self.domains):
            return False

        for var in self.domains:
            if var not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check whether all assigned words are of correct length (unary constraint)
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # Check that all assigned words are distinct (binary constraint). If there are
        #  any duplicate words, a set created from these words will be smaller size.
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # Check if there are conflicts between neighboring variables (binary constaint)
        for v1 in assignment:
            for v2 in self.crossword.neighbors(v1):

                # Skip those neighbors that haven't been assigned any value yet
                if v2 not in assignment:
                    continue

                # Find the overlap of these two variables (there should always be one)
                overlap = self.crossword.overlaps[v1, v2]

                # By this point, all the words should be distinct. So we need to only
                #  check that the words actually overlap with correct letters
                if assignment[v1][overlap[0]] != assignment[v2][overlap[1]]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Create a set with all yet unassigned neighbors of var
        neighbors = self.crossword.neighbors(var) - set(assignment)

        # Then, for every possible value (word) that could be assigned for var,
        #  check how many constraints each choice creates for each of its neighbors
        constraints = dict()
        for word in self.domains[var]:

            constraints[word] = 0
            for neighbor in neighbors:

                # overlap is a tuple where [0] is the location of overlapping
                #  char in var and [1] is the location of that char in neighbor
                overlap = self.crossword.overlaps[var, neighbor]

                # Create a filtered list from the neighbour's domain (possible words)
                # Filtered out words don't fit binary constraints:
                # 1. Words must be different
                # 2. As words will overlap, they must overlap with same letters
                possible_word_choices = list(
                    filter(
                        lambda w: word != w and word[overlap[0]] == w[overlap[1]],
                        [w for w in self.domains[neighbor]],
                    )
                )

                # Calculate how many words are filtered from neighbor's domain
                num_filtered = len(self.domains[neighbor]) - len(possible_word_choices)
                constraints[word] += num_filtered

        # After looping all possible word choices for var, sort the domain in asceding
        #  order according to how many constraints each word creates for all its
        #  neighbors. Domain will then obey the least constraining value heuristic.
        domain = list(self.domains[var])

        # Add additional shuffle to allow any words with equal amount of constraints
        #  to appear in different order even after sorting (adds variety to crosswords)
        random.shuffle(domain)

        domain.sort(reverse=False, key=lambda word: constraints[word])
        return domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # All crossword variables have keys in self.domains and all assigned variables
        #  have keys in assignment. Unassigned variables is the difference of these sets
        unassigned_vars = set(self.domains) - set(assignment)

        # We may assume unassigned_vars won't be an empty set (project specification)
        # Early exit clause: If there's only one unassigned variable, it's the only choice
        if len(unassigned_vars) == 1:
            return unassigned_vars.pop()

        # Primary criteria: minimun remaining values heuristic

        # Create an ordered list of variables based on their domain size
        ordered_vars = sorted(
            list(unassigned_vars), reverse=False, key=lambda var: len(self.domains[var])
        )

        # Leading variable with the smallest domain is now at head of the list. If there
        #  is no tie between the sizes of domains for the first two variables (= their
        #  sizes are different), we can just return the leading variable
        leading_var, second_var = ordered_vars[0], ordered_vars[1]
        if len(self.domains[leading_var]) != len(self.domains[second_var]):
            return leading_var

        # Otherwise, use secondary criteria: degree heuristic

        # First, filter out any variable that isn't tying with the leading variable
        tying_vars = list(
            filter(
                lambda var: len(self.domains[var]) == len(self.domains[leading_var]),
                ordered_vars,
            )
        )

        # Then, order this list of remaining variables according to number of their
        #  neighbours in descending order (= variable with the most neighbors is at
        #  the head of the list)
        tying_vars.sort(
            reverse=True, key=lambda var: len(self.crossword.neighbors(var))
        )

        # Finally, filter out any remaining variables that are not trying with current
        #  leading variable after the second sort. These now are the best choices
        leading_var = tying_vars[0]
        best_choices = list(
            filter(
                lambda var: len(self.crossword.neighbors(var))
                == len(self.crossword.neighbors(leading_var)),
                tying_vars,
            )
        )

        # Return any of these best choices
        return random.choice(best_choices)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # If the assignment is complete, we have a solution
        if self.assignment_complete(assignment):
            return assignment

        # Select a variable from the assignment for the search process
        var = self.select_unassigned_variable(assignment)

        # Loop through all the possible words in variable's domain in order
        #  according to the least constraining value heuristic
        for word in self.order_domain_values(var, assignment):

            # Create a copy of current assignment and assign this word to variable
            new_assignment = assignment.copy()
            new_assignment[var] = word

            # Check if the new assignment is still consistent knowing the constraints
            if self.consistent(new_assignment):

                # Using inference makes the search problem more efficient
                # We can maintain arc consistency for the problem after every consistent
                #  assignment. Arc consistency should be maintained for all neighboring
                #  variables of currently processed variable.

                # First, we need to remove all other words from current variables domain
                #  because current word is now truly assigned and it is the only choice
                self.domains[var].clear()
                self.domains[var].add(word)

                # After that, create a list of all arcs leading to current variable. The
                #  arcs come from current variable's neighbouring variables
                arcs = []
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((neighbor, var))

                # Calling ac3 will enforce arc consistency for current problem and it will
                #  modify any variable's domain so that each of them is arc consistent. If
                #  the algorithm fails, a domain has been cleared and there is no solution
                if not self.ac3(arcs):
                    return None

                # If there's still a solution, use new assignment in next recursive search
                result = self.backtrack(new_assignment)

                # Result will be a completed assignment that uses current
                #  [var] = word combo if there was any possible assignment
                if result is not None:
                    return result

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
