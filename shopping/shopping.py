import csv
import sys

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
        -0 Administrative, an integer
        -1 Administrative_Duration, a floating point number
        -2 Informational, an integer
        -3 Informational_Duration, a floating point number
        -4 ProductRelated, an integer
        -5 ProductRelated_Duration, a floating point number
        -6 BounceRates, a floating point number
        -7 ExitRates, a floating point number
        -8 PageValues, a floating point number
        -9 SpecialDay, a floating point number
        -10 Month, an index from 0 (January) to 11 (December)
        -11 OperatingSystems, an integer
        -12 Browser, an integer
        -13 Region, an integer
        -14 TrafficType, an integer
        -15 VisitorType, an integer 0 (not returning) or 1 (returning)
        -16 Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    
    evidenceList = []
    labelList = []
    with open('shopping.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_first = True
        for row in csv_reader:
            if line_first == True:
                line_first = False
            else:
                evidence = [ 
                int(row[0]), 
                float(row[1]), 
                int(row[2]), 
                float(row[3]), 
                int(row[4]), 
                float(row[5]), 
                float(row[6]), 
                float(row[7]), 
                float(row[8]),
                float(row[9]), 
                getMonthAsInt(row[10]), 
                int(row[11]), 
                int(row[12]), 
                int(row[13]), 
                int(row[14]), 
                1 if row[15] == 'Returning_Visitor' else 0, 
                1 if row[16] else 0]
                
                evidenceList.append(evidence)
                if row[-1] == "TRUE":
                    labelList.append(1)
                else:
                    labelList.append(0)

    return (evidenceList, labelList)
    
def getMonthAsInt(shortMonth):
    return{
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'June' : 6,
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9, 
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
    }[shortMonth]

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    knn = KNeighborsClassifier(n_neighbors = 1)
    knn.fit(evidence, labels)
    return knn

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    pos_all = labels.count(1) 
    neg_all = labels.count(0)
    
    pos_true = 0
    neg_true = 0
    
    for i in range(len(predictions)):
        if predictions[i] == 1 and labels[i] == 1:
            pos_true += 1
        elif predictions[i] == 0 and labels[i] == 0:
            neg_true += 1
            
    return (pos_true/pos_all, neg_true/neg_all)

if __name__ == "__main__":
    main()
