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

        # Only if all the cells are marked as mines, are all mines known
        if len(self.cells) == self.count:
            return self.cells

        # Otherwise, there is no 100 % certainty for which of the
        #  cells in current set are mines. This also covers the case,
        #  where mine count is 0 -> known mines is an empty set.
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # Only if there are no mines in the set, all cells are safe
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

            # Only mark sentences that are not already full of mines
            if len(self.cells) == self.count:
                return

            # Remove mine cell from the set and update mine count accordingly
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

            # Only mark safes in sentences that have mines in them
            if self.count == 0:
                return

            # Remove the safe cell from this sentence, nothing else to update
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

        # Add current cell as one of the moves made
        self.moves_made.add(cell)

        # Mark current cell as a safe cell
        # Method will propagate the knowledge to all other sentences, too
        self.mark_safe(cell)

        # To contruct the sentence, we need to know the neigbouring
        #  cells of the current cell. We're only provided with the
        #  knowledge of mine count in this set of neighbouring cells.
        # First, find all the possible neighbours and then out of
        #  those, leave only the cells which have not already been
        #  marked as safe cells as those cannot be mines.
        neighbours = self.neighbours(cell)
        cells = neighbours - self.safes

        # Now the set contains only the unexplored cells, some of which
        #  could be mines. We can check whether any of the known mines
        #  are within this set using the intersection operator.
        known_mine_cells = cells & self.mines

        # If there are any known mines in this set, we can just remove
        #  them from this sentence as it does not bring new information
        if known_mine_cells:
            cells -= known_mine_cells
            count -= len(known_mine_cells)

        # TODO Maybe remove cells.moves_made from this set also?

        # Only add this new knowledge (sentence) if there is any information
        if cells:

            # Only add unique sentences to knowledge base
            sentence = Sentence(cells, count)
            if sentence not in self.knowledge:
                self.knowledge.append(sentence)

                # Having this knowledge, check whether there are new known
                #  mines or new known safes that haven't been marked yet.
                self.update_safes_mines()

                # Having this knowledge, check the knowledge base if we can
                #  infer more knowledge. We are trying to find whether some
                #  sentences have subsets of other sentence's sets.
                #  Do this as long as any new knowledge can be infered from
                #  any new knowledge that was created.
                while self.infer_new_knowledge():
                    self.update_safes_mines()

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

        # If there are no allowed moves left, return nothing
        if not allowed_choices:
            return None

        # Because sets are deterministic, we need to create a list
        #  out of the remaining set to actually get a random move
        choices = list(allowed_choices)
        choice = random.choice(choices)

        return choice

    def neighbours(self, cell):
        """
        Returns a set that contains all cells that are neighbouring given cell.
        """

        neighbour_cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Only add cells that are inside the minesweeper board
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

        # First, create a sorted list from the knowledge base based on len(self.cells)
        sorted_knowledge = sorted(
            self.knowledge, key=lambda sentence: len(sentence.cells)
        )

        inferred_knowledge = []
        sentences_to_remove = []

        # Subsets must be smaller than the sets they are contained in
        # So for every possible subset, only check the sets that are larger
        for i, sentence1 in enumerate(sorted_knowledge):
            for sentence2 in sorted_knowledge[i + 1 :]:
                if sentence1.cells.issubset(sentence2.cells):
                    if sentence1 == sentence2:
                        # print(
                        #     "A duplicate sentence",
                        #     sentence1,
                        #     "was found for",
                        #     i,
                        #     "- skipping",
                        # )
                        continue

                    # Create a new sentence
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)

                    # Only add unique sentences to knowledge base
                    if new_sentence in self.knowledge:
                        continue

                    # print(
                    #     "From:",
                    #     sentence2,
                    #     "and",
                    #     sentence1,
                    # )

                    if not new_cells:
                        raise Exception("attempting to add an empty set to KB")
                    else:
                        # print("Inferring:", new_sentence)
                        inferred_knowledge.append(new_sentence)

                        # TODO This may still create duplicate entries if similar info
                        #  can be inferred from different sentences. Duplicates are
                        #  skipped above so this doesn't really cause any problems.

                        # We can condense information in the knowledge base by removing
                        #  one of the sentences from which we could infer this new
                        #  information. Otherwise, there will eventually be repeating
                        #  sentences in the KB as updating safes and mines will modify
                        #  these sentences anyway
                        sentences_to_remove.append(sentence2)

        # If there was any inferred knowledge..
        if inferred_knowledge:

            # Remove some repetition from knowledge base
            if sentences_to_remove:

                # Filter out rows from the knowledge base that were marked for removal
                new_knowledge = list(
                    filter(
                        lambda sentence: not sentence in sentences_to_remove,
                        self.knowledge,
                    )
                )

                # print("Removing", len(sentences_to_remove), "sentences")
                self.knowledge = new_knowledge

            # Add the new inferred knowledge to knowledge base
            # print("Adding", len(inferred_knowledge), "sentences")
            self.knowledge += inferred_knowledge
            return True

        return False

    def update_safes_mines(self):
        """
        Updates the sets containing known mines and safes based on current knowledge.
        """

        # In order for this to work and find all mines and safes, this needs recursion.
        # First, you mark all safes and mines from the sentences. If any marks were made,
        #  you keep looping through sentences again to see if it caused any clear mines or
        #  safes to appear into any sentences. If you did this only in one same loop,
        #  some mines and safes wouldn't be found. This was a source to one difficult to
        #  find bug for me. TODO This could probably be done more efficiently...

        re_evaluate = True
        while re_evaluate:

            # Exit loop unless something forces it to continue
            re_evaluate = False

            mark_safes = []
            for sentence in self.knowledge:

                # Find all certain safes
                # Then select only those that are not already known
                safes = sentence.known_safes()
                new_safes = safes - self.safes

                # Add these to a list
                mark_safes += list(new_safes)

            # It's important to do this in outside loop so self.safes is updated correctly
            for safe in mark_safes:
                self.mark_safe(safe)
                re_evaluate = True

            mark_mines = []
            for sentence in self.knowledge:

                # Process is the same here
                mines = sentence.known_mines()
                new_mines = mines - self.mines

                mark_mines += list(new_mines)

            for mine in mark_mines:
                self.mark_mine(mine)
                re_evaluate = True
