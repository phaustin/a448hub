---
jupytext:
  notebook_metadata_filter: all,-language_info,-toc,-latex_envs
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.8.2
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

```{code-cell} ipython3
#!mamba install -c conda-forge intake-esm -y
#!mamba install -c conda-forge cmocean -y
```

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

```{code-cell} ipython3
catalog_df=pd.read_csv(csv_filename)
catalog_df.head()
```

```{code-cell} ipython3
col = intake.open_esm_datastore(json_filename)
```

```{code-cell} ipython3
col
```

### First show all CCCma historical sithick instances

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

```{code-cell} ipython3
member = 'r1i1p2f1'
filename=col_subset.df.query("member_id=='r1i1p2f1'")['zstore'].iloc[0]
```

```{code-cell} ipython3
dset_cccma_sithick=xr.open_zarr(fsspec.get_mapper(filename), consolidated=True)
dset_cccma_sithick
```

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

### now mohc

+++

Note that MOHC has three archived versions, GCM3.1 LL and MM and ESM1

https://cera-www.dkrz.de/WDCC/ui/cerasearch/cmip6?input=CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL

https://cera-www.dkrz.de/WDCC/ui/cerasearch/cmip6?input=CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM

https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019MS001739

https://agupubs.onlinelibrary.wiley.com/doi/pdf/10.1029/2019MS001995

```{code-cell} ipython3
mohc_index = df.query("activity_id=='CMIP' & institution_id == 'MOHC' & table_id=='SImon'"
                         "& source_id == 'HadGEM3-GC31-LL'"
                         "& member_id == 'r1i1p1f3'"
                         "& experiment_id == 'historical'& variable_id=='sithick'").index

mohc_sithick_file =df.loc[mohc_index].iloc[0]['zstore']

mohc_index = df.query("activity_id=='CMIP' & institution_id == 'MOHC'"
            "& experiment_id == 'historical'& variable_id=='tas'"
            "& source_id == 'HadGEM3-GC31-LL'"
             "& member_id == 'r1i1p1f3' & table_id == 'Amon'").index

mohc_tas_file =df.loc[mohc_index].iloc[0]['zstore']

print(mohc_sithick_file)
print(mohc_tas_file)
```

### Limit to 1 run of the earth system model (ESM)

```{code-cell} ipython3
cccma_index = df.query("activity_id=='CMIP' & institution_id == 'CCCma' & table_id=='SImon'"
            "& experiment_id == 'historical' & variable_id=='sithick'"
            "& source_id=='CanESM5' & member_id == 'r12i1p2f1'").index
cccma_sithick_file = df.loc[cccma_index].iloc[0]['zstore']

cccma_index = df.query("activity_id=='CMIP' & institution_id == 'CCCma' "
            "& experiment_id == 'historical' & variable_id=='tas'"
            "& table_id == 'Amon'"
            "& source_id=='CanESM5' & member_id == 'r12i1p2f1'").index

cccma_tas_file = df.loc[cccma_index].iloc[0]['zstore']

print(cccma_sithick_file)
print(cccma_tas_file)
```

### Find the cell area for MOHC GC31-LL

```{code-cell} ipython3
mohc_areacello = df.query("activity_id=='CMIP' & institution_id == 'MOHC' "
            "& experiment_id == 'piControl' & source_id == 'HadGEM3-GC31-LL' & variable_id=='areacello'")
mohc_areacello
```

```{code-cell} ipython3
cccma_areacello = df.query("activity_id=='CMIP' & institution_id == 'CCCma' "
            "& experiment_id == 'historical' & variable_id=='areacello'"
            "& source_id=='CanESM5' & member_id == 'r12i1p2f1'")

cccma_areacello_file = cccma_areacello.iloc[0]['zstore']
cccma_areacello_file
```

```{code-cell} ipython3
cccma_sithick_file
```

### Read the file into a zarr dataset

```{code-cell} ipython3
cccma_fs = gcsfs.GCSFileSystem(project="cccma")
```

```{code-cell} ipython3
cccma_sithick_file
```

```{code-cell} ipython3
gcsmap_cccma = cccma_fs.get_mapper(cccma_sithick_file)
dset_si_cccma = xr.open_zarr(gcsmap_cccma)
```

