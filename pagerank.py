import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """

    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # This transition model is a Markov model (assumes that the probability of
    #  choosing any link the page is only dependent on current page the user is in).

    probabilities = dict()
    num_pages = len(corpus)
    num_outgoing_pages = len(corpus[page])

    # If there are no outgoing pages in given page, create a simple probability
    #  distribution with equal weights over all the possible pages in the given corpus
    if num_outgoing_pages == 0:

        for page_name in corpus:
            probabilities[page_name] = 1 / num_pages
        return probabilities

    # Otherwise, loop over all the outgoing pages of given page
    for outgoing_page_name in corpus[page]:

        # Any one of all the outgoing pages is selected with the probability
        #  of damping factor. So for each outgoing page, give a probability
        #  of damping factor / outgoing page count.
        probabilities[outgoing_page_name] = damping_factor / num_outgoing_pages

    # And for all pages in the corpus (both the ones that are not linked
    #  and those that are linked from this page) give (an additional) equal
    #  probability of (1 - damping factor) / total page count
    for page_name in corpus:

        # Initialize any unspecified keys for math operation
        if not page_name in probabilities:
            probabilities[page_name] = 0

        probabilities[page_name] += (1 - damping_factor) / num_pages

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize dict for counting page visits
    page_visits = {page_name: 0 for page_name in corpus}

    # Select starting page at random (page names are specified as keys in corpus)
    page_name = random.choice(list(corpus.keys()))

    # Start sampling
    for _ in range(n):

        # Generate the probability distribution for current page
        probabilities = transition_model(corpus, page_name, damping_factor)

        # Generate linked lists for sampling using probabilities as weights
        pages, weights = zip(*probabilities.items())

        # Then, choose the next page using these weights
        # Along with that, keep track of the number of page visit
        page_name = random.choices(population=pages, weights=weights, k=1)[0]
        page_visits[page_name] += 1

    # After sampling, generate the PageRanks
    # This is done by turning the number of visits into proportions of all total visits
    pageranks = {page_name: count / n for page_name, count in page_visits.items()}

    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    num_pages = len(corpus)
    page_names = list(corpus.keys())

    # First, we need to create a new dict which holds the information of all
    #  other pages that link to that given page. corpus currently holds the
    #  opposite information. O(n^2) for loop seems to be a way to do this...

    pages_linking_to = dict()
    for page_name in page_names:

        # Initialize the set for inbound pages
        pages_linking_to[page_name] = set()
        for linking_page_name in page_names:

            # If there's a link to the current page on some other page that
            #  has any links to some other pages, add page this to the set
            if page_name in corpus[linking_page_name]:
                pages_linking_to[page_name].add(linking_page_name)

            # Alternatively, if there are no links on this other page,
            #  assume it has one link for every possible page in the corpus,
            #  including a link for current page (project specification)
            elif len(corpus[linking_page_name]) == 0:
                pages_linking_to[page_name].add(linking_page_name)

    # Initialize PageRanks
    pageranks = {page_name: 1 / num_pages for page_name in page_names}

    # Define the function that calculates PageRank for a page
    def pagerank(page, corpus, d):

        # PageRank of any page is a sum of two factors
        # Factor 1: User landed randomly to current page

        # That means, a random choice among equally likely choices was the current
        # page. This factor is weighted according to inverse of the damping factor.
        factor1 = 1 / num_pages * (1 - d)

        # Factor 2: User followed a link from a linking page to current page

        # Initialize the second factor
        factor2 = 0

        # Get the set of unique pages linking to given page
        incoming_pages = pages_linking_to[page]

        # Calculate the probability of being at any of those linking
        #  pages. This is the current PageRank for that page.
        for incoming_page in incoming_pages:
            P_at_incoming_page = pageranks[incoming_page]

            # Get the number of unique links of said linking page
            num_links = len(corpus[incoming_page])

            # If there are no links on that page, assume it has a link to
            #  every possible page in the corpus (project specification)
            if num_links == 0:
                num_links = num_pages

            # Assume there is an equal probability on clicking any
            #  of the links on that linking page. Add this probability
            #  to the total sum of probabilities that the user reached the page.
            P_follows_link_to_page = P_at_incoming_page / num_links
            factor2 += P_follows_link_to_page

        # Finally, we need to weigh the second factor according to damping factor
        factor2 = factor2 * d

        return factor1 + factor2

    while True:
        # Calculate new values for PageRanks
        new_ranks = dict()
        for page_name in page_names:
            new_ranks[page_name] = pagerank(page_name, corpus, damping_factor)

        # Stop iterating when all of the newly calculated PageRanks
        #  have changed at most 0.001 units
        if all(
            abs(pageranks[page_name] - new_ranks[page_name]) <= 0.001
            for page_name in page_names
        ):
            break

        # Otherwise keep iterating...
        # For the next iteration, use newly calculated PageRanks
        pageranks = new_ranks

    return pageranks


if __name__ == "__main__":
    main()
