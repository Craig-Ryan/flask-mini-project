// Jquery that runs the mobile collapse navbar - Initialization section
// https://materializecss.com/sidenav.html#options
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"}); //places sidenav to the right
    $('.collapsible').collapsible(); // Accordion
    $('.tooltipped').tooltip(); // https://materializecss.com/tooltips.html
    $('.datepicker').datepicker({
        format: "dd mmmm yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
  });