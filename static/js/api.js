function fetchData(value, api) {
	$.get({
		url: "../api/" + api + "/" + value,
		contentType: "application/json; charset=utf-8",
		cache: false, // dev 
		dataType: "json",
		success: function(data) {
			console.log(JSON.stringify(data));
		}
	});	
}

