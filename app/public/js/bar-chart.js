// module barchart
// creates a barchart based on data - transforms and adds to DOM
// exports function barchart.add(domObj,dataObj,[list,of,selections])

var barChart = (function(){

  var add = function(container,dataObj,highlighted){

    // ------ DATA PROCESSING ------ //
    
    // TRANSFORM DATA so it is list of feature-scores
    var features = util.scoredFeatures(dataObj);
    var data = []
    for(i = 0; i < features.length; i++){
      var score = dataObj[features[i]];
      if(features[i] === 'price_scaled'){
        features[i] = 'price';
      }
      if (score){
        data.push({
          'feature':features[i],
          'score':score
        });
      }
    }

    // sort the feature data in descending order
    data = data.sort(function(a, b) { 
      return d3.ascending(a.score, b.score); 
    }).reverse();

    features = []
    for(var i = 0; i < data.length; i++){
      features.push(data[i].feature)
    }


    // ------ SVG SETUP ------ // 

    var margin = {top: 10, right: 20, bottom: 32, left: 100},
      width = 360 - margin.left - margin.right,
      height = 200 - margin.top - margin.bottom;

    // map x values onto numeric scale
    var x = d3.scale.linear()
        .range([0,width])
        .domain([0,5]);
    // setup x axis
    var xAxis = d3.svg.axis()
      .scale(x)
      .orient('bottom')
      .ticks(5)

    // map y value onto ordinal (categorical) scale
    var y = d3.scale.ordinal()
        .rangeRoundBands([0, height], .1)
        .domain(features);
    // setup y axis
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient('left')
        .innerTickSize(0)
        .outerTickSize(0);
    

    // ------ SVG DRAWING / DOM MANIPULATION ------ // 

    // add svg
    var svg = container.append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    // add axes
    .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform','translate(0,' + height + ')')
        .call(xAxis)
      .append('text')
        .attr('x', -8)
        .attr('dx', '.71em')
        .attr('y', 24)
        .text('sentiment score');

    svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis)

    // add each bar
    svg.selectAll('.bar')
        .data(data)
      .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', 0)
        .attr('width', function(d) { return x(d.score);})
        .attr('y', function(d) { return y(d.feature); })
        .attr('height', y.rangeBand())
        .style('fill', function(d){
          if (highlighted.indexOf(d.feature) === -1){ return 'lightgray';} 
          else{ return 'gray';}
        });
  }

  return {
    add : add
  }
}());