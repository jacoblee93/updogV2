$(document).ready(function() {
	// this function is called when the likes <button> is clicked (in
	// other words, when the button is clicked, an AJAX request is
	// made, given our url mapping, this gives the like_category view
	// which updates the category and returns a new number of likes).
	// When the AJAX request receives the response it updates part of
	// the page (ie. the text and the button)
	$('#likes').click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/like_category/', {category_id: catid}, function(data){
			// increment the HTML element with the id called like_count
			$('#like_count').html(data);
			// hide the likes <button> when when the count has been increased
			$('#likes').hide();
		    });
	    });

    });