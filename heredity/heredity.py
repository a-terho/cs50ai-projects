import csv
import itertools
import sys
import math

# fmt: off
PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}
# fmt: on


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # fmt: off
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # fmt: on

    # Loop over all sets of people who might have the trait
    names = set(people)

    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
                # Second line means: if person has the trait, they need
                # to be in the have_trait set. If they don't have the
                #  trait, they must not be in the have_trait set.
                # Thus, have_trait will only have people with traits.
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):

            # This part will loop over opposite powersets from names,
            #  so all possible combinations of all people having any
            #  of the combinations of either 1 or 2 genes is checked
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """

    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False if row["trait"] == "0" else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """

    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def OR(*args: float) -> float:
    """
    Helper function for probability arithmetrics.

    Assumes mutual exclusivity for each argument, meaning they cannot happen at same time.
    """
    return sum(args)


def AND(*args: float) -> float:
    """
    Helper function for probability arithmetrics.

    Assumes indepedence for each argument, meaning they do not influence one another.
    """
    return math.prod(args)


def NOT(prob: float) -> float:
    """
    Helper function for probability arithmetrics.
    """
    return 1 - prob


def prob_person_passed_gene(person, permutation):
    """
    Calculate the probability that person passes the gene in given permutation:
    either a potential gene is passed unmutated or healthy gene is passed mutated.
    """

    # Assuming person does not have the gene, they have no potential to pass it on
    prob_gene_passing_potential = 0

    # But depending on given permutation of genes, there may be potential:
    # a. if person happens to have 1 gene, 50/50 chance happens
    # b. if person happens to have 2 genes, they will try to pass it on
    if person in permutation["one_gene"]:
        prob_gene_passing_potential = 0.5
    if person in permutation["two_genes"]:
        prob_gene_passing_potential = 1

    # Ultimately, whether they will pass the gene is a product of the potential
    #  and any chance of possible mutation that could happen during the process
    return OR(
        AND(prob_gene_passing_potential, NOT(PROBS["mutation"])),
        AND(NOT(prob_gene_passing_potential), PROBS["mutation"]),
    )


def prob_no_gene(person, people, permutation):
    """
    Calculate the probability of person having no genes in given permutation.
    """

    # Get person's parents
    mother = people[person]["mother"]
    father = people[person]["father"]

    # If person has no parents, use unconditional probability
    if not (mother and father):
        return PROBS["gene"][0]

    # Person will have no genes only if both parents don't pass the gene
    return AND(
        NOT(prob_person_passed_gene(mother, permutation)),
        NOT(prob_person_passed_gene(father, permutation)),
    )


def prob_one_gene(person, people, permutation):
    """
    Calculate the probability of person having one gene in given permutation.
    """

    # Get person's parents
    mother = people[person]["mother"]
    father = people[person]["father"]

    # If person has no parents, use unconditional probability
    if not (mother and father):
        return PROBS["gene"][1]

    # Person will have one only gene only if one of these possible worlds happen:
    # a. mother passes the gene and father does not
    # b. father passes the gene and mother does not
    # Both cases a and b cannot happen at the same time
    return OR(
        AND(
            prob_person_passed_gene(mother, permutation),
            NOT(prob_person_passed_gene(father, permutation)),
        ),
        AND(
            prob_person_passed_gene(father, permutation),
            NOT(prob_person_passed_gene(mother, permutation)),
        ),
    )


def prob_two_genes(person, people, permutation):
    """
    Calculate the probability of person having two genes in given permutation.
    """

    # Get person's parents
    mother = people[person]["mother"]
    father = people[person]["father"]

    # If person has no parents, use unconditional probability
    if not (mother and father):
        return PROBS["gene"][2]

    # Person will have two genes only when both parents pass the gene
    return AND(
        prob_person_passed_gene(mother, permutation),
        prob_person_passed_gene(father, permutation),
    )


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Function computes a single probability for above events happening within the
    #  given permutation of one_gene, two_genes and have_trait (a possible world)

    # Gather info about this possible world into a seperate dict
    possible_world = {
        "one_gene": one_gene,
        "two_genes": two_genes,
        # "have_trait": have_trait,
    }

    probabilities = []
    for person in people:

        # Probability that anyone in one_gene has one copy of the gene
        if person in one_gene:
            probabilities.append(prob_one_gene(person, people, possible_world))

            # With 1 gene, gather probability for having current trait status
            probabilities.append(PROBS["trait"][1][person in have_trait])

        # Probability that anyone in two_genes has two copies of the gene
        if person in two_genes:
            probabilities.append(prob_two_genes(person, people, possible_world))

            # With 2 genes, gather probability for having current trait status
            probabilities.append(PROBS["trait"][2][person in have_trait])

        # Probability that anyone in neither set doesn't have the gene
        if not (person in one_gene or person in two_genes):
            probabilities.append(prob_no_gene(person, people, possible_world))

            # With no genes, gather probability for having current trait status
            probabilities.append(PROBS["trait"][0][person in have_trait])

    # Return the probability of all events happening simultaneously
    return AND(*probabilities)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # For the given permutation of one_gene, two_genes and have_trait (a possible
    #  world), store the calculated probability of that possible world happening

    # Function takes advantage of rule for marginalizing probability distributions:
    #  a probability distribution is the sum of each of those probabilities where a
    #  certain possible world within the distribution occurs

    for person in probabilities:

        # First, distribute the probability for gene count
        # These all should be mutually exclusive (no elif should be needed)
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        if person not in one_gene and person not in two_genes:
            probabilities[person]["gene"][0] += p

        # Second, distribute the probability for the trait status
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        for dist in probabilities[person].keys():
            # Calculate the sum of all values in the distribution
            # From that, calculate normalizing factor (alpha)
            sum_dist = sum(probabilities[person][dist].values())
            alpha_dist = 1 / sum_dist

            # Then, normalize the dictionary accordingly
            for key in probabilities[person][dist].keys():
                probabilities[person][dist][key] *= alpha_dist


if __name__ == "__main__":
    main()
