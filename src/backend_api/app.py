import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import json

SQL_SCHEMA = '''
drop table if exists tickets;
create table tickets (
  id integer primary key autoincrement,
  title text not null,
  state text not null,
  created_at text not null,
  last_updated text not null,
  created_by text not null,
  tags text not null
);
drop table if exists interactions;
create table interactions (
  id integer primary key autoincrement,
  ticket_id integer not null,
  sender text not null,
  receiver text not null,
  date text not null,
  content text not null,
  type text not null
);
drop table if exists agents;
create table agents (
  id integer primary key autoincrement
);
'''

# TODO: User management
# TODO: 


# create our little application :)
app = Flask(__name__)
socketio = SocketIO(app)

def connect_db():
    """Connects to the specific database."""
    # TODO: Configuration
    rv = sqlite3.connect('the.db')
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    db.cursor().executescript(SQL_SCHEMA)
    db.commit()

def add_mock_data():
    db = get_db()
    list_mock, interaction_mock = gen_mock_data(7)
    for l_mock in list_mock:
        cur = db.execute('insert into tickets (title, state, created_at, last_updated, created_by, tags) VALUES (?, ?, ?, ?, ?, ?)', l_mock)
    for i_mock in interaction_mock:
        db.execute('insert into interactions (ticket_id, sender, receiver, date, content, type) VALUES (?, ?, ?, ?, ?, ?)', i_mock)    
    db.commit()
    
   
    
def gen_mock_data(num_data):
    '''
    This function create random mock database from a list of predefined data.
    '''
    import random
    from random import randint
    import datetime
    titles = ['Complaints', 'Support', 'Return Request', 'Technical']
    states = ['Open', 'Progress', 'WaitClient', 'Done']
    staffs = ['Nikolas', 'Newton', 'Einstein', 'MickyMouse']
    clients = ['Sarah', 'Curie', 'MinnieMouse']
    tags = []
    list_mock = []
    interaction_mock = []
    for ticket in range(num_data):
        this_title = random.choice(titles)
        this_state = random.choice(states)
        created_at = datetime.date(randint(2005,2017), randint(1,12),randint(1,28))
        last_updated = created_at + datetime.timedelta(randint(1,365))
        created_by = random.choice(staffs)
        list_mock.append([this_title, 
                    this_state,  
                    created_at,              
                    last_updated, 
                    created_by, 
                    '' # tags
                    ])
        if this_state == 'Open':
            num_inter = 1
        else:
            num_inter = random.randint(1,5)
        for i in range(num_inter):
            # define sender
            if i == 0: 
                sender = random.choice(clients)
            else:
                sender = random.choice(staffs + clients)
            # define receiver
            if sender in staffs:
                receiver = random.choice(clients)
            elif sender in clients:
                receiver = random.choice(staffs)
            else:
                receiver = None
            # define date
            if i == 0:
                date = created_at
            else:
                date = created_at + (last_updated - created_at) * random.random()
            # define content
            content = sender + ' is sending this message to ' + receiver 
            # define interaction type
            inter_type = ''
            interaction_mock.append([ticket+1,
                                     sender, 
                                    receiver, 
                                    date, 
                                    content, 
                                    inter_type])
        
    return list_mock, interaction_mock


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    add_mock_data()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('../frontend/public', path)

@app.route('/<name>.js')
def send_static_js(name):
    return flask.send_from_directory('../frontend/public', name + '.js')

@app.route('/<name>.css')
def send_static_css(name):
    return flask.send_from_directory('../frontend/public', name + '.css')

@app.route('/')
def show_spa():
    return flask.send_from_directory('../frontend/public', 'index.html')

# TODO: Allow sorting, filtering and pagination
@app.route('/api/tickets/list')
def list_tickets():
    db = get_db()
    cur = db.execute('select * from tickets')
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)

@app.route('/api/tickets/create', methods=['POST'])
def create_ticket():
    db = get_db()
    ticket = request.json
    cur = db.execute('insert into tickets (title, state, created_at, last_updated, created_by, tags) VALUES (?, ?, ?, ?, ?, ?)', [ticket['title'], ticket['state'], ticket['created_at'], ticket['last_updated'], ticket['created_by'], ticket['tags']])
    db.commit()
    return jsonify({'result': 'ok', 'id': cur.lastrowid})

@app.route('/api/tickets/<int:ticket_id>/show')
def show_ticket(ticket_id):
    db = get_db()
    cur_ticket = db.execute('select * from tickets where id=?', [ticket_id])
    ticket = cur_ticket.fetchone()
    ticket = dict(ticket)
    cur_interactions = db.execute('select * from interactions where ticket_id=?', [ticket_id])
    interactions = cur_interactions.fetchall()
    interactions = list(map(dict, cur_interactions))
    ticket['interactions'] = interactions
    return jsonify(ticket)

@app.route('/api/tickets/<int:ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    db = get_db()
    ticket = request.json
    if ticket_id != ticket.id:
      return jsonify({'result': 'error', 'detail': 'id does not match'})
    cur = db.execute('update tickets (title, state, created_at, last_updated, created_by, tags) VALUES (?, ?, ?, ?, ?, ?) WHERE id=?', [ticket['title'], ticket['state'], ticket['created_at'], ticket['last_updated'], ticket['created_by'], ticket['tags'], ticket_id])
    db.commit()
    return jsonify({'result': 'ok'})

@app.route('/api/tickets/<int:ticket_id>/interactions/create', methods=['POST'])
def create_interaction(ticket_id):
    db = get_db()
    interaction = request.json
    cur = db.execute('insert interactions (interaction_id, sender, receiver, date, content, type) VALUES (?, ?, ?, ?, ?, ?)', [interaction['interaction_id'], interaction['sender'], interaction['receiver'], interaction['date'], interaction['content'], interaction['type']])
    db.commit()
    return jsonify({'result': 'ok', 'id': cur.lastrowid})

@app.route('/api/interactions/list')
def list_interactions():
    db = get_db()
    cur = db.execute('select * from interactions')
    interaction = list(map(dict, cur.fetchall()))
    return jsonify(interaction)

@socketio.on('connected')
def user_connected():
    
    pass

@socketio.on('ticket-opened')
def ticket_opened(data):
    room = 'ticket:{}'.format(data['id'])
    send(json.dumps({'msg': 'Opened by: ' + data['user_name']}), room=room)
    join_room(room)

@socketio.on('ticket-closed')
def ticket_closed():
    room = 'ticket:{}'.format(data['id'])
    leave_room(room)
    send(json.dumps({'msg': 'Closed by: ' + data['user_name']}), room=room)

@socketio.on('ticket-editing')
def ticket_editing():
    pass

@socketio.on('ticket-edited')
def ticket_edited():
    pass

