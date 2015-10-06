var express = require( 'express' );
var mongodb = require( 'mongodb' );
var ObjectID = require('mongodb').ObjectID;
var jade = require('jade');
var bodyParser = require('body-parser');

// basic server
var app = express();
var server = app.listen(3000,function() {
    console.log('Listening on port %d', server.address().port);
});

// mongodb
var mongoServer = new mongodb.Server('localhost',27017);
var db = new mongodb.Db( 'nofreelunch', mongoServer );

db.open(function( err, db ){
	console.log ('Connected to Mongodb');
});

// config
app.use( express.static(__dirname + '/public') );
app.use(bodyParser.urlencoded( { extended: true }));
app.use(bodyParser.json());

// ROUTING

app.get('/',function(req, res){
	res.redirect('/index.html');
});

// search
app.get('/search', function (req, res){

  var category = req.query.category;

  db.collection('productcategory',function(outer_error,collection){

    if (outer_error) throw outer_error;
    collection.findOne({'name': category},function(inner_error,obj){

      if(inner_error) throw inner_error;
      if(obj){
        var fn=jade.compileFile('server/views/search.jade',{pretty: true});
        var html = fn({
          category: category,
          features: obj.features.slice(0,15)
        })     
      }else{
        var fn=jade.compileFile('server/views/error.jade',{pretty: true});
        var html = fn({
          category: category
        })
      }
      res.send(html);
    });
  });

});

// explore trade-offs
app.get('/exploretradeoffs', function (req, res){

  var category = req.query.category;

  db.collection('productcategory',function(outer_error,collection){

  	if (outer_error) throw outer_error;
  	collection.findOne({'name': category},function(inner_error,obj){

  		if(inner_error) throw inner_error;
  		if(obj){

	   		var fn=jade.compileFile('server/views/exploretradeoffs.jade',{pretty: true});
	  		var html = fn({
	  			category: category,
	  			features: obj.features.slice(0,15)
	  		})

  		}else{
        var fn=jade.compileFile('server/views/error.jade',{pretty: true});
        var html = fn({
          category: category
        })
      }
      res.send(html);
  	});
  });

});

// returns json for tradeoffs
app.get('/tradeoffdata', function (req, res){

  var category = req.query.category;

  db.collection('product',function(outer_error,collection){
    if (outer_error) throw outer_error;

    collection.find({'category': category},{'brand':0,'timestamp':0,'failures':0,
      'category':0})
    .toArray(function(inner_error,data){

      if(inner_error) throw inner_error;
      if(data){
        res.jsonp(data);      
      }else{
        res.send('Error, data not found.');
      }
    });

  });

});

// return correlations for tradeoffs
app.get('/pairs', function (req, res){

  var category = req.query.category;

  db.collection('productcategory',function(outer_error,collection){

    if (outer_error) throw outer_error;
    collection.findOne({'name': category},function(inner_error,data){

      if(inner_error) throw inner_error;
      if(data){
        res.jsonp(data.interesting);      
      }else{
        res.send('Error, data not found');
      }
    });

  });

});

// get reviews
app.get('/seereviews',function(req,res){

  var product_id = req.query.product;
  var feature1 = req.query.feature1;
  var feature2 = req.query.feature2;

  var query = {}

  if(feature2){
    var clause1 = { };
    var clause2 = { };
    clause1[feature1] = true;
    clause2[feature2] = true;
    query['$or'] = [ clause1, clause2 ];

  }else{
    query[feature1] = true;
  }

  query['product_id'] = ObjectID(product_id);

  db.collection('review',function(outer_error,collection){

    if (outer_error) throw outer_error;
    collection.find( query ).toArray(function(inner_error,data){
      if(inner_error) throw inner_error;
      res.jsonp(data);
    });

  });

});

// pick features

app.get('/pickfeatures', function (req, res){

  var category = req.query.category;
  db.collection('productcategory',function(outer_error,collection){
    if (outer_error) throw outer_error;
    collection.findOne({'name': category},{'features': 1},

      function(inner_error,obj){
      if(inner_error) throw inner_error;
      if(obj){
        obj.features.splice(0,0,'price');
        var fn=jade.compileFile('server/views/pickfeatures.jade',{pretty: true});
        var html = fn({
          category: category,
          features: obj.features.slice(0,15),
          lookup: ['1st','2nd','3rd','4th','5th','6th','7th']
        })
      }else{
        var fn=jade.compileFile('server/views/error.jade',{pretty: true});
        var html = fn({
          category: category
        })
      }
      res.send(html);
    });

  });

});

// scoring - calculates weighted scores according to query params
app.get('/getscores', function (req, res){

  var category = req.query.category;

  // get the requested features
  var choices = [];
  for(key in req.query){
    if (key.indexOf('choice') !== -1){
      if(req.query[key]){
        if(req.query[key] === 'price'){
          var feature = 'price_scaled';
        }else{
          var feature = req.query[key];
        }
        choices.push(feature);
      }
    }
  }
  // setup for weighting
  var numChoices = choices.length;
  var denom = 0;
  for(var i = 1; i < numChoices + 1; i++){
    denom += i;
  }

  // comparator for sorting
  function compare(a,b) {
    if (a.score > b.score)
       return -1;
    if (a.score < b.score)
      return 1;
    return 0;
  }

  db.collection('product',function(outer_error,collection){

    if (outer_error) throw outer_error;
    collection.find({'category': category},{'brand':0,'category':0,'timestamp':0,'failures':0})
    .toArray(function(inner_error,data){

      if(inner_error) throw inner_error;
      if(data){

        // compute weighted score for each data object
        for(var j = 0; j < data.length; j++){

          data[j]['score'] = 0;
          for(var k = numChoices, l = 0; k > 0, l < numChoices; k--, l++){

            data[j]['score'] += (k*data[j][choices[l]])/denom;
            // scores for each feature will also be recorded
            if(data[j][choices[l]]){
              data[j][choices[l]] = data[j][choices[l]].toFixed(1);
            }
          }
          data[j]['score'] = data[j]['score'].toFixed(1);
        }

        res.jsonp(data.sort(compare)); 

      }else{
        res.send('Error, data not found');
      }
    });
  });

});

// ERROR HANDLING
app.use(function(err, req, res, next){
  console.error(err.stack);
  res.redirect('/');
});

app.use(function(req, res, next){
  res.redirect('/');
});