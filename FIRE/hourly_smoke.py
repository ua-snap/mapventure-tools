# process smoke data from wrf-chem
# currently specific to the PM_2_5_DRY variable...
# author: Michael Lindgren (malindgren@alaska.edu)
#      Scenarios Network For Alaska + Arctic Planning

def process_timestamp( t ):
    ''' specific to the wrf smoke inputs '''
    ts = str( t.data ).strip('"b').strip( "'" )
    ts = ts.replace( '_', ' ' )
    pt = pd.Timestamp( ts )
    return {'timestamp_raw':ts,'year':pt.year, 'month':pt.month,
            'day':pt.day, 'hour':pt.hour,
            'minute':pt.minute, 'second':pt.second }

if __name__ == '__main__':
    import rasterio, os
    from rasterio.warp import calculate_default_transform, RESAMPLING, reproject
    from rasterio.transform import array_bounds
    import xarray as xr
    import pandas as pd
    import numpy as np

    # open the netcdf file
    variable = 'PM2_5_DRY'
    ds = xr.open_dataset( '/center1/w/rltorgerson/2017061200/mywork/wrfout_d01_2017-06-12_00:00:00' )
    output_path = '/center1/w/rltorgerson/2017061200/mywork'

    # subset to the variable we want
    sub_ds = ds['PM2_5_DRY']

    # make the dataset somewhat sane
    lon = sub_ds[ 'XLONG' ][ 0 ]
    lat = sub_ds[ 'XLAT' ][ 0 ]

    # make the times something that are easily parseable
    time_raw = ds[ 'Times' ]
    df = pd.DataFrame( [process_timestamp( t ) for t in time_raw] )
    df = df.sort_values(['year', 'month', 'day', 'hour', 'minute', 'second'])
    start_date = df.iloc[0]
    # leverage pandas datetime functionality to make legit timestamps
    new_dates = pd.date_range( df.loc[0,'timestamp_raw'], periods=df.shape[0], freq='1H' )

    # make a NetCDF-like Dataset in memory
    # NOTE: I have no idea what the level variable is here but I am including it
    # the data for the variable seems to be structured (time,?,x,y)
    out_ds = xr.Dataset( {variable:(['time','level','x', 'y'], sub_ds.data)},
                coords={'lon': (['x', 'y'], lon),
                        'lat': (['x', 'y'], lat),
                        'time': new_dates,
                        'level':list(range(sub_ds.shape[1]))},
                attrs={ 'variable':variable,
                        'wrf-chem':'smoke model',
                        'postprocessed by:':'Michael Lindgren -- SNAP'} )


    # write this to disk -- if you want...
    output_filename = os.path.join( output_path, 'netcdf', 'wrfout_d01_{}_2017-06-15_00-00-00.nc'.format( variable ) )

    # make output directory if needed
    dirname, basename = os.path.split( output_filename )
    if not os.path.exists( dirname ):
        os.makedirs( dirname )

    out_ds.to_netcdf( output_filename, 'w', 'NETCDF4_CLASSIC' )

    # * * * * * * * * * REPROJECTION: * * * * * * * * * * * * * * * * * * * * * * * * * * *
    # some crs stuff that @bob got from the provider
    crs = "+proj=lcc +lat_1=65.000000 +lat_2=65.000000 +lat_0=65.000000 +lon_0=-152.000000 +R=6370000"
    crs = rasterio.crs.CRS.from_string( crs )
    gcps = "-gcp 0 0 -164.510605 57.652809 -gcp 0 298 -172.422668 70.599640 -gcp 298 0 -139.489395 57.652809 -gcp 298 298 -131.577332 70.599640"

    # resolution is a real hacky way to do it and not correct
    res = np.mean([np.diff(lon).min(), np.diff(lon).max()])
    affine = rasterio.transform.from_origin( lon.data.min(), lat.data.max(), res, -res ) # upper left pixel
    time, levels, height, width = out_ds[variable].shape
    meta = {'res':(res, res), 'affine':affine, 'height':height, 'width':width, 'count':1, 'dtype':'float32', 'driver':'GTiff', 'compress':'lzw', 'crs':crs }

    # subset to one of the 29 'levels' no idea what these are...
    levelint = 0
    out_ds_level = out_ds[variable].isel( level=levelint )

    # # warp to 3338
    with rasterio.drivers( CHECK_WITH_INVERT_PROJ=True ): # constrain output to legit warp extent -- may want to remove...
        src_bounds = array_bounds( width, height, affine )
        dst_crs = {'init':'epsg:3338'}
        # Calculate the ideal dimensions and transformation in the new crs
        dst_affine, dst_width, dst_height = calculate_default_transform(
                    crs, dst_crs, width, height, *src_bounds)

        for band in range(time):
            print( 'reprojecting: {}'.format(band) )
            # in/out arrays
            cur_arr = out_ds_level[ band, ... ].data
            out_arr = np.empty_like( cur_arr )

            # reproject
            reproject( cur_arr, out_arr, src_transform=affine, src_crs=crs, src_nodata=-1,
                    dst_transform=dst_affine, dst_crs=dst_crs, dst_nodata=-9999, resampling=RESAMPLING.bilinear,
                    SOURCE_EXTRA=1000, num_threads=4 )

            meta_out = meta.copy()
            meta_out.update( crs=dst_crs, width=dst_width, height=dst_height,
                                    affine=dst_affine, compress='lzw', nodata=-9999 )

            # write out a GeoTiff
            row = df.iloc[band]
            output_filename = os.path.join( output_path, 'geotiff',
                '{}_wrf-chem_{}_{}_{}-{}_level{}_epsg3338.tif'.format( variable,row['year'],row['month'],row['day'],row['hour'],levelint))

            # make output directory if needed
            dirname, basename = os.path.split( output_filename )
            if not os.path.exists( dirname ):
                os.makedirs( dirname )

            with rasterio.open( output_filename, 'w', **meta_out ) as out:
                out.write( out_arr, 1 )
