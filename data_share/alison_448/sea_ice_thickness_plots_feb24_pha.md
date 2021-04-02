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

# SEA ICE THICKNESS

```{code-cell} ipython3
#!conda install mamba -y
#!mamba install intake -y
# !mamba install xarray -y
# !mamba install -c conda-forge gcsfs -y
# !mamba install -c conda-forge zarr -y
```

```{code-cell} ipython3
import gcsfs
import xarray as xr
import pandas as pd
import cftime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
```

# CCCMA PLOTS

```{code-cell} ipython3
# Connect to Google Cloud Storage
fs_cccma = gcsfs.GCSFileSystem(token='anon', access='read_only')

# create a MutableMapping from a store URL
cccma_mapper = fs_cccma.get_mapper("gs://cmip6/CMIP6/CMIP/CCCma/CanESM5/historical/r12i1p2f1/SImon/sithick/gn/v20190429/")

# make sure to specify that metadata is consolidated
cccma_ds = xr.open_zarr(cccma_mapper, consolidated=True, decode_times=True, use_cftime=True)
```

```{code-cell} ipython3
cccma_ds.attrs
```

```{code-cell} ipython3
# for Google Cloud:
df = pd.read_csv("https://cmip6.storage.googleapis.com/pangeo-cmip6.csv")

df_subset_cccma = df.query("activity_id=='CMIP' & institution_id == 'CCCma' & table_id=='SImon'"
            "& experiment_id == 'historical' & variable_id=='sithick'"
            "& source_id=='CanESM5' & member_id == 'r12i1p2f1'")
```

```{code-cell} ipython3
# get the path to a specific zarr store
zstore_cccma = df_subset_cccma.zstore.values[-1]
mapper_cccma = fs_cccma.get_mapper(zstore_cccma)

# open using xarray
ds_cccma = xr.open_zarr(mapper_cccma, consolidated=True)
```

#### Plotting imshow and histograms:

```{code-cell} ipython3
# plt.imshow of the first time step
plt.imshow(ds_cccma['sithick'][0,:,:])
```

```{code-cell} ipython3
# histogram of first time step of sea ice thickness

fig, axis = plt.subplots(1,1,figsize=(10,10))
axis.hist(ds_cccma['sithick'][0,:,:].values.flatten())
```

```{code-cell} ipython3
# plt.imshow of the last time step
plt.imshow(ds_cccma['sithick'][-1,:,:])
```

#### Trying to actually plot sea ice thickness

```{code-cell} ipython3
ax = plt.axes(projection=ccrs.Robinson())
col = plt.pcolor(ds_cccma['sithick'][0,:,:].longitude, ds_cccma['sithick'][0,:,:].latitude, ds_cccma['sithick'][0,:,:], transform=ccrs.PlateCarree(), cmap='coolwarm')
ax.coastlines()
ax.set(title="Sea Ice Thickness -" + str(ds_cccma.attrs['institution_id']) + " : " + str(ds_cccma['sithick'][0,:,:].coords['time'].values))

cbar = ax.figure.colorbar(col, extend="both", orientation="vertical")
cbar.set_label("Sea Ice Thickness")
```

```{code-cell} ipython3
ax = plt.axes(projection=ccrs.Robinson())
col = plt.pcolor(ds_cccma['sithick'][-1,:,:].longitude, ds_cccma['sithick'][-1,:,:].latitude, ds_cccma['sithick'][-1,:,:], transform=ccrs.PlateCarree(), cmap='coolwarm')
ax.coastlines()
ax.set(title="Sea Ice Thickness -" + str(ds_cccma.attrs['institution_id']) + " : " + str(ds_cccma['sithick'][-1,:,:].coords['time'].values))

cbar = ax.figure.colorbar(col, extend="both", orientation="vertical")
cbar.set_label("Sea Ice Thickness")
```

