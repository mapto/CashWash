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
        "serverSide": true,
        "stateSave": true,
        info: false,
        paging: false,
        searching: false,
        "ajax": "../datatables/aliases/" + id
    } );

    var table = $('#incoming').DataTable( {
        //"processing": true,
        lengthChange: false,
        searching: false,
        pagingType: "simple",
        info: false,
        "serverSide": true,
        "stateSave": true,
        "ajax": "../datatables/incoming/" + id
    } );

    var table = $('#outgoing').DataTable( {
        //"processing": true,
        lengthChange: false,
        pagingType: "simple",
        searching: false,
        info: false,
        "serverSide": true,
        "stateSave": true,
        "ajax": "../datatables/outgoing/" + id
    } );
}