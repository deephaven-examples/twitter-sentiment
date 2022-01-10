# Imports
from deephaven.TableTools import emptyTable
from deephaven.learn import gather
from deephaven import learn
import numpy as np

# Define the number of rows in our source table
n_rows = 10

# Create a table to be used as input
source = combined_tweets

# This function applies a summation "model" to the input data
def summation_model(features):
    return np.sum(features, axis = 1)

# This function gathers data from a table into a NumPy ndarray
def table_to_numpy(rows, columns):
    return gather.table_to_numpy_2d(rows, columns, dtype = np.double)

# This function scatters data back into a Deephaven table
def numpy_to_table(data, idx):
    return data[idx]

# The learn function call
result = learn.learn(
    table = source,
    model_func = summation_model,
    inputs = [learn.Input(["Weight_compound", "Average_compound"], table_to_numpy)],
    outputs = [learn.Output("Compound", numpy_to_table, "double")],
    batch_size = n_rows
)
