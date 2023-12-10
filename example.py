import pandas as pd

def isSummer(ind):
    return ind.day>2 and ind.day <=4

# Create a sample series
data = [10, 20, 30, 40, 50]
dates = pd.date_range('2023-01-01', periods=len(data), freq='D')
series = pd.Series(data, index=dates)

# Filter the series for a range of dates
# start_date = pd.to_datetime('2023-01-03')
# end_date = pd.to_datetime('2023-01-05')
# filtered_series = series[(series.index.day < 2) | (series.index.day > 4)]

filtered_series = series[(isSummer(ind) for ind in series.index)]

print(filtered_series)
