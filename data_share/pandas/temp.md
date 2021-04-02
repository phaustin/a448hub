### Unique Values & Counting

For a column `df['A']` which contains many repeated values (such as categories), some useful summary methods are:

|**feature**|method|
|---|---|
|Unique values | `df['A'].unique()`|
|Number of unique values | `df['A'].nunique()`|
|Counts of each unique value | `df['A'].value_counts()`|


> Note: The `unique`, `nunique`, and `value_counts` methods can only be applied to a Series (not a DataFrame)
