const ppAmount = (x) => {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

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
			$("#amount").text(ppAmount(data["amount"]));
		}
	});
});
