---
jupytext:
  cell_metadata_filter: all
  notebook_metadata_filter: -language_info
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.7.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

+++ {"toc": true}

# Process Daily Data

Concatenate the raw data csv files into a single dataframe for all years,
doing some quality control.  We'll be focussing on the YVR airport station.

* Start with a single year to develop the code

* Write a function so

```{code-cell} ipython3
from pathlib import Path

import pandas as pd
```

## Test Calcs (Single Year)

```{code-cell} ipython3
station = "YVR"
stn_id = 889
year = 2010
this_dir = Path()
datafile = this_dir / Path(f"weather_daily_{station}_{stn_id}_{year}.csv")
```

```{code-cell} ipython3
df_in = pd.read_csv(datafile, skiprows=0, index_col=0, parse_dates=True)
df_in.head()
```

Some years, such as 2013, have a chunk of missing data at the beginning or end because the data is split into two different files where the Environment Canada station ID changed partway through the year.

To make sure these rows don't mess things up for concatenation later, we will simply discard any rows where all the measurements are missing (the measurements go from column `'Data Quality'` to the final column).

Note that we are specifying the 'Data Quality' column by its name, not its column number

```{code-cell} ipython3
# Create a series which is True for any row that has at least one non-null measurement
# and False otherwise

not_null = df_in.loc[:, "Data Quality":].notnull().any(axis=1)
not_null.head()
```

```{code-cell} ipython3
# Extract the subset of df_in where the not_null Series is True
data = df_in[not_null]
data.head()
```

To make life easier, let's also remove the degree symbol from the column names, using the string method `replace` and a [list comprehension](https://jakevdp.github.io/WhirlwindTourOfPython/11-list-comprehensions.html)

```{code-cell} ipython3
# # Create list of column names with degree symbols removed
columns = [nm.replace("\xb0", "") for nm in data.columns]
columns
```

```{code-cell} ipython3
# Update the column names in the DataFrame
data.columns = columns
data.head()
```

## Process All Years

Let's consolidate the above code into a function and then use it to process each year and concatenate the years into a single DataFrame.

```{code-cell} ipython3
def process_data(datafile, skiprows=0):
    """Process data for a single year."""
    df_in = pd.read_csv(datafile, skiprows=skiprows, index_col=0, parse_dates=True)

    # Create a series which is True for any row that has at least one
    # non-null measurement and False otherwise
    not_null = df_in.loc[:, "Data Quality":].notnull().any(axis=1)

    # Extract the subset of df_in where the not_null Series is True
    data = df_in[not_null]

    # Create list of column names with degree symbols removed
    columns = [nm.replace("\xb0", "") for nm in data.columns]

    # Update the column names in the DataFrame
    data.columns = columns

    return data
```

```{code-cell} ipython3
# Test the function on the data file from above
test = process_data(datafile)
test.head()
```

- First, concatenate all the data from the first set of years.
  - *Note: The YVR data from 1937 is a bit wonky, so we'll exclude it here.*
- Then, concatenate the data from recent years

```{code-cell} ipython3
# Initialize an empty DataFrame
data_all = pd.DataFrame()

# Early data (1938 to mid 2013)
stn_id_early = 889
years_early = range(1938, 2014)

# Recent data (mid 2013 to 2017)
stn_id_recent = 51442
years_recent = range(2013, 2020)

# Loop over station IDs and years, using Python's zip function
for stn, years_list in zip([stn_id_early, stn_id_recent], [years_early, years_recent]):
    for year in years_list:
        filename = this_dir / Path(f"weather_daily_{station}_{stn}_{year}.csv")
        data_in = process_data(filename)

        # Use the append method to append the new data
        data_all = data_all.append(data_in)
```

```{code-cell} ipython3
data_all.head(2)
```

```{code-cell} ipython3
data_all.tail(2)
```

```{code-cell} ipython3
data_all.shape
```

```{code-cell} ipython3
# Save the full set of concatenated data to file
processed_dir = this_dir / 'processed'
processed_dir.mkdir(parents=True,exist_ok=True)
year_min, year_max = data_all["Year"].min(), data_all["Year"].max()
savefile = (processed_dir 
             / Path(f"weather_daily_{station}_{year_min}-{year_max}_all.csv"))
print(f"Saving to {savefile}")
data_all.to_csv(savefile)
```

## Create a subset of the data

For demos we'll use a subset of the data columns and rename some of them for convenience.

```{code-cell} ipython3
# Extract subset with columns of interest and rename some columns

columns = [
    "Year",
    "Month",
    "Day",
    "Mean Temp (C)",
    "Max Temp (C)",
    "Min Temp (C)",
    "Total Rain (mm)",
    "Total Snow (cm)",
    "Total Precip (mm)",
]

cols_dict = {
    "Mean Temp (C)": "T_mean (C)",
    "Max Temp (C)": "T_high (C)",
    "Min Temp (C)": "T_low (C)",
    "Total Rain (mm)": "Rain (mm)",
    "Total Snow (cm)": "Snow (cm)",
}
data_subset = data_all[columns].rename(columns=cols_dict)
data_subset.index.name = "Date"
data_subset.head()
```

```{code-cell} ipython3
savefile2 = processed_dir / Path(f"weather_{station}.csv")
print(f"Saving to {savefile2}")
data_subset.to_csv(savefile2)
```

```{code-cell} ipython3

```
