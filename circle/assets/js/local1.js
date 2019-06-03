$( document ).ready(function() {
	
  
  $("#djengaadd").on("click", function() {
	  //when the add button is pressed
	  var val = $("input").val();
	  //val is my targeted input
	  if(val !== '') {
		  //Make sure val isn't empty
		  var elem = $("<li></li>").text(val);
		  //create elem, a list item, with text from val
		  $(elem).append("<button class='djengarem'>REMOVE</button>");
		  //add remove button to end of elem
		  $("#djengalist").append(elem);
		  //add elem list item, (li tags, val text, remove button) under djengalist ul tag 
		  $("input").val("");
		  //empty original input box
		  $(".djengarem").on("click", function() {
			  //when remove button is clicked
			  $(this).parent().remove();
			  //remove, obviously
		  });
	  }
  });
  $(".circle--clone--list").on("click", ".circle--clone--add", function(){
	  //when the add button ispressed
	  var parent = $(this).parent("li");
	  //get parent of the list item in this class
	  var num = parseInt(parent.prop("id").match(/[0-9]?/g) ) +1;
	  //find number inside id property, add 1, and pass to variable num
	  var copy = parent.clone().prop("id", "id_skillset-" + num + "name");
	  //clone parent element, add 1 to id, pass to copy variable
	  parent.after(copy);
	  //put new clone with new id after original 
	  copy.find("input, textarea, select").val("");
	  //find the clone, set input value to empty
	  copy.find("*:first-child").focus();
	  //focus on empty input
  });

});