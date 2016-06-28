# -*- coding: utf-8 -*-

# geojson data that will be used to update the data
# pts = './data/fires_2016_all.json'
# perims_all = './data/fireperimeters_2016_all.json'
# perims_active = './data/fireperimeters_2016_active.json'

def process( pts, perims_all, perims_active, output_directory, join_field_perims='FIREID', join_field_pts='ID' ):

    import geopandas as gpd
    from os.path import join

    # read in the data
    fires = gpd.read_file( join(output_directory, pts) )
    perims = gpd.read_file( join(output_directory, perims_all) )
    perims_active = gpd.read_file( join(output_directory, perims_active) )

    # merge and add ACTIVENOW column --> HARDWIRED AND DANGERTOWN
    # joined = perims.join( fires_clean, how='left', on=join_field, lsuffix='_pol', rsuffix='_pts' )
    fires_clean = fires.drop( ['geometry', 'NAME'] , axis=1 )
    merged_pols = perims.merge( fires_clean, how='left', left_on=join_field_perims, right_on=join_field_pts, suffixes=['_pol','_pts'] )
    merged_pols[ 'ACTIVENOW' ] = merged_pols.FIREID.isin( perims_active.FIREID ).astype( int )

    # drop the ones that have perimeters from the points database
    keep = [ i for i in fires.ID if i not in perims.FIREID ]
    pts_noperim = fires[ fires.ID.isin( keep ) ]

    # keep the fields that we want
    pols = [ 'NAME', 'ACRES', 'FIREYEAR', 'UPDATETIME', 'FIREID', 'ACTIVENOW', 'PERIMETERDATE', 'geometry' ]
    pts = [ 'GENERALCAUSE', 'PRIMARYFUELTYPE', 'DISCOVERYDATETIME', 'ISACTIVE' ]
    fields = pols + pts

    # remove what we dont want
    merged_pols = merged_pols.ix[ :, fields ]
    pts_noperim = pts_noperim.ix[ :, fields ]

    # update the time fields
    # time_fields = [ 'UPDATETIME','DISCOVERYDATETIME', 'PERIMETERDATE' ]
    # for t in time_fields:
    #   merged_pols[t] = [ time.ctime(i) for i in merged_pols[t].astype(int)/1000 ]

    # # update the dates in the points without perims layer
    # pts_noperim[time_fields[1]] = [ time.ctime(i) for i in pts_noperim[time_fields[1]].astype(int)/1000 if i != np.nan ]

    # re-geo the geometry column
    merged_pols = gpd.GeoDataFrame( merged_pols, geometry='geometry', crs={'init':'epsg:3338'}) #this crs may be incorrect
    pts_noperim = gpd.GeoDataFrame( pts_noperim, geometry='geometry', crs={'init':'epsg:3338'}) #this crs may be incorrect

    # write merged file to a new GeoJSON
    # output_filename = 'fireperimeters_2016_all_cleaned_joined.json'
    # if os.path.exists( output_filename ):
    #   os.remove( output_filename )

    # merged_pols.to_file( output_filename, driver='GeoJSON' )

    output_filename = join( output_directory, 'fireperimeters_2016_all_cleaned_joined.shp')
    merged_pols.to_file( output_filename, driver='ESRI Shapefile' )

    # this is a hack since the to_file method is failing...
    # with open( output_filename, 'w' ) as f:
    #   json.dump( merged_pols.to_json(), f )

    # write the remainder of un-joined points to a new GeoJSON
    # output_filename = 'fires_2016_cleaned_noperim.json'
    # if os.path.exists( output_filename ):
    #   os.remove( output_filename )

    # pts_noperim.to_file( output_filename, driver='GeoJSON' )

    output_filename = join(output_directory, 'fires_2016_cleaned_noperim.shp')
    pts_noperim.to_file( output_filename, driver='ESRI Shapefile' )

