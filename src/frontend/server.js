var express = require('express');
var app = express();
var path = require('path');
var server = require('http').createServer(app);
var express = require('express');
var session = require('express-session');
var bodyParser = require('body-parser');
var mail = require("nodemailer");
var sessionstore = require('sessionstore');
var os = require("os");


var VERSION = "1";
var port = process.env.PORT || 3000;


//----------------------------- EXPRESS APP SETUP ------------------------------------------//
app.set('trust proxy', 1);
app.use(function(req,res,next){
  if(!req.session){
      return next() //handle error
  }
  next() //otherwise continue
  });
//app.set('views', __dirname + '/views');
//app.engine('html', require('ejs').renderFile);
// Routing
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({secret: 'ssshhfddghjhgewretjrdhfsgdfadvsgvshthhh',
store: sessionstore.createSessionStore(),
resave: true,
saveUninitialized: true
}));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));


server.listen(port, function () {
  console.log('Server listening at port %d', port);
});



