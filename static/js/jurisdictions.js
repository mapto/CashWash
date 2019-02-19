$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/jurisdictions",
     //    columnDefs: [
     //    	{targets: [1, 3], render: renderOrgAndAcc},
	    //     {targets: [2, 4], visible: false}
	    // ],
	    order: [[ 4, "desc" ]],
        pageLength: 100,
        serverSide: true,
        stateSave: true,
    } );

});
