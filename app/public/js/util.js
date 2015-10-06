// util module has various helper functions

var util = (function(){

  var scoredFeatures = function(dataObj){
    features = Object.keys(dataObj);
    features.splice(features.indexOf('name'),1);
    features.splice(features.indexOf('_id'),1);
    features.splice(features.indexOf('url'),1);
    features.splice(features.indexOf('price'),1);
    if(features.indexOf('score') !== -1){
      features.splice(features.indexOf('score'),1);
    }
    return features;
	}

  var className = function(str){
    // remove special characters
    str = str.replace(/[^a-zA-Z ]/g,'');
    return str.split(' ').join('-');
  }

  var boldText = function(str,target){
    var strLower = str.toLowerCase();
    var startBold = strLower.indexOf(target.toLowerCase());
    var endBold = startBold + target.length;
    return str.slice(0,startBold) + '<b>' + 
      str.slice(startBold,endBold) + '</b>' +
      str.slice(endBold,str.length+7);
  }

	return {
		boldText: boldText,
		scoredFeatures : scoredFeatures,
		className: className
	}
  
}());