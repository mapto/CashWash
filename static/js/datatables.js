// precondition: this column contains organisation name, next column contains account
function renderOrgAndAcc(data, type, row, settings) {
	var acc = row[settings.col + 1];
	return '<a href="organisation.html?acc=' + acc + '">' +
	  '<span class="org">' + data + '</span>' +
	  '<br/><span class="acc">' + acc + '</span></a>';
}
