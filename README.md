# RWTH_HACK_2018 (4-5.05.2018 Aachen)


![GitHub Logo](/documentation/icon_blue_trans.png)


## THE TEAM

* Markus Hoehnerbach
* Marcel Ochsendorf
* Peerapon Wechsuwanmanee
* Weiling Xi

## THE CHALLANGE

The have chosen the real-digital challange for the RWTH Hack 2018. The following problems are to solve:

* Collaborative Ticket System
* No time base ticket blocking




## FEATURES

* simple to use web interface
* desktop notification for ticket events (status changes, attention needed,...)
* email notification for customers
* Account/Login System
* Historical action tracking 
* Advanced ticket filtering/sorting
* Live nofication if an other user edit or review a ticket
* Realtime status update system for ticket changes


## USED ARCHITECTURE

* BACKEND: Python + Flash(Webserver)
* DATABASE: SQL-LITE (embedden in directly in the Backend)
* FRONTEND: Bootstrap 4.0 and Vuejs as templating engine

## SCREENSHOTS (FINAL RESULT)

### Ticket overview / List
![GitHub Logo](/documentation/img/ticket_list_overview.png)

### Ticket sorting system
![GitHub Logo](/documentation/img/tickets_sorting_system.png)

### Detailed ticket view with read/edit nodifications
![GitHub Logo](/documentation/img/ticket_detail_view.png)

### User Account Management System
![GitHub Logo](/documentation/img/admin_account_management.png)


### Simple Ticket Creation Dialouge
![GitHub Logo](/documentation/img/create_ticket.png)


## SETUP

To start the Ticket Server System, simply start the `start.sh` in the root directory of this repo.
After the server started, you can navigate your browser to `127.0.0.1:5000/html/list.html`
You find a detailed documentation about the Ticket System in the `README.md` in the `/src/backend_api/` folder.
