$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/organisations",
        columnDefs: [
        	{targets: [0], render: renderOrgAndId},
	        {targets: [1], visible: false}
	    ],
	    order: [[ 4, "desc" ]],
        serverSide: true,
        stateSave: true,
    } );

});
