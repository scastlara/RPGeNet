/*==================================================
overlays.js - Setting the overlays of the index page
==================================================*/

// INPUT GENES
$(".inputgenes-btn").on("click", function() {
	$("#inputgenes-dialog").slideToggle(450);
});

$("#close-inputgenes-btn").on("click", function() {
	$("#inputgenes-dialog").hide();
});

// GENEDISTANCE
$(".genedistance-btn").on("click", function() {
	$("#genedistance-dialog").slideToggle(450);
});

$("#close-genedistance-btn").on("click", function() {
	$("#genedistance-dialog").hide();
});

// INTLVL
$(".intlvl-btn").on("click", function() {
	$("#intlvl-dialog").slideToggle(450);
});

$("#close-intlvl-btn").on("click", function() {
	$("#intlvl-dialog").hide();
});

// GENEXP
$(".genexp-btn").on("click", function() {
	$("#genexp-dialog").slideToggle(450);
});

$("#close-genexp-btn").on("click", function() {
	$("#genexp-dialog").hide();
});