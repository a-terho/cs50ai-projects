from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Common contraints for every knowledge base
# Each person be either knight or knave but not both
# This is basically Xor(Knight, Knave)
AConstraint = And(Or(AKnight, AKnave), Not(And(AKnight, AKnave)))
BConstraint = And(Or(BKnight, BKnave), Not(And(BKnight, BKnave)))
CConstraint = And(Or(CKnight, CKnave), Not(And(CKnight, CKnave)))
CommonConstraints = And(AConstraint, BConstraint, CConstraint)

# Puzzle 0
# A says "I am both a knight and a knave."
ProposementA0 = And(AKnight, AKnave)
knowledge0 = And(
    CommonConstraints,
    # Implying that someone has said something is tricky. It was easier to
    #  think of this by adding a temporary symbol P = "A's proposement",
    #  then embed that when A is knight, this proposement is true and when
    #  A is knave, this proposement is false. After setting up the logic,
    #  just replace P's with the content of those proposements.
    Implication(AKnight, ProposementA0),
    Implication(AKnave, Not(ProposementA0)),
)

# Puzzle 1
# A says "We are both knaves."
ProposementA1 = And(AKnave, BKnave)
# B says nothing.
knowledge1 = And(
    CommonConstraints,
    # Again, A being knight implies their proposition is true
    # If A is knave, the proposition is false
    Implication(AKnight, ProposementA1),
    Implication(AKnave, Not(ProposementA1)),
)

# Puzzle 2
# A says "We are the same kind."
ProposementA2 = Or(And(AKnight, BKnight), And(AKnave, BKnave))
# B says "We are of different kinds."
ProposementB2 = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    CommonConstraints,
    # Same thing again, but now that both are speaking, we need
    #  to tell the same thing about both people.
    Implication(AKnight, ProposementA2),
    Implication(AKnave, Not(ProposementA2)),
    Implication(BKnight, ProposementB2),
    Implication(BKnave, Not(ProposementB2)),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
ProposementA3 = Or(AKnight, AKnave)
# B says "A said 'I am a knave'."
# B says "C is a knave."
ProposementB3a = And(ProposementA3, AKnave)  # what A said + what is claimed to be said
ProposementB3b = CKnave
ProposementsB3 = And(ProposementB3a, ProposementB3b)  # combine B's proposements
# C says "A is a knight."
ProposementC3 = AKnight
knowledge3 = And(
    CommonConstraints,
    # Same thing for all people
    Implication(AKnight, ProposementA3),
    Implication(AKnave, Not(ProposementA3)),
    Implication(BKnight, ProposementsB3),
    Implication(BKnave, Not(ProposementsB3)),
    Implication(CKnight, ProposementC3),
    Implication(CKnave, Not(ProposementC3)),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
