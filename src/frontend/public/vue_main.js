
  // your code goes here


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
})



$.getJSON( "http://127.0.0.1:5000/api/tickets/list", function( data ) {
  if(data == null || data == undefined){console.log("data empty");return;}
  app.recent_ticket_tems = data
 
  alert( "Load was performed." );
});

