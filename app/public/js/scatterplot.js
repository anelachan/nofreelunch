// scatterplot.js
// builds a scatterplot based on data and x and y variables
// exports scatterplot.addScatterplot(data,x,y)
// based off tutorial by Mike Bostocks, creator of d3.js

var scatterplot = (function(){

  var addScatterplot = function(data,x,y){

    // ------ DATA PROCESSING ------ //

    // filter blank values
    data = data.filter(function(d){
      if(isNaN(d[x]) || isNaN(d[y]) || !d[x] || !d[y]){
          return false;
      }
      return true;
    });

    // ------ SVG SETUP ------ //  

    // graph properties
    var margin = {top: 20, right: 10, bottom: 30, left: 40},
    width = 600 - margin.left - margin.right,
    height = 390 - margin.top - margin.bottom;

    // setup x 
    var xValue = function(d) { return d[x];}, 
        xScale = d3.scale.linear().range([0, width]),
        xMap = function(d) { return xScale(xValue(d));}, 
        xAxis = d3.svg.axis().scale(xScale).orient('bottom');
    // rescale x
    xScale.domain([d3.min(data, xValue)-.4,d3.max(data, xValue)]);

    // setup y
    var yValue = function(d) { return d[y];},
        yScale = d3.scale.linear().range([height, 0]),
        yMap = function(d) { return yScale(yValue(d));},
        yAxis = d3.svg.axis().scale(yScale).orient('left');

    // rescale y
    if(y === 'price'){
      yScale.domain([d3.max(data, yValue)+1, d3.min(data, yValue)-1]);
    } else{
      yScale.domain([d3.min(data, yValue)-.4,d3.max(data, yValue)])
    }

    // setup fill color scale
    var color = d3.scale.linear()
        .range(['red','green'])
        .domain([1,25]);
    // different scale for price
    var priceScale = d3.scale.linear()
      .domain([d3.min(data,yValue),d3.max(data,yValue)])
      .range([5,1]);


    // ------ SVG DRAWING / DOM MANIPULATION ------ //     

    // add the graph canvas to the body of the webpage
    var svg = d3.select('.charts').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .attr('class', util.className(x) + ' ' + util.className(y))
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    // add the tooltip area to the webpage
    var tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);

    // x-axis
    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis)
      .append('text')
        .attr('class', 'label')
        .attr('x', width)
        .attr('y', -6)
        .style('text-anchor', 'end')
        .text(x + ' sentiment');

    // y-axis
      // set axisLabel
    if(y === 'price'){ var axisLabel = y;}
    else{ var axisLabel = y + ' sentiment';}
    svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
      .append('text')
        .attr('class', 'label')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text(axisLabel);

    // draw dots
    svg.selectAll('.dot')
        .data(data)
      .enter().append('circle')
        .attr('class', 'dot')
        .attr('r', 5)
        .attr('cx', xMap)
        .attr('cy', yMap)
        .attr('stroke-width',0)
        // fill color according to scale/type
        .style('fill', function(d) {
          if(y === 'price'){ return color(d[x]*priceScale(d[y]));}
          else{ return color(d[x]*d[y]);}
        }) 

        // ------ EVENT HANDLER ------ //
        .on('mouseover', function(d) {
          // display tooltip
          tooltip.transition()
            .duration(500)
            .style('opacity',0);
          tooltip.transition()
             .duration(200)
             .style('opacity', 1);
          tooltip.html('<a href="' + d['url'] + '">' + d['name'] + 
              '</a> $' +d['price'])
          
          // tooltip includes bar chart and contextual reviews
          var highlighted = [x,y];
          barChart.add(tooltip,d,highlighted);
          reviewText.add(tooltip,d,x,y,false);

        })
  }

  return {
    addScatterplot: addScatterplot
  }
  
}());