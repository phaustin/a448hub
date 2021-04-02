|**feature** |dataframe attribute/method|
|---|---|
|**Useful Attributes** |
|Number of rows and columns (rows first, columns second) | `df.shape` |
|Names and data types of each column |  `df.dtypes` 
|Just the names of each column | `df.columns` 
|**Rows at a Glance** |
|First `n` rows (default 5) |`df.head(n)`
|Last `n` rows (default 5) | `df.tail(n)`
|A random sampling of `n` rows (default 1) | `df.sample(n)`


|**feature**|method|
|---|---|
|Unique values | `df['A'].unique()`|
|Number of unique values | `df['A'].nunique()`|
|Counts of each unique value | `df['A'].value_counts()`|


|a  |b  |c  |d | d |
|---|---|---|---|---|
|a  |b  |c  |d  |e  |

