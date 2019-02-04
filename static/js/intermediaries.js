$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/intermediaries",
        columnDefs: [
        	{targets: [3], render: renderOrgAndAcc},
	        {targets: [4], visible: false}
	    ],
	    order: [[ 0, "desc" ]],
        serverSide: true,
        stateSave: true
    } );
});
