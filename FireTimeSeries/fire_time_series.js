'use strict';

var http = require('http');
var moment = require('moment');
var fs = require('fs');

var geoserver_url = 'http://localhost:8080/geoserver';
var url = geoserver_url + '/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=geonode:active_fires&srsName=EPSG:3338&outputFormat=application/json&bbox=-2255938.4795,449981.1884,1646517.6368,2676986.5642';
var filename = 'output/' + moment().format('YYYY') + '.json';
var series;

if (fs.existsSync(filename)) {
  fs.readFile(filename, 'utf-8', function (err, data) {
    if (err) {
      return console.error(err);
    }
    series = JSON.parse(data);
  });
} else {
  series = [];
}

http.get(url, function (res) {
  var body = '';
  var acres = 0;
  res.on('data', function(chunk){
    body += chunk;
  });
  res.on('end', function(){
    var parsed = JSON.parse(body);

    parsed.features.forEach(function (feature) {
      acres += feature.properties.ACRES;
    });

    series.push([moment().format('MMMM D'), acres]);

    fs.writeFile(filename, JSON.stringify(series), function (err) {
      if (err) {
        return console.error(err);
      }
    });
  });
});
