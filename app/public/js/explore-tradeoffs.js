// explore-tradeoffs.js
// gets data for explore tradeoffs, creates UI based on data
// passes the data to scatterplot, bar-chart, review-text modules.

 window.onload = function(){ 

  var current_url = document.location.toString();
  var parsed = current_url.split('?');
  var category = parsed[1];

  // get data
  d3.json('/tradeoffdata?'+category, function(error, data) {
    features = util.scoredFeatures(data[data.length-1]);
    // for each feature, add scatterplot and buttons
    features.forEach(function(f,i){
      scatterplot.addScatterplot(data,f,'price');
      var btn = d3.select('#relationships').append('button')
      btn.attr('class','btn btn-relationship btn-xs price ' 
        + util.className(f));
      btn.text(f +', price');
    });
    
    // for each correlation pair, add scatterplot and buttons
    d3.json('/pairs?'+category,function(error,pairs){
      pairs.forEach(function(p,i){
        scatterplot.addScatterplot(data,p[0],p[1]);
        var btn = d3.select('#relationships').append('button')
          btn.attr('class','btn btn-relationship btn-xs ' 
            + util.className(p[0]) + ' '
            + util.className(p[1]));
          btn.text(p[0] +', ' + p[1]);
      });
    })
  });


  // maintain a record of what is clicked
  var featureButtons = d3.selectAll('.btn-default')[0];
  var clicked = []
  for(var i = 0; i < featureButtons[0].length; i++){
    clicked[i] = false;
  }
  // bind click events for each feature button
  featureButtons.forEach(function(button,i){

    // convert to d3 object
    var button = d3.select(button); 

    button.on('click',function(){

      // manage toggling
      var display, background;
      if(clicked[i]){

        display = 'none';
        clicked[i] = false;
        background = 'white';
        d3.selectAll('svg').style('display','none');
        d3.selectAll('.tooltip').style('opacity',0);
        // // reset relationship buttons
        d3.selectAll('.'+util.className(button.text()) +':not(svg)')
          .style('background','lightgray')
          .style('color','black');

      }else{

        display = 'inline-block'
        clicked[i] = true;
        background = 'lightgray'

      }
      button.style('background-color',background);
      d3.select('#relationships').style('display',display);
      var relationshipButtons = d3.selectAll('.'+util.className(button.text()) +':not(svg)')
      .style('display',display);

      // bind click events for relationship buttons
      var clickedRel = false;
      relationshipButtons[0].forEach(function(button,j){

        var button = d3.select(button); 

        button.on('click',function(){

          // manage toggling

          // clear all the old colors
          d3.selectAll('.btn-relationship').style('background','lightgray').style('color','black');
          var display,background,color;

          if(clickedRel){
            display = 'none';
            background = 'lightgray';
            textColor = 'black';

          }else {
            display = 'block';
            background = 'gray';
            textColor = 'white';
          }

          var classes = button.attr('class');
          classes = classes.split(' ');
          classes = classes.slice(classes.length-2);
          // clear all previous svg, reset
          d3.selectAll('svg').style('display','none');
          d3.selectAll('svg').filter('.'+classes[0]).filter('.'+classes[1])
            .style('display',display);
          button.style('background',background).style('color',textColor);
          // clear all previous tooltips
          d3.selectAll('.tooltip').style('opacity',0);
        });
      });
    });
  });
}