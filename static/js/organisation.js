$(document).ready(function() {
	var url = new URL(location.href);
	var org_acc = url.searchParams.get("account");
	$.ajax({
	  url: "../owner/" + org_acc,
	  success: function(d) {
	  	$("#orgName").text(d.name);
	  	loadOrganisation(d.id);
	  },
	  dataType: "json"
	});
});

function loadOrganisation(id) {
    var table = $('#aliases').DataTable( {
        //"processing": true,
        serverSide: true,
        stateSave: true,
        info: false,
        paging: false,
        searching: false,
        ajax: "../datatables/aliases/" + id
    });

    var table = $('#accounts').DataTable( {
        ajax: "../datatables/accounts/" + id,
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