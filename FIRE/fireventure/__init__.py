def run(output_directory):

    import os, json
    from FireData import FireData
    import arcgis
    from clean_join_perims_points import process

    services = {
        'FirePerimeters':"FIREYEAR='2016'",
        'Fires':"FIRESEASON='2016'"
    }
    groups = {
        'active':0,
        'all':1
    }
    fmat='GeoJSON'
    ext='.json'

    all_fires_fields = [
        'OBJECTID',
        'ID',
        'NAME',
        'FIRESEASON',
        'LASTUPDATETIME',
        'MGMTORGID',
        'MGMTOFFICEID',
        'MGMTOPTIONID',
        'PRESCRIBEDFIRE',
        'LATITUDE',
        'LONGITUDE',
        'MAPNAME',
        'MAPNUMBER',
        'NEARESTWEATHERSTA',
        'ORIGINOWNERID',
        'ORIGINADMINUNITID',
        'DISCOVERYDATETIME',
        'DISCOVERYSIZE',
        'IADATETIME',
        'IASIZE',
        'INITIALBEHAVIOR',
        'CONTROLDATETIME',
        'OUTDATE',
        'ESTIMATEDTOTALACRES',
        'ACTUALTOTALACRES',
        'ESTIMATEDTOTALCOST',
        'GENERALCAUSE',
        'SPECIFICCAUSE',
        'ORIGINSLOPE',
        'ORIGINASPECT',
        'ORIGINELEVATION',
        'ORIGINTOWNSHIP',
        'ORIGINRANGE',
        'ORIGINSECTION',
        'ORIGINQUARTER',
        'ORIGINMERIDIAN',
        'STRUCTURESTHREATENED',
        'STRUCTURESBURNED',
        'PRIMARYFUELTYPE',
        'HARDCOPYREPORTAVAILABLE',
        'TYPE1ASSIGNEDDATE',
        'TYPE1RELEASEDDATE',
        'TYPE2ASSIGNEDDATE',
        'TYPE2RELEASEDDATE',
        'AFSNUMBER',
        'DOFNUMBER',
        'USFSNUMBER',
        'ADDITIONALNUMBER',
        'FALSEALARM',
        'FORCESITRPT',
        'FORCESITRPTSTATUS',
        'RECORDNUMBER',
        'COMPLEX',
        'IMPORT_NOTES',
        'WFUFIRE',
        'REPORTRECEIVEDDATE',
        'ISCOMPLEX',
        'CARRYOVER',
        'STATEADSID',
        'ORIGINAL_LATITUDE',
        'ORIGINAL_LONGITUDE',
        'IRWINID',
        'ISVALID',
        'SUPPRESSIONSTRATEGY',
        'FIREMGMTCOMPLEXITY',
        'ADSPERMISSIONSTATE',
        'OWNERKIND',
        'FIRECODEREQUESTED',
        'ISREIMBURSABLE',
        'ISFSASSISTED',
        'ISTRESPASS',
        'FIRECODENOTES',
        'CONTAINMENTDATETIME',
        'CONFLICTIRWINID',
        'COMPLEXPARENTIRWINID',
        'BURNEDOVER',
        'BURNEDOVERBY',
        'MERGEDINTO',
        'MERGEDDATE'
    ]

    for service in services:
        for group in groups:
            baseurl = '/'.join([ 'http://afs.ak.blm.gov/arcgis/rest/services/MapAndFeatureServices',service,'MapServer' ])
            whereclause = services[ service ] #"FIREYEAR='2016'"

            # Currently (7/18) there is a bug with the API,
            # which is advertising different fields from
            # what it actually can query, so we need to
            # explicitly list the fields we want.
            if service is 'Fires':
                layerlist = all_fires_fields
            else:
                layerlist = None

            # REST key:vals available for use when interacting with the service
            #   * info on the rest service from ESRI: http://resources.arcgis.com/en/help/rest/apiref/mapserver.html
            #   * QUERY params docs: http://resources.arcgis.com/en/help/rest/apiref/query.html
            # QUERY = {
            #     'where' : whereclause,
            #     'text' : '',
            #     'objectIds' : '',
            #     'time' : '',
            #     'geometry' : '',
            #     'geometryType' : 'esriGeometryEnvelope',
            #     'inSR' : '',
            #     'spatialRel' : 'esriSpatialRelIntersects',
            #     'relationParam' : '',
            #     'outFields' : '*',
            #     'returnGeometry' : 'true',
            #     'maxAllowableOffset' : '',
            #     'geometryPrecision' : '',
            #     'outSR' : '',
            #     'returnIdsOnly' : 'false',
            #     'returnCountOnly' : 'false',
            #     'orderByFields' : '',
            #     'groupByFieldsForStatistics' : '',
            #     'outStatistics' : '',
            #     'returnZ' : 'false',
            #     'returnM' : 'false',
            #     'gdbVersion' : '',
            #     'returnDistinctValues' : 'false',
            #     'returnTrueCurves' : 'false',
            #     'resultOffset' : '',
            #     'resultRecordCount' : '',
            #     'f' : 'pjson'
            # }

            #f = FireData( baseurl )

            # after inspecting layers available choose a layerid
            layerid = groups[ group ]

            # [OPTIONAL] return a dict of meta information about the layer of interest
            #f.get_meta( layerid=layerid )

            #f.get_data( layerid, QUERY )

            # use the url generated by requests to issue a system command using subprocess
            output_filename = os.path.join( output_directory, '_'.join([ service.lower(), '2016', group ]) + ext )
            if os.path.exists( output_filename ):
                os.remove( output_filename )

            source = arcgis.ArcGIS( baseurl )
            tmp_file = os.path.join( output_directory, 'TMP_REMOVE_ME.json' )

            # Clean existing tempfile...
            if os.path.exists( tmp_file ):
                os.unlink( tmp_file )

            if os.path.exists( output_filename ):
                os.unlink( output_filename )

            with open( tmp_file, 'w' ) as out_json:
                json.dump( source.get( layerid, whereclause, layerlist ), out_json )

            # convert to the proper system? -- HACKY!!!
            os.system( 'ogr2ogr -f GeoJSON -t_srs EPSG:3338 ' + output_filename + ' ' + tmp_file )
            os.unlink( tmp_file )

    # Clean & join data to yield final output
    process('fires_2016_all.json', 'fireperimeters_2016_all.json', 'fireperimeters_2016_active.json',
        output_directory)

    out_wkt = 'PROJCS["NAD_1983_Alaska_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-154.0],PARAMETER["Standard_Parallel_1",55.0],PARAMETER["Standard_Parallel_2",65.0],PARAMETER["Latitude_Of_Origin",50.0],UNIT["Meter",1.0]]'
    outSR = '3338'
    # perim_prj = 'fireperimeters_2016_all_cleaned_joined.prj'
    # with open( perim_prj, 'w' ) as out:
    #     out.write( out_wkt )

    # pts_prj = 'fires_2016_cleaned_noperim.prj'
    # with open( perim_prj, 'w' ) as out:
    #     out.write( out_wkt )