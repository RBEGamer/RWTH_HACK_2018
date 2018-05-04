var socket = null;

function guid() {
    function s4() {
      return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
      s4() + '-' + s4() + s4() + s4();
  }

  function reps_guid() {
    function s4() {
      return Math.floor((1 + Math.random()) * 0x10000)
        .toString(8)
        .substring(1);
    }
    return s4() + s4()  + s4()  + s4();
  }
function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes;
    return strTime;
}            




$(function () {
    socket = io();
    socket.emit('event', reps_guid());

    socket.on('message', function (data) {
       console.log(data);


       console.log(data.event_type);

       if(data.event_type == "push"){
        Push.create(data.payload.header.toString() , {
            body: data.payload.message.toString(),
            icon: './img/icon/ticket_256.png',
            timeout: 4000,
            onClick: function () {
                window.location 
                window.focus();
                this.close();
            }
        });
        
       }
      });
});