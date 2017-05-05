'use strict';

var http = require('http');
var moment = require('moment');
var fs = require('fs');

var url = 'http://mv-aicc-fire-shim-mv-aicc-fire-shim.openshift.snap.uaf.edu/';
var outputDir;

if (process.env.OUTPUT_DIR === undefined) {
  console.error('You need to set the OUTPUT_DIR environment variable.');
  process.exit();
} else {
  outputDir = process.env.OUTPUT_DIR;
}

var filename = outputDir + '/' + moment().format('YYYY') + '.json';
var series = {};

if (fs.existsSync(filename)) {
  fs.readFile(filename, 'utf-8', function (err, data) {
    if (err) {
      return console.error(err);
    }
    series = JSON.parse(data);
  });
} else {
  series.dates = [];
  series.acres = [];
}

http.get(url, function (res) {
  var body = '';
  var acres = 0;

  res.on('data', function(chunk) {
    body += chunk;
  });

  res.on('end', function() {
    var parsed = JSON.parse(body);

    parsed.features.forEach(function (feature) {
      acres += feature.properties.ESTIMATEDTOTALACRES;
    });

    series.dates.push(moment().format('MMMM D'));
    series.acres.push(acres);

    fs.writeFile(filename, JSON.stringify(series), function (err) {
      if (err) {
        return console.error(err);
      }
    });
  });
});
