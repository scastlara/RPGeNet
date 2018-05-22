// This script contains the general behaviour of card overlay divs

$('.card-overlay').hide();
$('.close-overlay').hide();

$('.close-overlay').click(function(){
    $('.card-overlay').hide(250);
    $('.close-overlay').hide();
});

$(document).keyup(function(e) {
    if(e.keyCode== 27) {
        $('.card-overlay').hide(250);
        $('.close-overlay').hide();

    }
});

 $('.close-overlay').click(function(event){
     event.stopPropagation();
 });
