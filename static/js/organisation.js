$(document).ready(function() {
	var url = new URL(location.href);
	var org_id = url.searchParams.get("org");
	var org_acc = url.searchParams.get("acc");
	if (org_id) {
		loadOrganisation(org_id);
	} else if (org_acc) {
		$.ajax({
		  url: "../owner/" + org_acc,
		  success: function(d) {
		  	$("#orgName").text(d.name);
		  	loadOrganisation(d.id);
		  },
		  dataType: "json"
		});
	}
});

function loadOrganisation(id) {
    var table = $('#aliases').DataTable( {
        ajax: "../datatables/aliases/" + id,
        //"processing": true,
        columnDefs: [
            {targets: [0], render: renderFetchableName}
        ],
        info: false,
        paging: false,
        serverSide: true,
        stateSave: true,
        searching: false
    });

    var table = $('#accounts').DataTable( {
        ajax: "../datatables/accounts/" + id,
        columnDefs: [
            {targets: [0], render: renderFetchableAcc}
        ],
        info: false,
        serverSide: true,
        stateSave: true,
        paging: false,
        searching: false,
    });

    var table = $('#incoming').DataTable( {
        ajax: "../datatables/incoming/" + id,
        info: false,
        lengthChange: false,
        order: [[0, "desc"]],
        pagingType: "simple",
        searching: false,
        serverSide: true,
        stateSave: true
    });

    var table = $('#outgoing').DataTable( {
        ajax: "../datatables/outgoing/" + id,
        info: false,
        lengthChange: false,
        order: [[0, "desc"]],
        pagingType: "simple",
        searching: false,
        serverSide: true,
        stateSave: true
    });
}