import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # States are represented as (movie_id, person_id) tuples
    # Nodes contain additional information on parent nodes and action
    # Neighbors is a list of tuples and it includes source itself, too

    # Handle the edge case where source = target
    if source == target:
        return []

    # Create a search frontier and add the initial states as nodes to it
    # Choose queue frontier (BFS) to make sure we find the shortest route
    frontier = QueueFrontier()
    neighbors = neighbors_for_person(source)
    for neighbor in neighbors:
        # TODO Check whether neighbor state is the goal state here

        frontier.add(Node(state=neighbor, parent=None, action=None))

    # Explored set will contain all explored states (sic! not nodes)
    explored = set()

    while True:
        # If frontier is empty, there is no solution
        if frontier.empty():
            return None

        # Grab next node from the frontier
        node = frontier.remove()
        person_id = node.state[1]

        # If selected node contains the goal state (target), there is a path
        if person_id == target:

            # Backtrack path back to source, initialize with current state
            path = [node.state]

            # While there are parent nodes, traverse through them
            parent_node = node.parent
            while parent_node:

                # Add parent state to the top of the list
                path = [parent_node.state] + path
                parent_node = parent_node.parent

            return path

        # Add current state to explored states
        explored.add(node.state)

        # Expand the neighbor states of current node
        neighbor_states = neighbors_for_person(person_id)
        for neighbor_state in neighbor_states:
            # TODO Check whether neighbor state is the goal state here

            # Only add current node to the frontier if it hasn't been
            # explored already and it is not already in the frontier
            if (
                not frontier.contains_state(neighbor_state)
                and not neighbor_state in explored
            ):
                frontier.add(Node(state=neighbor_state, parent=node, action=None))


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for star_id in movies[movie_id]["stars"]:  # edited variable name for clarity
            neighbors.add((movie_id, star_id))
    return neighbors


if __name__ == "__main__":
    main()