```{code-cell} ipython3
gcsmap_cccma = cccma_fs.get_mapper(cccma_tas_file)
dset_tas_cccma = xr.open_zarr(gcsmap_cccma)
```

```{code-cell} ipython3
mohc_fs = gcsfs.GCSFileSystem(project="mohc")
gcsmap_mohc = mohc_fs.get_mapper(mohc_sithick_file)
dset_sithick_mohc = xr.open_zarr(gcsmap_mohc)
```

```{code-cell} ipython3
gcsmap_mohc = mohc_fs.get_mapper(mohc_tas_file)
dset_tas_mohc = xr.open_zarr(gcsmap_mohc)
```

#### Get metadata corresponding to sea-ice thickness (sithick)

```{code-cell} ipython3
dset_tas_cccma
```

### get one tas timestep from ccma

```{code-cell} ipython3
# select specific time
cccma_tas_1850 = dset_tas_cccma['tas'].sel(time=cftime.DatetimeNoLeap(1850, 1, 16, 12, 0, 0, 0))
cccma_tas_1850.plot(cmap = 'coolwarm');
```

```{code-cell} ipython3
dset_tas_cccma
```

### check some histograms

```{code-cell} ipython3
type(dset_tas_cccma.lon.values)
```

```{code-cell} ipython3
north_lats = dset_tas_cccma.lat.values > 75;
cccma_tas = cccma_tas_1850[north_lats]
lons = dset_tas_cccma.lon.values
lons.shape, cccma_tas.shape
```

### polar plot

```{code-cell} ipython3
fig = plt.figure(1, figsize=[13,13])

# Set the projection to use for plotting
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.coastlines()

# Pass ax as an argument when plotting. Here we assume data is in the same coordinate reference system than the projection chosen for plotting
# isel allows to select by indices instead of the time values
cccma_ds_1850.plot.pcolormesh(ax=ax, cmap='coolwarm')
```

```{code-cell} ipython3
dset_mohc
```

```{code-cell} ipython3
dset_mohc.time
```

```{code-cell} ipython3
# select specific time
mohc_ds_1850 = dset_mohc['sithick'].sel(time=cftime.Datetime360Day(1850, 4, 16,0, 0, 0, 0))
mohc_ds_1850.plot(cmap = 'coolwarm');
```

```{code-cell} ipython3
ds_1850
```

```{code-cell} ipython3
sithick=dset_cccma['sithick']
sithick
```

```{code-cell} ipython3
# select the nearest time. Here from 1st April 1850

dset_cccma['sithick'].sel(time=cftime.DatetimeNoLeap(1850, 4, 1), method='nearest').plot(cmap='coolwarm')
```

### Customize the plot

```{code-cell} ipython3
lon=ds_1850.longitude.values
print(lon.shape)
```

```{code-cell} ipython3
plt.plot(ds_1850.longitude.values[-150:,-150:],ds_1850.latitude.values[-150:,-150:],'r.');
```

```{code-cell} ipython3
pc_proj = ccrs.PlateCarree()
np_proj = ccrs.NorthPolarStereo()
fig,ax = plt.subplots(1,1, figsize=[13,13],subplot_kw = {'projection' : np_proj} )

# Set the projection to use for plotting
ax.coastlines()

# Pass ax as an argument when plotting. Here we assume data is in the same coordinate reference system than the projection chosen for plotting
# isel allows to select by indices instead of the time values
ax.pcolormesh(ds_1850.longitude.values,ds_1850.latitude.values,ds_1850.values, cmap='coolwarm', transform = pc_proj)
```

#### Change Plotting Projection

```{code-cell} ipython3
fig = plt.figure(1, figsize=[10,10])

# We're using cartopy and are plotting in Orthographic projection 
# (see documentation on cartopy)
ax = plt.subplot(1, 1, 1, projection=ccrs.Orthographic(0, 90))
ax.coastlines()

# We need to project our data to the new Orthographic projection and for this we use `transform`.
# we set the original data projection in transform (here PlateCarree)
dset_cccma['sithick'].isel(time=0).plot(ax=ax, transform=ccrs.PlateCarree(), cmap='coolwarm')

# One way to customize your title
plt.title(dset.time.values[0].strftime("%B %Y"), fontsize=18)
```

```{code-cell} ipython3

```