```{code-cell} ipython3
# Still not really working! 

fig = plt.figure(1, figsize=[10,10])

# We're using cartopy and are plotting in Orthographic projection 
# (see documentation on cartopy)
ax = plt.subplot(1, 1, 1, projection=ccrs.Orthographic(0, 90))
ax.coastlines()

# We need to project our data to the new Orthographic projection and for this we use `transform`.
# we set the original data projection in transform (here PlateCarree)
ds_cccma['sithick'].isel(time=0).plot(ax=ax, transform=ccrs.PlateCarree(), cmap='coolwarm')

# One way to customize your title
plt.title(ds_cccma.time.values[0].strftime("%B %Y"), fontsize=18)
```

# MOHC PLOTS

```{code-cell} ipython3
# Connect to Google Cloud Storage
fs_mohc = gcsfs.GCSFileSystem(token='anon', access='read_only')

# create a MutableMapping from a store URL
mohc_mapper = fs_mohc.get_mapper("gs://cmip6/CMIP6/CMIP/MOHC/HadGEM3-GC31-LL/historical/r2i1p1f3/SImon/sithick/gn/v20190624/")

# make sure to specify that metadata is consolidated
mohc_ds = xr.open_zarr(mohc_mapper, consolidated=True, decode_times=True, use_cftime=True)
```

```{code-cell} ipython3
# for Google Cloud:
df = pd.read_csv("https://cmip6.storage.googleapis.com/pangeo-cmip6.csv")

df_subset_mohc = df.query("activity_id=='CMIP' & institution_id == 'MOHC' & table_id=='SImon'"
            "& experiment_id == 'historical' & variable_id=='sithick'"
            "& source_id=='UKESM1-0-LL' & member_id == 'r10i1p1f2'")
```

```{code-cell} ipython3
# get the path to a specific zarr store
zstore_mohc = df_subset_mohc.zstore.values[-1]
mapper_mohc = fs_mohc.get_mapper(zstore_mohc)

# open using xarray
ds_mohc = xr.open_zarr(mapper_mohc, consolidated=True)
```

#### Plotting imshow and histograms:

```{code-cell} ipython3
# plt.imshow of the first time step
plt.imshow(ds_mohc['sithick'][0,:,:])
```

```{code-cell} ipython3
# histogram of first time step of sea ice thickness
# really not sure what this means ..

plt.hist(ds_mohc['sithick'][0,:,:])
```

```{code-cell} ipython3
# plt.imshow of the last time step
plt.imshow(ds_mohc['sithick'][-1,:,:])
```

#### Trying to actually plot sea ice thickness

```{code-cell} ipython3
ax = plt.axes(projection=ccrs.Robinson())
col = plt.pcolor(ds_mohc['sithick'][0,:,:].longitude, ds_mohc['sithick'][0,:,:].latitude, ds_mohc['sithick'][0,:,:], transform=ccrs.PlateCarree(), cmap='coolwarm')
ax.coastlines()
ax.set(title="Sea Ice Thickness -" + str(ds_mohc.attrs['institution_id']) + " : " + str(ds_mohc['sithick'][0,:,:].coords['time'].values))

cbar = ax.figure.colorbar(col, extend="both", orientation="vertical")
cbar.set_label("Sea Ice Thickness")
```

```{code-cell} ipython3
ax = plt.axes(projection=ccrs.Robinson())
col = plt.pcolor(ds_mohc['sithick'][-1,:,:].longitude, ds_mohc['sithick'][-1,:,:].latitude, ds_mohc['sithick'][-1,:,:], transform=ccrs.PlateCarree(), cmap='coolwarm')
ax.coastlines()
ax.set(title="Sea Ice Thickness -" + str(ds_mohc.attrs['institution_id']) + " : " + str(ds_mohc['sithick'][-1,:,:].coords['time'].values))

cbar = ax.figure.colorbar(col, extend="both", orientation="vertical")
cbar.set_label("Sea Ice Thickness")
```

```{code-cell} ipython3
# Still not really working! 

fig = plt.figure(1, figsize=[10,10])

# We're using cartopy and are plotting in Orthographic projection 
# (see documentation on cartopy)
ax = plt.subplot(1, 1, 1, projection=ccrs.Orthographic(0, 90))
ax.coastlines()

# We need to project our data to the new Orthographic projection and for this we use `transform`.
# we set the original data projection in transform (here PlateCarree)
ds_mohc['sithick'].isel(time=0).plot(ax=ax, transform=ccrs.PlateCarree(), cmap='coolwarm')

# One way to customize your title
plt.title(ds_mohc.time.values[0].strftime("%B %Y"), fontsize=18)
```

