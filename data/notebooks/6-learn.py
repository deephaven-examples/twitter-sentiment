# Imports

from deephaven import DynamicTableWriter
from deephaven import dtypes as dht
from deephaven.learn import gather
from deephaven import read_csv
from deephaven import learn

import numpy as np, random, threading, time

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

#split_time = minus(now(),to_datetime("T"+str(int((24*time_history/2)))+"H"))

#combined_data_train = combined_data.where(["i %2 ==0"])
#combined_data_test = combined_data.where(["i %2 ==1"])

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
    table = live_binned,
    model_func = use_fitted_model,
    inputs = [learn.Input([ "Weight_compound",  "Average_negative", "Average_positive"], table_to_numpy)],
    outputs = [learn.Output("predicted_values", scatter, "double")],
    batch_size = live_binned.size()
).sort_descending(["Time_bin"])



from deephaven.plot.figure import Figure
figure = Figure()

learned_plot_sai = figure.plot_xy(series_name ="compound sia", t = predicted_data,  x ="Time_bin", y = "Average_compound")\
    .plot_xy(series_name ="compound sia live", t = predicted_data,  x ="Time_bin",  y = "Average_compound")\
    .show()

learned_plot_price = figure.plot_xy(series_name ="close predicted", t =predicted_data, x ="Time_bin", y = "predicted_values")\
    .plot_xy(series_name ="close train", t =combined_data, x ="Time_bin", y = "Average_close")\
    .show()
predicted_price = figure.plot_xy(series_name ="close predicted", t =predicted_data, x ="Time_bin",y =  "predicted_values")\
    .plot_xy(series_name ="close value", t =predicted_data, x ="Time_bin", y = "Average_close")\
    .show()