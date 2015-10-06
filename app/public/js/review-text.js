// module reviewText
// exports reviewText.add(tooltipObj,dataObj,xVariable,yVariable,isButton)
// this grabs from the database, adds to the DOM and formats accordingly

var reviewText = (function(){

  // MODULE SCOPE VARIABLES
  var tooltip, d, x, y, button;

  // MAIN METHODS
  var addReviews, getReviews, add;

  // add review section to the DOM
  addReviews = function(reviews){
    reviews.forEach(function(r,i){
      var reviewSection = tooltip.append('div')
        .attr('class','review-text');

      // bold relevant terms
      if(y === 'price'){
        var reviewText = util.boldText(r.review,x);
      }else{
        if(r.review.toLowerCase().indexOf(x.toLowerCase()) !== -1){
          var reviewText = util.boldText(r.review,x);
        }
        if(y){
          if(r.review.toLowerCase().indexOf(y.toLowerCase()) !== -1){
            var reviewText = util.boldText(r.review,y);
          }
        }
      }
      reviewSection.html(reviewText);
    })
  }

  // get review data by AJAX request
  getReviews = function(){
    if(!y || y === 'price'){
      var resource = '../seereviews?product='+d['_id']+'&feature1=' +x;
    }else if (y){
      var resource = '../seereviews?product='+d['_id']+'&feature1=' +x 
                  + '&feature2=' + y;
    }
    d3.json(resource, function(error,reviews){
      addReviews(reviews);
    });   
  }

  // add entire review section
  add = function(tt,data,x_var,y_var,btn){

    // set module scope variables
    tooltip = tt;
    d = data;
    x = x_var;
    y = y_var;
    button = btn;

    // button option only shows reviews if btn clicked
    if(button){
      var btn = tooltip.append('btn')
        .attr('class','btn btn-xs btn-default see-reviews-btn')
        .attr('disabled',null)
        .html('See Reviews')
      btn.on('click',function(){
        btn.attr('disabled',true);
        getReviews();
      })
    }
    // otherwise always show the reviews
    else{
      getReviews();
    }
  }

  return {
    add : add
  }
}());