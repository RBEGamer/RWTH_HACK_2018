
  // your code goes here

function update_recent_table(){
  $.getJSON( "http://127.0.0.1:5000/api/tickets/list", function( data ) {
    if(data == null || data == undefined){console.log("data empty");return;}
    app.recent_ticket_tems = data
  var sv = 0;
  
    for (i = 0; i < data.length; i++) { 
    if(data[i].state != undefined && data[i].state == "Done"){
      sv++;
      console.log(data.length);
    }
    
  }
    
    app.all_ticket_count = data.length;
    app.solved_ticket_count = sv;
    app.pending_ticket_count = data.length - sv;
});
}




var app = new Vue({
  el: '#app',
  data: {
    all_ticket_count: 1,
    solved_ticket_count:2,
    pending_ticket_count:3,
    recent_ticket_tems: [
      { id: '0',title: 'title1', created_by: 'IT', created_at: '01-04-2018', last_update: 'AAA', state: 'answered', tag: 'OPEN'},
    
    ],
    stuff: [
      { STUFF_ID: 'Stuff0',TICKET_ID: 'ticket#0', STATUS: 'OPEN'},
      { STUFF_ID: 'Stuff1',TICKET_ID: 'ticket#1', STATUS: 'CLOSED'}
    ]
  }
});



update_recent_table();

setInterval(function(){ update_recent_table(); }, 500);




  //alert( "Load was performed." );