### Playing around

```{code-cell} ipython3
import proplot as plot 

fig, ax = plot.subplots(axwidth=4.5, tight=True,
                        proj='robin', proj_kw={'lon_0': 180},)
# format options
ax.format(land=False, coast=True, innerborders=True, 
          borders=True,
          labels=True, geogridlinewidth=0,)
map1 = ax.contourf(ds_cccma['longitude'], ds_cccma['latitude'], ds_cccma['sithick'][0,:,:],
                   cmap='IceFire', extend='both')
ax.colorbar(map1, loc='b', shrink=0.5, extendrect=True)

plt.show()
```

```{code-cell} ipython3
fig, ax = plot.subplots(axwidth=4.5, tight=True,
                        proj='npstere', )
# format options
ax.format(land=True, coast=True, innerborders=True, 
          borders=True,
          labels=True, geogridlinewidth=1,
          boundinglat=60,)
map1 = ax.contourf(ds_cccma['longitude'], ds_cccma['latitude'], ds_cccma['sithick'][0,:,:],
                   cmap='coolwarm', extend='both')
ax.colorbar(map1, loc='b', shrink=0.5, extendrect=True)
plt.show()
```

```{code-cell} ipython3
fig, ax = plot.subplots(axwidth=4.5, tight=True,
                        proj='npstere', )
# format options
ax.format(land=False, coast=True, innerborders=True, 
          borders=True,
          labels=True, geogridlinewidth=0,
          boundinglat=60,)
map1 = ax.contourf(ds_mohc['longitude'], ds_mohc['latitude'], ds_mohc['sithick'][0,:,:],
                   cmap='coolwarm', extend='both')
ax.colorbar(map1, loc='b', shrink=0.5, extendrect=True)
plt.show()
```

```{code-cell} ipython3
clim = ds_cccma['sithick'].mean('time', keep_attrs=True)
```

```{code-cell} ipython3
plt.figure(figsize=(14,6))
ax = plt.axes(projection=ccrs.Orthographic(0, 90))
ax.set_global()
ds_cccma.sithick[0].plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), x='longitude', y='latitude', add_colorbar=True, cmap='coolwarm')
ax.coastlines()
#global_extent = ax.get_extent(crs=ccrs.Orthographic())
#ax.set_extent(global_extent[:2] + (50, 90), crs=ccrs.PlateCarree())

land_hires = cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                          edgecolor='k', facecolor='grey')
ax.add_feature(land_hires)
```

```{code-cell} ipython3
plt.figure(figsize=(14,6))
ax = plt.axes(projection=ccrs.Orthographic(0, 90))
ax.set_global()
ds_mohc.sithick[0].plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), x='longitude', y='latitude', add_colorbar=True, cmap='coolwarm')
ax.coastlines()
global_extent = ax.get_extent(crs=ccrs.Orthographic())
ax.set_extent(global_extent[:2] + (50, 90), crs=ccrs.PlateCarree())

import cartopy.feature as cfeature
land_hires = cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                          edgecolor='k', facecolor='grey')
ax.add_feature(land_hires)
```

```{code-cell} ipython3
plt.figure(figsize=(14,6))
ax = plt.axes(projection=ccrs.NorthPolarStereo(0, 90))
ax.set_global()
ds_cccma.sithick[0].plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), x='longitude', y='latitude', add_colorbar=True)
ax.coastlines()
#global_extent = ax.get_extent(crs=ccrs.Orthographic())
#ax.set_extent((0, 500000, 0, 500000), crs=ccrs.NorthPolarStereo())
```

```{code-cell} ipython3
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker


ax = plt.axes(projection=ccrs.Mercator())
ax.coastlines()

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
gl.xlabels_top = False
gl.ylabels_left = False
gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -45, 0, 45, 180])
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 15, 'color': 'gray'}
gl.xlabel_style = {'color': 'red', 'weight': 'bold'}

plt.show()
```

```{code-cell} ipython3

```
