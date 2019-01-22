$(document).ready(function() {
	$.get({
		url: "../summary",
		contentType: "application/json; charset=utf-8",
		cache: false, // dev 
		dataType: "json",
		success: function(data) {
			$("#intermediaries").text(data["intermediaries"]);
			$("#periodFrom").text(data["period"]["from"]);
			$("#periodTo").text(data["period"]["to"]);
			$("#amount").text(data["amount"]);
		}
	});
});
