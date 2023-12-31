# -*- coding: utf-8 -*-
"""AI_Assignment_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17bcfGLVgu2HzXscX_6683vYwoHH-Z6J7

### Defining the function to process txt datasets
"""

import pandas as pd

def load_and_process_data(filename):
    try:
        # Read the data file
        df = pd.read_csv(filename, delim_whitespace=True, header=None)

        # The first column is the class label
        df.columns = ['class'] + ['feature_'+str(i) for i in range(1, len(df.columns))]

        # Move the 'class' column to the end
        df = df[[col for col in df.columns if col != 'class'] + ['class']]
        return df

    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
    except pd.errors.ParserError:
        print(f"There was a problem parsing the file {filename}. Check if the file format is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

"""### The nearest neighbor function"""

from sklearn.model_selection import LeaveOneOut
import numpy as np

def nearest_neighbor(df, features):
    loo = LeaveOneOut()
    correct_classifications = 0
    total_classifications = 0

    # Convert features and class columns to numpy arrays for efficient calculation
    feature_data = df[features].values
    class_data = df['class'].values

    for train_index, test_index in loo.split(feature_data):
        X_train, X_test = feature_data[train_index], feature_data[test_index]
        y_train, y_test = class_data[train_index], class_data[test_index]

        # Calculate Euclidean distances and find the nearest neighbor
        distances = np.sqrt(((X_train - X_test)**2).sum(axis=1))
        nearest_neighbor_index = np.argmin(distances)

        # Classify the test data point based on its nearest neighbor
        predicted_class = y_train[nearest_neighbor_index]

        if predicted_class == y_test[0]:
            correct_classifications += 1

        total_classifications += 1

    # Calculate and return the accuracy
    accuracy = correct_classifications / total_classifications
    return accuracy

"""### The forward selection function"""

def forward_selection(df):
    current_set_of_features = []  # Start with an empty set
    best_overall_accuracy = 0
    best_overall_features = []
    print("\nBeginning search.")
    for i in range(len(df.columns) - 1):  # The '-1' is to exclude the class column
        feature_to_add_at_this_level = None
        best_so_far_accuracy = 0

        for feature in df.columns[:-1]:  # The '[:-1]' is to exclude the class column
            if feature not in current_set_of_features:
                accuracy = nearest_neighbor(df, current_set_of_features + [feature])

                print(f"\tUsing feature(s) {current_set_of_features + [feature]} accuracy is {accuracy * 100:.1f}%")

                if accuracy > best_so_far_accuracy:
                    best_so_far_accuracy = accuracy
                    feature_to_add_at_this_level = feature

        current_set_of_features.append(feature_to_add_at_this_level)

        print(f"\nFeature set {current_set_of_features} was best, accuracy is {best_so_far_accuracy * 100:.1f}%\n")

        if best_so_far_accuracy > best_overall_accuracy:
            best_overall_accuracy = best_so_far_accuracy
            best_overall_features = current_set_of_features.copy()
        elif feature_to_add_at_this_level is not None:
            print("\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)")
        else:
            print("\nCannot improve by adding any features. Stopping.")
            break

    print(f"Finished search!! The best feature subset is {best_overall_features}, which has an accuracy of {best_overall_accuracy * 100:.1f}%")
    return best_overall_features, best_overall_accuracy

"""### The backward elimination function"""

def backward_elimination(df):
    current_set_of_features = df.columns[:-1].tolist()  # Start with all features
    best_overall_accuracy = 0
    best_overall_features = []

    print("Beginning search.\n")

    for i in range(len(df.columns) - 1):  # The '-1' is to exclude the class column
        feature_to_remove_at_this_level = None
        best_so_far_accuracy = 0

        for feature in current_set_of_features:
            test_features = current_set_of_features.copy()
            test_features.remove(feature)
            accuracy = nearest_neighbor(df, test_features)

            print(f"\tUsing feature(s) {test_features} accuracy is {accuracy * 100:.1f}%")

            if accuracy > best_so_far_accuracy:
                best_so_far_accuracy = accuracy
                feature_to_remove_at_this_level = feature

        current_set_of_features.remove(feature_to_remove_at_this_level)

        print(f"\nFeature set {current_set_of_features} was best, accuracy is {best_so_far_accuracy * 100:.1f}%\n")

        if best_so_far_accuracy > best_overall_accuracy:
            best_overall_accuracy = best_so_far_accuracy
            best_overall_features = current_set_of_features.copy()
        elif feature_to_remove_at_this_level is not None:
            print("\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)")
        else:
            print("\nCannot improve by removing any features. Stopping.")
            break

    print(f"Finished search!! The best feature subset is {best_overall_features}, which has an accuracy of {best_overall_accuracy * 100:.1f}%")
    return best_overall_features, best_overall_accuracy

"""### Main execution block"""

if __name__=="__main__":
    print("Welcome to Bertie Woosters Feature Selection Algorithm.")
    filename = input("Type in the name of the file to test: ")

    # Load and process data
    df = load_and_process_data(filename)

    # Print dataset info
    num_features = len(df.columns) - 1
    num_instances = len(df)
    print(f"\nThis dataset has {num_features} features (not including the class attribute), with {num_instances} instances.")

    # Calculate and print accuracy with all features
    all_features = df.columns[:-1].tolist()
    full_accuracy = nearest_neighbor(df, all_features)
    print(f"\nRunning nearest neighbor with all {num_features} features, using 'leaving-one-out' evaluation, I get an accuracy of {full_accuracy * 100:.1f}%")

    # Ask for algorithm choice and run the selected algorithm
    algorithm_choice = int(input("\nType the number of the algorithm you want to run.\n\n\t1) Forward Selection\n\t2) Backward Elimination\n\n"))

    if algorithm_choice == 1:
        forward_selection(df)
    elif algorithm_choice == 2:
        backward_elimination(df)
    else:
        print("Invalid choice. Please enter either 1 or 2.")
