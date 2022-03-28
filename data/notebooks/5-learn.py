# Imports
from deephaven.learn import gather
from deephaven import learn, read_csv
from deephaven.MovingAverages import ByEmaSimple

import numpy as np
os.system("pip install -U scikit-learn")
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

#model = LinearRegression(n_jobs=-1)
#model = make_pipeline(PolynomialFeatures(2), Ridge())
#model = make_pipeline(PolynomialFeatures(3), Ridge())
model = KNeighborsRegressor(n_neighbors=2)

# A function to fit our linear model
def fit_model(features, target):
    model.fit(features, target)
    print(model.score(features, target))

# A function to use the fitted model
def use_fitted_model(features):
    return model.predict(features)

# Our gather function
def table_to_numpy(rows, cols):
    return gather.table_to_numpy_2d(rows, cols, dtype = np.double)

# This function scatters data back into a Deephaven table
def numpy_to_table(data, idx):
    #print( data[idx])
    try:
        return float(data[idx])
    except (TypeError, AttributeError):
        return ""

# Our scatter function
def scatter(data, idx):
    return np.round(data[idx][0], 4)

split_time = minus(currentTime(),convertPeriod("T"+str(int((24*time_history/2)))+"H"))

combined_data_train = combined_data.where("Time_bin < split_time")
combined_data_test = combined_data.where("Time_bin >split_time")
# Train the linear regression model
learn.learn(
    table = combined_data,
    model_func = fit_model,#fit_linear_model,
    inputs = [learn.Input(["Weight_compound",  "Average_negative", "Average_positive"], table_to_numpy), learn.Input("Average_close", table_to_numpy)],
    outputs = None,
    batch_size = combined_data.size()
)

# Use the fitted model to make predictions
predicted_data = learn.learn(
    table = combined_data_test,
    model_func = use_fitted_model,
    inputs = [learn.Input([ "Weight_compound",  "Average_negative", "Average_positive"], table_to_numpy)],
    outputs = [learn.Output("predicted_values", scatter, "double")],
    batch_size = combined_data_test.size()
).sortDescending("Time_bin")

learned_plot = Plot.plot("compound sia predicted", predicted_data, "Time_bin", "Average_compound")\
    .plot("compound sia train", combined_data_train, "Time_bin", "Average_compound")\
    .plot("compound sia test", combined_data_test, "Time_bin", "Average_compound")\
    .twinX()\
    .plot("close predicted", predicted_data, "Time_bin", "Average_close")\
    .plot("close train", combined_data_train, "Time_bin", "Average_close")\
    .plot("close test", combined_data_test, "Time_bin", "Average_close")\
    .plot("predicted", predicted_data, "Time_bin", "predicted_values")\
    .show()
