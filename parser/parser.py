import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP V | NP VP | NP Adv VP
S -> S Conj S | S Conj VP
NP -> N | Det N | Det AdjN | NP P NP
AdjN -> Adj N | Adj AdjN
VP -> V NP | V NP Adverbial | V Adverbial | V Adv
Adverbial -> P NP | Adverbial Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Tokenize sentence with nltk
    tokens = nltk.tokenize.word_tokenize(sentence)

    # Filter out tokens with no alphanumerics and turn each word to lowercase
    words = [
        word.lower()
        for word in filter(
            lambda token: any(letter.isalpha() for letter in token), tokens
        )
    ]
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    if not contains_np(tree):
        return []

    # Look for other any noun phrases inside possible subtrees
    subtree_nps = []
    for subtree in tree:
        if type(subtree) == nltk.Tree:
            subtree_nps += np_chunk(subtree)

    # If current tree is a noun phrase, we can only return it if it
    #  didn't contain any subtrees with other noun phrases in them
    if tree.label() == "NP" and len(subtree_nps) == 0:
        return [tree]
    else:
        return subtree_nps


def contains_np(tree):
    """Checks whether current tree contains any non-terminals with label "NP"."""

    if tree.label() == "NP":
        return True

    return any([contains_np(subtree) for subtree in tree if type(subtree) == nltk.Tree])


if __name__ == "__main__":
    main()
