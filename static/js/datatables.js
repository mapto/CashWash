// precondition: this column contains organisation name, next column contains account
function renderOrgAndAcc(data, type, row, settings) {
	var acc = row[settings.col + 1];
	return '<a href="organisation.html?acc=' + acc + '">' +
	  '<span class="org">' + data + '</span>' +
	  '<br/><span class="acc">' + acc + '</span></a>';
}

function renderFetchableAcc(data, type, row, settings) {
	return '<button class="btn btn-primary btn-sm" data-name="' + data + '" onclick="fetchData(\'' + data + '\', \'bank_codes\')">' +
		'<i class="fas fa-download"></i></button> ' + data;
}

function renderFetchableName(data, type, row, settings) {
	return '<button class="btn btn-primary btn-sm" data-name="' + data + '" onclick="fetchData(\'' + data + '\', \'open_corporates\')">' +
		'<i class="fas fa-download"></i></button> ' + data;
}
