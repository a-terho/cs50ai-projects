import csv
import sys
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    evidence = []
    labels = []

    # Define conversion function for every cell value
    convert = {
        "Administrative": int,
        "Administrative_Duration": float,
        "Informational": int,
        "Informational_Duration": float,
        "ProductRelated": int,
        "ProductRelated_Duration": float,
        "BounceRates": float,
        "ExitRates": float,
        "PageValues": float,
        "SpecialDay": float,
        # Convert month abbreviation (from first 3 letters) to datetime object
        #  and then to zero-padded string representation of its number (01-12).
        #  Then convert that string to int that is in scale of 0-11.
        "Month": lambda v: int(datetime.strptime(v[:3], "%b").strftime("%m")) - 1,
        "OperatingSystems": int,
        "Browser": int,
        "Region": int,
        "TrafficType": int,
        "VisitorType": lambda v: 1 if v == "Returning_Visitor" else 0,
        "Weekend": lambda v: 1 if v == "TRUE" else 0,
        "Revenue": lambda v: 1 if v == "TRUE" else 0,
    }

    # Open csv file for read and let csv reader handle newlines
    with open(filename, "r", newline="") as file:

        # Open reader and read column headers
        reader = csv.reader(file)
        headers = next(reader)

        for row in reader:

            # Convert row cells to appropriate types
            row = [convert[column](value) for column, value in zip(headers, row)]

            # Seperate each row into evidence and a label
            # There are 18 columns on each row
            evidence.append(row[:17])
            labels.append(row[17])

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    # Load nearest neighbor classifier and use it to create
    #  a model that fits current data for evidence and labels
    classifier = KNeighborsClassifier(n_neighbors=1)
    model = classifier.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    num_true_positives = labels.count(1)
    num_true_negatives = labels.count(0)

    # Using numpy comparison operators
    equal_values = labels == predictions
    num_correct_positives = ((predictions == 1) & equal_values).sum()
    num_correct_negatives = ((predictions == 0) & equal_values).sum()

    # Alternative way by using a loop
    # Calculate the number of correct predictions
    # for actual, prediction in zip(labels, predictions):
    #     if actual == prediction:
    #         if prediction == 1:
    #             num_correct_positives += 1
    #         elif prediction == 0:
    #             num_correct_negatives += 1

    # Sensitivity asks: Out of all true positives, how many
    #  were correcty identified using the prediction model?
    sensitivity = num_correct_positives / num_true_positives

    # Specificity asks: Out of all true negatives, how many
    #  were correctly identified using the prediction model?
    specificity = num_correct_negatives / num_true_negatives

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
