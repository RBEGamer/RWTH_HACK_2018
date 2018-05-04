var app = new Vue({
  el: '#app',
  data: {
    all_ticket_count: 1,
    items: [
      { TICKET_ID: '0',TICKET_TITLE: 'title1', DEPARTMENT: 'IT', DATE: '01-04-2018', CLIENT: 'AAA', LAST_ACTION: 'answered', STATUS: 'OPEN'},
      { TICKET_ID: '1',TICKET_TITLE: 'title0', DEPARTMENT: 'IT', DATE: '04-01-2018', CLIENT: 'BBB', LAST_ACTION: 'not answered', STATUS: 'CLOSED'}
    ],
    stuff: [
      { STUFF_ID: 'Stuff0',TICKET_ID: 'ticket#0', STATUS: 'OPEN'},
      { STUFF_ID: 'Stuff1',TICKET_ID: 'ticket#1', STATUS: 'CLOSED'}
    ]
  }
})