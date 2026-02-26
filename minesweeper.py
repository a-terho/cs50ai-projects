import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    # Receives input the form: [cell, cell, cell], mine_count
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # If the size of the self.cells is equal to the mine count
        #  in that set, then each item in the set is a mine
        if len(self.cells) == self.count:
            print("Returning", len(self.cells), "mines...")
            return self.cells

        # Otherwise, there is no 100 % certainty for which of the
        #  cells in current set are mines. This also covers the case,
        #  where mine count is 0 -> known mines is an empty set.
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # If the self.cells does not have any mines (mine count = 0),
        #  then each item in the set is safe
        if self.count == 0:
            return self.cells

        # Otherwise, there is no 100 % certainty for which of the cells
        #  in current set are safe. This also covers the case, where
        #  mine count = size of self.cells -> known safes is an empty set.
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            # If this sentence already contains only the information that
            #  this single cell is mine, there is no need to do anything.
            # BUG Should this be the action?
            # if self.count == 1 and len(self.cells) == 1:

            # Only mark sentences that are not already full of mines
            if len(self.cells) == self.count:
                print("Not going to remove", cell, "from this sentence full of mines")
                return

            # Otherwise, there is something to update. We want to remove
            #  that mine cell from the set and update the count of mines
            #  in this set accordingly.
            self.cells.remove(cell)
            self.count -= 1

        # If provided cell is not in self.cells, do nothing
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            # If this sentence already contains only the information that
            #  this single cell is safe, there is no need to do anything.
            # BUG Should this be the action?
            # if self.count == 0 and len(self.cells) == 1:

            # Only mark safes in sentences that have mines in them
            if self.count == 0:
                return

            # Otherwise, there is something to update. We want to remove
            #  that safe cell from the set. Mine count stays the same.
            self.cells.remove(cell)

        # If provided cell is not in self.cells, do nothing
        return


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        print("Plannning to add knowledge:", cell, count, "...")
        print("Inferred mines thus far:", self.mines)

        # Add current cell as one of the moves made
        self.moves_made.add(cell)

        # Mark current cell as a safe cell
        # Method will propagate this knowledge to other sentences, too
        self.mark_safe(cell)

        # To contruct the sentence, we need to know the neigbouring
        #  cells of the current cell. We're only provided with the
        #  knowledge of mine count in this set of neighbouring cells.
        # First, find all the possible neighbours and then out of
        #  those, leave only the cells which have not already been
        #  marked as safe cells as those cannot be mines.
        neighbours = self.neighbours(cell)
        cells = neighbours - self.safes

        # print("Unexplored neighbour cells:", cells, "size:", len(cells))

        # Now the set contains only the unexplored cells, some of which
        #  could be mines. We can check whether any of the known mines
        #  are within this set using the intersection operator.
        known_mine_cells = cells & self.mines

        # If there are any known mines in this set, we can just remove
        #  them from this sentence as it does not bring new information
        if known_mine_cells:
            print(
                "Planning to add:",
                cells,
                count,
                "but removing",
                len(known_mine_cells),
                "mines first",
            )
            cells -= known_mine_cells
            count -= len(known_mine_cells)

        # Everything up to this point should be correct!

        # Add this new knowledge (sentence) if there is any information
        if cells:

            print(
                "KB:",
                [str(sentence) for sentence in self.knowledge],
                "size:",
                len(self.knowledge),
            )

            # Only add unique sentences to knowledge base
            sentence = Sentence(cells, count)
            if sentence not in self.knowledge:

                print("Adding knowledge:", sentence)
                self.knowledge.append(sentence)

                # Having this knowledge, check whether there are new known
                #  mines or new known safes that haven't been marked yet.
                self.update_safes_mines()

                print(
                    "KB after safes_mines:",
                    [str(sentence) for sentence in self.knowledge],
                    "size:",
                    len(self.knowledge),
                    "self.mines:",
                    self.mines,
                    "self.safes:",
                    self.safes,
                )

                # Having this knowledge, check the knowledge base if we can
                #  infer more knowledge. We are trying to find whether some
                #  sentences have subsets of other sentence's sets. This way
                #  we can infer new knowledge on the minesweeper board.
                #  Do this as long as any new knowledge can be infered from
                #  any new knowledge that was created. Infer method will
                #  eventually return an empty list which will evaluate False

                while self.infer_new_knowledge():
                    print(
                        "Inferred some new knowledge, knowledge base size:",
                        len(self.knowledge),
                    )
                    # self.knowledge += new_knowledge

                    self.update_safes_mines()
            else:
                print("Skipping new sentence:", sentence)

        print(
            "KB now:",
            [str(sentence) for sentence in self.knowledge],
            "size:",
            len(self.knowledge),
        )
        print("Inferred mines after knowledge:", self.mines)
        print("---")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Create a set with safe moves that have not already been made
        safe_choices = self.safes - self.moves_made

        # Pick one of these moves
        # Empty sets will throw KeyError on .pop()
        try:
            choice = safe_choices.pop()
        except KeyError:
            choice = None

        return choice

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # First create a set with all possible moves (cells)
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i, j))

        # Out of these cells, remove all moves that are not allowed
        allowed_choices = all_moves - self.moves_made - self.mines

        if not allowed_choices:
            return None
        else:
            # Because sets are deterministic, we need to create a list
            #  out of the remaining set to actually get a random move
            choices = list(allowed_choices)
            choice = random.choice(choices)

            return choice

    def neighbours(self, cell):
        """
        Returns a set that contains all cells that are neighbouring given cell.
        """

        # Initialize empty set
        neighbour_cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Add only cells that are inside the minesweeper board
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbour_cells.add((i, j))

        return neighbour_cells

    def infer_new_knowledge(self):
        """
        Infers new knowledge on the minesweeper board from given knowledge
        and returns a list of new knowledge if there is anything to infer.
        """

        # Any time we have two sentences set1 = count1 and set2 = count2
        #  where set1 is a subset of set2, then we can construct the new
        #  sentence set2 - set1 = count2 - count1
        # So, cross-reference each sentence in knowledge base with each other

        """
        inferred_knowledge = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:

                # Don't cross reference same sentence
                if sentence1 == sentence2:
                    print(
                        "A duplicate sentence",
                        sentence1,
                        "was found - skipping",
                    )
                    continue

                if sentence1.cells.issubset(sentence2.cells):
                    # Create a new sentence
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)

                    # Only add unique sentences to knowledge base
                    if new_sentence in self.knowledge:
                        print("Skipping new inferred sentence", new_sentence)
                        continue

                    print("Adding:", new_sentence)
                    inferred_knowledge.append(new_sentence)
        
        """

        # First, create a sorted list from the knowledge base based on len(self.cells)
        sorted_knowledge = sorted(
            self.knowledge, key=lambda sentence: len(sentence.cells)
        )

        inferred_knowledge = []
        sentences_to_remove = []

        print("Starting to infer...")

        # Subsets must be smaller than the sets they are contained in
        # So for every possible subset, only check the sets that are larger
        for i, sentence1 in enumerate(sorted_knowledge):
            for sentence2 in sorted_knowledge[i + 1 :]:
                if sentence1.cells.issubset(sentence2.cells):
                    if sentence1 == sentence2:
                        print(
                            "A duplicate sentence",
                            sentence1,
                            "was found for",
                            i,
                            "- skipping",
                        )
                        continue

                    # Create a new sentence
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)

                    # Only add unique sentences to knowledge base
                    if new_sentence in self.knowledge:
                        print("Skipping new inferred sentence", new_sentence)
                        continue

                    print(
                        "From:",
                        sentence2,
                        "and",
                        sentence1,
                    )

                    if not new_cells:
                        raise Exception(
                            "Attempting to add an empty set to KB - disallowing"
                        )
                    else:
                        print("Inferring:", new_sentence)
                        inferred_knowledge.append(new_sentence)

                        # TODO If inferred sentence is len 1, sentence2 can be deleted as it will only be a duplicate of sentence1, because after the  inferred sentence is added to the knowledge base, it will remove itself from this sentence2 anyway
                        # TODO Maybe is inferred sentence is len == count and count or if count == 0

                        # We can remove the sentence with the bigger sentence from the
                        #  knowledge base as we have more specific information available.
                        #  This condenses the information in the knowledge base.
                        # sentences_to_remove.append(sentence1)
                        # sentences_to_remove.append(sentence2)

        # If there was any inferred knowledge..
        if inferred_knowledge:
            # print("Removing", len(sentences_to_remove), "sentences")
            print("Adding", len(inferred_knowledge), "sentences")

            # Filter out rows from the knowledge base that were marked for removal
            # new_knowledge = list(
            #     filter(
            #         lambda sentence: not sentence in sentences_to_remove, self.knowledge
            #     )
            # )
            # self.knowledge = new_knowledge

            # Add the new inferrec knowledge to knowledge base
            self.knowledge += inferred_knowledge
            return True

        return False

    def update_safes_mines(self):
        """
        Updates the sets containing known mines and safes based on current knowledge.
        """

        # In order for this to work and find all mines and safes, this needs recursion.
        # First, you mark all safes and mines from the sentences. After that, you keep
        #  looping through them again to see if there are changes made sentences. If
        #  you do this in one same loop, some mines and safes will not be found.
        #  This was a source one difficult to find bug for me.

        needs_verifying = True
        while needs_verifying:

            # Exit loop unless something requires it to continue
            needs_verifying = False

            mark_safes = []
            for sentence in self.knowledge:

                # Find all certain safes
                # Then select only those that are not already known
                safes = sentence.known_safes()
                new_safes = safes - self.safes

                # Add these to a list
                mark_safes += list(new_safes)

            for safe in mark_safes:
                needs_verifying = True
                print("Marking new safe: ", safe)
                self.mark_safe(safe)

            mark_mines = []
            for sentence in self.knowledge:

                # Process is the same here
                mines = sentence.known_mines()
                new_mines = mines - self.mines

                mark_mines += list(new_mines)

            for mine in mark_mines:
                needs_verifying = True
                print("Marking new mine: ", mine)
                self.mark_mine(mine)
