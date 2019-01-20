$(document).ready(function() {
	$.get({
		url: "../partials/menu.html",
		dataType: "html",
		cache: false, // dev 
		success: function( data ) {
			$("header").html(data);

			$("header nav li").each(function(){
				$(this).removeClass("active");
				if (location.href.endsWith($("a", this).attr("href"))) {
					$(this).addClass("active");
				}
			});
		}
	});
});
