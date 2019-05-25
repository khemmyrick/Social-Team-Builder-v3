$( document ).ready(function() {

  $('textarea').autogrow({onInitialize: true});


  //Cloner for infinite input lists
  //Add id iterating logic. . .
  //Use SETTER for id iteration.
  //parent.after(copy) inserts copy after the parent.
  //
  $(".circle--clone--list").on("click", ".circle--clone--add", function(){
    var parent = $(this).parent("li");
	var num = parseInt(parent.prop("id").match(/\d+/g), 10 ) +1;
    var copy = parent.clone().prop("id", "id_skillset-" + num + "name" );
    parent.after(copy);
    copy.find("input, textarea, select").val("");
    copy.find("*:first-child").focus();
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