# Commands

    export FLASK_DEBUG=TRUE
    export FLASK_APP=app.py

    flask run

To initialize the database:

    flask initdb

# Endpoints

    /frontend/index.html = /index.html
    /frontent/* = /static/*
    /api/tickets/list = list of tickets
    /api/tickets/<n>/show = shows details of ticket, including its interactions
    /api/tickets/create POST = create new ticket, returns its ID
    /api/tickets/<n>/update POST = update a ticket
    /api/tickets/<n>/interactions/create POST = create a ticket

# Socket IO

    ticket-opened = when the ticket page is opened, call this event
    ticket-closed = when the ticket page is closed, call this event
    ticket-editing = when the user starts editing something, call this event
    ticket-changed = when the user has edited something, call this event

Clients receive events with fields msg, and send with id=`ticket_id` and `user_name` as their user name.


# Filter in backends
The current available filtering methods are by:
	- state
	- created_older
	- created_newer
	- updated_older
	- updated_newer
	- tag

It can be called by:

http://localhost:5000/api/tickets/search/[method]/[arg]/[sorting]

where 	method is either of the methods above,
		arg is state_name for state, date for [created_older, created_newer, updated_older, updated_newer]
		sorting is either ASC or DESC for ascendent and descrntdent sorting respectively.
		