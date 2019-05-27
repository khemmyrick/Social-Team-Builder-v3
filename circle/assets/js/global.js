$( document ).ready(function() {

  $('textarea').autogrow({onInitialize: true});


  //Cloner for infinite input lists
  //Add id iterating logic. . .
  //Use SETTER for id iteration.
  //parent.after(copy) inserts copy after the parent.
  //
  $(".circle--clone--list").on("click", ".circle--clone--add", function(){
	  //when the add button ispressed
	  var parent = $(this).parent("li");
	  console.log(parent);
	  //get parent first list item ancestor of our anchor tag
	  var stf = $("#id_skillset-TOTAL_FORMS").prop("value");
	  console.log("Skillset Total Forms pre-button: ")
	  console.log(stf);
	  //get hidden total forms input value
	  stf++;
	  $("#id_skillset-TOTAL_FORMS").prop("value", stf);
	  //increment total forms value
	  console.log("Skillset Total Forms post-button: ")
	  console.log(stf);
	  var newid = parent.find("*:first-child").prop("id");
	  console.log(newid);
	  var numarray = newid.match(/[0-9]?/g);
	  console.log(numarray);
	  var numstr = numarray.join();
	  console.log(numstr);
	  var foo = numstr.replace(/,/g, "");
	  console.log(foo);
	  var num = parseInt(foo) + 1;
	  console.log(num);
	  var bar = num.toString();
	  console.log(bar);
	  var copy = parent.clone();
	  parent.after(copy);
	  //put new clone with new id after original
	  copy.find("input").prop("id", "id_skillset-" + bar + "-name");
	  copy.find("input").prop("name", "skillset-" + bar + "-id");
	  copy.find("input, textarea, select").val("");
	  //find the clone, set input value to empty
	  copy.find("*:first-child").focus();
	  //focus on empty input
  });

  $(".circle--clone--list").on("click", "li:not(:only-child) .circle--clone--remove", function(){
    var parent = $(this).parent("li");
    parent.remove();
  });

  // Adds class to selected item
  $(".circle--pill--list a").click(function() {
    $(".circle--pill--list a").removeClass("selected");
    $(this).addClass("selected");
  });

  // Adds class to parent div of select menu
  $(".circle--select select").focus(function(){
   $(this).parent().addClass("focus");
   }).blur(function(){
     $(this).parent().removeClass("focus");
   });

  // Clickable table row
  $(".clickable-row").click(function() {
      var link = $(this).data("href");
      var target = $(this).data("target");

      if ($(this).attr("data-target")) {
        window.open(link, target);
      }
      else {
        window.open(link, "_self");
      }
  });

  // Custom File Inputs
  var input = $(".circle--input--file");
  var text = input.data("text");
  var state = input.data("state");
  input.wrap(function() {
    return "<a class='button " + state + "'>" + text + "</div>";
  });




});