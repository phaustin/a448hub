---
jupytext:
  notebook_metadata_filter: all,-language_info,-toc,-latex_envs
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

```{code-cell} ipython3
import context
import warnings
import intake
import xarray as xr 
import matplotlib.pyplot as plt 
import pandas as pd
import cftime
import gcsfs
import cartopy.crs as ccrs
from pathlib import Path
import pandas as pd
from a448_lib import data_read
import fsspec
import cmocean as cm
import cartopy.feature as cfeature
import numpy as np
```

# Sea-ice thickness demo

http://gallery.pangeo.io/repos/pangeo-gallery/cmip6/index.html

http://xarray.pydata.org/en/stable/weather-climate.html

+++

# Plot CanESM5 sea ice thickness

+++

* Download the catalog in csv and json format

```{code-cell} ipython3
csv_filename = "pangeo-cmip6.csv"
root = "https://storage.googleapis.com/cmip6"
if Path(csv_filename).is_file():
    print(f"found {csv_filename}")
else:
    print(f"downloading {csv_filename}")
    data_read.download(csv_filename,root=root)
    
json_filename="https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
```

* make a dataframe from the csv version

```{code-cell} ipython3
catalog_df=pd.read_csv(csv_filename)
catalog_df.head()
```

* make an intake collection from the json version

```{code-cell} ipython3
col = intake.open_esm_datastore(json_filename)
```

```{code-cell} ipython3
col
```

## First show all 40 CCCma historical runs

```{code-cell} ipython3
source = "CanESM5"
query = dict(
    experiment_id=['historical'],
    institution_id = "CCCma",
    source_id = source)

col_subset = col.search(require_all_on=["source_id"],**query)
names=set(col_subset.df.variable_id)
names
```

```{code-cell} ipython3
source = "CanESM5"
query = dict(
    experiment_id=['historical'],
    institution_id = "CCCma",
    source_id = source,
    table_id=["SImon"],
    variable_id=['sithick'])

col_subset = col.search(require_all_on=["source_id"],**query)
```

```{code-cell} ipython3
col_subset.df.head()
```

```{code-cell} ipython3
len(col_subset.df)
```

## get the first realization for the sithick dataset

```{code-cell} ipython3
member = 'r1i1p2f1'
filename=col_subset.df.query("member_id=='r1i1p2f1'")['zstore'].iloc[0]
```

```{code-cell} ipython3
dset_cccma_sithick=xr.open_zarr(fsspec.get_mapper(filename), consolidated=True)
dset_cccma_sithick
```

## Now get the cell area for the ocean grid

```{code-cell} ipython3
query = dict(
    experiment_id=['historical'],
    institution_id = "CCCma",
    table_id = "Ofx",
    source_id = source,
    member_id = member,
    variable_id=['areacello'])

col_subset = col.search(require_all_on=["source_id"],**query)
col_subset.df
```

```{code-cell} ipython3
filename=col_subset.df['zstore'].iloc[0]
filename
```

```{code-cell} ipython3
dset_cccma_areacello=xr.open_zarr(fsspec.get_mapper(filename), consolidated=True)
dset_cccma_areacello
```

## Plot the lat/lon for this curvilinear ocean grid

```{code-cell} ipython3
lons = dset_cccma_sithick.longitude
lats = dset_cccma_sithick.latitude
data = dset_cccma_sithick['sithick']
```

```{code-cell} ipython3
lons.shape
lats.shape
data.shape
```

```{code-cell} ipython3
plt.plot(lons[-30:],lats[-30:],'r.');
```

```{code-cell} ipython3
def deseam(lon, lat, data):
    """
    Function to get rid of the "seam" that shows up on 
    the map when you're using these curvilinear grids.
    """
    i, j = lat.shape
    new_lon = np.zeros((i, j + 1))
    new_lon[:, :-1] = lon
    new_lon[:, -1] = lon[:, 0]

    new_lat = np.zeros((i, j + 1))
    new_lat[:, :-1] = lat
    new_lat[:, -1] = lat[:, 0]

    new_data = np.zeros((i, j + 1))
    new_data[:, :-1] = data
    new_data[:, -1] = data[:, 0]
    new_data = np.ma.array(new_data, mask=np.isnan(new_data))
    return new_lon, new_lat, new_data
```

```{code-cell} ipython3
lons, lats, newdata = deseam(lons,lats,data[0,:,:])
```

```{code-cell} ipython3
f, ax = plt.subplots(1,1,figsize=(12,12),
                     subplot_kw=dict(projection=ccrs.Orthographic(0, 80)))

p = ax.pcolormesh(lons,
              lats,
              newdata,
              transform=ccrs.PlateCarree(),
              vmin=0, vmax=8, cmap=cm.cm.ice)

f.colorbar(p, label='sea ice thickness (m)')
ax.set_title('CCCma sea ice thickness (m)')

# Add land.
ax.add_feature(cfeature.LAND, color='#a9a9a9', zorder=4);
```

## Now do a mean climatology: 1970-2000

```{code-cell} ipython3
climatology =  dset_cccma_sithick['sithick'].sel(time=slice('1970', '2000'))
```

```{code-cell} ipython3
climatology.time
```

```{code-cell} ipython3
# Take a seasonal climatology over 1970-2000
climatology = dset_cccma_sithick['sithick'].sel(time=slice('1970', '2000')).groupby('time.season').mean('time')
```

```{code-cell} ipython3
JJA = climatology.sel(season='JJA').squeeze()
lons, lats, data = deseam(JJA.longitude, JJA.latitude, JJA)
```

```{code-cell} ipython3
f, ax = plt.subplots(1,1,figsize=(12,12),
                     subplot_kw=dict(projection=ccrs.Orthographic(0, 80)))

p = ax.pcolormesh(lons,
              lats,
              data,
              transform=ccrs.PlateCarree(),
              vmin=0, vmax=8, cmap=cm.cm.ice)

f.colorbar(p, label='sea ice thickness (m)')
ax.set_title('CCCma sea ice thickness (m)')

# Add land.
ax.add_feature(cfeature.LAND, color='#a9a9a9', zorder=4);
```

## Take the area-weighted mean

```{code-cell} ipython3
dset_cccma_areacello
```

```{code-cell} ipython3
areacello = dset_cccma_areacello['areacello'].squeeze()
```

```{code-cell} ipython3
sithick = dset_cccma_sithick['sithick'].squeeze()

# Grab north of the equator
arctic_ice = sithick.where(areacello.latitude > 0)
arctic_ice.isel(time=0).plot();
arctic_ice.shape
```

```{code-cell} ipython3
areacello.plot();
```

```{code-cell} ipython3
# compute area-weighted mean
aw_arctic_ice = (arctic_ice * areacello).sum(['j', 'i']) / areacello.sum()
```

```{code-cell} ipython3
aw_arctic_ice = aw_arctic_ice.compute()
```

```{code-cell} ipython3
fig, ax = plt.subplots(1,1)
lines = aw_arctic_ice.groupby('time.year').mean('time').plot(ax=ax)
ax.grid(True)
```

```{code-cell} ipython3
col_subset.df
```

```{code-cell} ipython3
member = 'r30i1p2f1'
filename=col_subset.df.query("member_id=='r30i1p2f1'")['zstore'].iloc[0]
dset_cccma_sithick_r30i1p2f1=xr.open_zarr(fsspec.get_mapper(filename), consolidated=True)
dset_cccma_sithick_r30i1p2f1['sithick']
```

```{code-cell} ipython3
dset_cccma_sithick['sithick']
```

```{code-cell} ipython3
dset_cccma_sithick['sithick'].values
```

```{code-cell} ipython3

```
