// pick-features.js
// handles the form submission and results creation for pick features
// gets data based on user choices and passes to bar-chart, review-text modules.

$(document).ready(function(){

	// FORM HANDLING
	var numFeatures = $('#choice-1').children().length -1;
	var $choiceForm = $('#get-score');

	// event handlers - change events for each select
	for(var i = 1; i < numFeatures+1; i++){
		// requires a closure to save namespace
		var bindChangeEvent = function(){
			var selectName = '#choice-'+ i;
			var $obj = $(selectName);
			var nextSelectName = '#choice-' + (i+1);

			// once a feature is selected, remove it from the other selects
			$obj.change(function(){
				if($obj.val().length > 0){
					$(nextSelectName+'-group').show();
					var $notSelected = $obj.children().not(':selected').clone();
					$(nextSelectName).empty();
					for(var i = 0; i < $notSelected.length; i++){
						$(nextSelectName).append($notSelected[i]);
					}
				}
			})
		}
		bindChangeEvent();
	}

	// MANAGING PAGINATION - TO BE USED IN RESULTS
	// technically this shouldn't happen until after the table is 
	// created, but we'll wait for the return of data.
	var toggle = function($toHide,$toShow){
		$toHide.forEach(function(t,i){
			$(t).hide();
		});
		$toShow.forEach(function(t,i){
			$(t).show();
		})
	}
	var managePagination = function(){
		var upTo = 8;
		var start = 0;
		$tr = $('tr').not('tr:first')
		$('#next-button').on('click',function(){
			$toShow = $tr.toArray().slice(start+8,upTo+8);
			$toHide = $tr.not($toShow).toArray();
			toggle($toHide,$toShow);
			upTo = upTo + 8;
			start = start + 8;
			if (upTo > $tr.length){
				$('#next-button').prop('disabled',true);
			}
			if(start > 0){
				$('#prev-button').prop('disabled',false);
			}
		});
		
		$('#prev-button').on('click',function(){
			$toShow = $tr.toArray().slice(start-8,upTo-8);
			$toHide = $tr.not($toShow).toArray();
			toggle($toHide,$toShow);
			upTo = upTo - 8;
			start = start - 8;
			if(upTo < $tr.length){
				$('#next-button').prop('disabled',false);
			}
			if(start < 8){
				$('#prev-button').prop('disabled',true);
			}
		});	
	}

	// SUBMITTING THE FORM
	$choiceForm.on('submit',function(e){

		e.preventDefault();
		$(this).hide();

		$(this).ajaxSubmit({

			error: function(xhr) {
        $choiceForm.show();
        $('.message-text').text('Error communicating with server. Please try again.');
      },

	    success: function(data) {

	    	// write out selections
	    	var selections = $("option:selected").map(function(){ 
	    		return this.value }).get();

	    	if(selections[0].length === 0){
	    		$('.message-text').html('You did not make any selections. <br><a href="index.html">Start over.</a>');
	    	}
	    	else{
		    	for(var i = 1; i < selections.length; i++){
		    		var choiceText = i +'. ' + selections[i-1] + ' ';
		    		$('#you-selected h4').append(choiceText);
		    	}
		    	$('#you-selected').show();

			    // setup color scale for numbers
		    	var color = d3.scale.linear()
		        .range(['red','green'])
		        .domain([0,5]);

		    	// create a table w/ info of each
		      // append rows to table based on data
		    	$('#results').show();
		    	var table = d3.select('tbody');

		    	data.forEach(function(d,i){

		    		if(d.score && d.score > 0){
		    			
		    			// create a tooltip w/ bar chart and review text
		    			var tooltip = d3.select('body').append('div')
				        .attr('class', 'tooltip')
				        .style('opacity',0)
			       		.html('<a href="' + d['url'] + '">' + d['name'] + 
	            '</a> $' +d['price']);
	            barChart.add(tooltip,d,selections); 
	    

				    	// create a table row for each one
			 				var tr = table.append('tr');
			 				tr.append('td')
								.attr('class','score')
								.style('color',color(d.score))
								.html(d.score);
							tr.append('td')
								.attr('class','product-details')
								.html('<a href="'+d.url+'">'+d.name+'</a>');
							tr.append('td')
								.html('$'+d.price);

							// event handlers - for mousing over the row
	            tr.on('mouseover', function() {
	            	// clear old reviews
	            	d3.selectAll('.review-text').remove();
	            	// add them again - this has to be placed hear because of async
		            tooltip.transition()
		             .duration(400)
		             .style('opacity', 1);
					    });

	            tr.on('click', function() {
	            	// clear old reviews
	            	d3.selectAll('.review-text').remove();
	            	// add them again - this has to be placed hear because of async
	            	reviewText.add(tooltip,d,selections[0],selections[1],false);
					    });

					    tr.on('mouseout',function(){
	            	tooltip.transition()
	               .duration(800)
	               .style('opacity', 0);
	              d3.selectAll('.review-text').remove();
					    });
		    		}
		    	});
					managePagination();
	    	}
	    }
		});
	});
});