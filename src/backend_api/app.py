import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import flask
from flask_socketio import SocketIO, emit, join_room, leave_room, send
import json
from flask_bcrypt import Bcrypt
import datetime 
import dateutil.parser

SQL_SCHEMA = '''
drop table if exists tickets;
create table tickets (
  id integer primary key autoincrement,
  title text not null,
  state text not null,
  created_at text not null,
  last_updated text not null,
  created_by text not null,
  tags text not null,
  real_time_state text not null,
  users_looking text not null,
  total_users_looking int not null,
  users_editing text not null,
  total_users_editing int not null
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
  id integer primary key autoincrement,
  is_admin integer not null,
  name text not null,
  email text not null,
  password text not null
);
'''

# TODO: User permissions, not included for development

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# create our little application :)
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)
bcrypt = Bcrypt(app)

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

def add_standard_agents():
    db = get_db()
    db.execute('insert into agents (is_admin, name, email, password) VALUES (0, "System", "system@system", "")')
    db.execute('insert into agents (is_admin, name, email, password) VALUES (1, "Admin", "admin@admin", ?)', [bcrypt.generate_password_hash('hunter2')])
    db.execute('insert into agents (is_admin, name, email, password) VALUES (0, "Default Agent", "default@agent", ?)', [bcrypt.generate_password_hash('hunter2')])
    db.commit()

def add_mock_data():
    db = get_db()
    list_mock, interaction_mock = gen_mock_data(7)
    for l_mock in list_mock:
        cur = db.execute('insert into tickets (title, state, created_at, last_updated, created_by, tags, real_time_state, users_looking, total_users_looking, users_editing, total_users_editing) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', l_mock)
    for i_mock in interaction_mock:
        db.execute('insert into interactions (ticket_id, sender, receiver, date, content, type) VALUES (?, ?, ?, ?, ?, ?)', i_mock)    
    db.commit()
    
    
def gen_mock_data(num_data):
    '''
    This function create random mock database from a list of predefined data.
    '''
    import random
    from random import randint
    titles = ['Complaints', 'Support', 'Return Request', 'Technical']
    states = ['Open', 'Progress', 'WaitClient', 'Done']
    staffs = ['Nikolas', 'Newton', 'Einstein', 'MickyMouse']
    clients = ['Sarah', 'Curie', 'MinnieMouse']
    tags = ['IT', 'sales', 'return', 'order', 'tracking', 'etc']
    list_mock = []
    interaction_mock = []
    for ticket in range(num_data):
        this_title = random.choice(titles)
        this_state = random.choice(states)
        created_at = datetime.date(randint(2005,2017), randint(1,12),randint(1,28))
        last_updated = created_at + datetime.timedelta(randint(1,365))
        created_by = random.choice(staffs)
        this_tag = random.choice(tags)
        # define real_time_state
        real_time_state = {}
        for num_realtime in range(random.randint(0, len(staffs))):
            staff_edit = random.choice(staffs)
            real_time_state[staff_edit] = (created_at + (last_updated - created_at) * random.random()).strftime("%Y-%m-%d")
        users_looking = random.sample(real_time_state.keys(), random.randint(0, len(real_time_state)))
        total_looking = len(users_looking)
        users_editing = random.sample(users_looking, random.randint(0, total_looking))
        total_editing = len(users_editing)
        list_mock.append([this_title, 
                    this_state,  
                    created_at,              
                    last_updated, 
                    created_by, 
                    this_tag,
                    json.dumps(real_time_state),
                    json.dumps(users_looking),
                    total_looking,
                    json.dumps(users_editing),
                    total_editing
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
            if sender in staffs:
                inter_type = 'ours'
            else:
                inter_type = 'theirs'
            
            random.randint
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
    add_standard_agents()
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

@app.route('/static2/<path:path>')
def send_static2(path):
    return flask.send_from_directory('static', path)

@app.route('/html/<path:path>')
def send_html(path):
    return flask.render_template(path)

@app.route('/<name>.js')
def send_static_js(name):
    return flask.send_from_directory('../frontend/public', name + '.js')

@app.route('/<name>.css')
def send_static_css(name):
    return flask.send_from_directory('../frontend/public', name + '.css')



@app.route('/bower_components/<path:path>')
def send_static_bower(path):
    return flask.send_from_directory('../frontend/public/bower_components', path)


@app.route('/')
def show_spa():
    return flask.send_from_directory('../frontend/public', 'index.html')

# TODO: Allow sorting, filtering and pagination
@app.route('/api/tickets/list')
def list_tickets():
    db = get_db()
    cur = db.execute('select * from tickets')
    tickets = list(map(dict, cur.fetchall()))
    for ticket in tickets:
        ticket['real_time_state'] = json.loads(ticket['real_time_state'])
        ticket['users_looking'] = json.loads(ticket['users_looking'])
        ticket['users_editing'] = json.loads(ticket['users_editing'])
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
    ticket['real_time_state'] = json.loads(ticket['real_time_state'])
    ticket['users_looking'] = json.loads(ticket['users_looking'])
    ticket['users_editing'] = json.loads(ticket['users_editing'])
    cur_interactions = db.execute('select * from interactions where ticket_id=? order by date ASC', [int(ticket_id)])
    interactions = cur_interactions.fetchall()
    interactions = list(map(dict, interactions))
    ticket['interactions'] = interactions
    return jsonify(ticket)

@app.route('/api/tickets/<int:ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    db = get_db()
    ticket = request.json
    if ticket_id != ticket.id:
      return jsonify({'result': 'error', 'detail': 'id does not match'})
    cur = db.execute('update tickets set title = ?, state = ?, created_at = ?, last_updated = ?, created_by = ?, tags = ? where id=?', [ticket['title'], ticket['state'], ticket['created_at'], ticket['last_updated'], ticket['created_by'], ticket['tags'], ticket_id])
    db.commit()
    return jsonify({'result': 'ok'})
@app.route('/api/tickets/search/state/<string:state>/<string:sorting>')
def filter_ticket_state(state, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where state=? order by created_at ASC', [state])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where state=? order by created_at DESC', [state])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)
@app.route('/api/tickets/search/created_older/<string:date>/<string:sorting>')
def filter_ticket_created_older(date, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where create_at<=? order by created_at ASC', [date])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where created_at<=? order by created_at DESC', [date])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)
@app.route('/api/tickets/search/created_newer/<string:date>/<string:sorting>')
def filter_ticket_created_newer(date, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where create_at>=? order by created_at ASC', [date])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where created_at>=? order by created_at DESC', [date])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)
@app.route('/api/tickets/search/updated_older/<string:date>/<string:sorting>')
def filter_ticket_updated_older(date, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where last_updated<=? order by created_at ASC', [date])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where last_updated<=? order by created_at DESC', [date])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)
@app.route('/api/tickets/search/updated_newer/<string:date>/<string:sorting>')
def filter_ticket_updated_newer(date, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where last_updated>=? order by created_at ASC', [date])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where last_updated>=? order by created_at DESC', [date])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)
@app.route('/api/tickets/search/tags/<string:tag>/<string:sorting>')
def filter_ticket_tags(tag, sorting):
    db = get_db()
    if sorting == 'ASC':
        cur = db.execute('select * from tickets where tag=? order by created_at ASC', [tag])
    elif sorting == 'DESC':
        cur = db.execute('select * from tickets where tag=? order by created_at DESC', [tag])
    tickets = list(map(dict, cur.fetchall()))
    return jsonify(tickets)

@app.route('/api/tickets/<int:ticket_id>/interactions/create', methods=['POST'])
def create_interaction(ticket_id):
    db = get_db()
    interaction = request.json
    cur = db.execute('insert into interactions (ticket_id, sender, receiver, date, content, type) VALUES (?, ?, ?, ?, ?, ?)', [interaction['ticket_id'], interaction['sender'], interaction['receiver'], interaction['date'], interaction['content'], interaction['type']])
    db.commit()
    return jsonify({'result': 'ok', 'id': cur.lastrowid})


@app.route('/api/interactions/list')
def list_interactions():
    db = get_db()
    cur = db.execute('select * from interactions')
    interaction = list(map(dict, cur.fetchall()))
    return jsonify(interaction)

@app.route('/api/agents/create', methods=['POST'])
def def_agent():
    db = get_db()
    agent = request.json
    cur = db.execute('insert into agents (is_admin, name, email, password) VALUES (?, ?, ?, ?)', [agent['is_admin'], agent['name'], agent['email'], bcrypt.generate_password_hash(agent['password'])])
    db.commit()
    return jsonify({'result': 'ok', 'id': cur.lastrowid})

@app.route('/api/agents/<int:agent_id>/update', methods=['POST'])
def update_agent(agent_id):
    db = get_db()
    agent = request.json
    if agent_id != agent['id']:
      return jsonify({'result': 'fail', 'error': 'Agent ID mismatch'})
    db.execute('update agents set is_admin = ?, name = ?, email = ?, password = ? where id = ?', [agent['is_admin'], agent['name'], agent['email'], bcrypt.generate_password_hash(agent['password']), agent_id])
    db.commit()
    return jsonify({'result': 'ok'})

@app.route('/api/agents/list')
def list_agent():
    db = get_db()
    cur = db.execute('select name, email, is_admin, id from agents')
    agents = list(map(dict, cur.fetchall()))
    return jsonify(agents)

@app.route('/api/login', methods=['POST'])
def login_agent():
    db = get_db()
    cur = db.execute('select * from agents where email=?', [request.form['email']])
    user = cur.fetchone()
    if user is None:
        flask.flash('Login failed')
        return redirect("/html/login.html", code=302)
    if bcrypt.check_password_hash(user['password'], request.form['password']):
        session['id'] = user['id']
        session['is_admin'] = user['is_admin']
        session['name'] = user['name']
        return redirect("/", code=302)
    flask.flash('Login failed')
    return redirect("/html/login.html", code=302)

@app.route('/api/tickets/submit', methods=['POST'])
def submit_ticket():
    db = get_db()
    name = request.form['name'] + ' <' + request.form['email'] + '>'
    the_time = datetime.datetime.now()
    cur = db.execute(
        'insert into tickets (title, state, created_at, last_updated, created_by, tags, real_time_state, total_users_looking) VALUES (?, ?, ?, ?, ?, ?, "{}", 0)', 
        [request.form['title'], 'Open', the_time, the_time, name, ''])
    db.commit()
    ticket_id = cur.lastrowid
    cur = db.execute('insert into interactions (ticket_id, sender, receiver, date, content, type) VALUES (?, ?, ?, ?, ?, ?)', [ticket_id, name, 'System', the_time, request.form['content'], 'theirs'])
    db.commit()
    # TODO What a User Sees
    return '<h1 style="text-align: center">{}</h1>'.format('Thank you for contacting us. In future communications, please refer to the following reference number: #' + str(ticket_id))


@app.route('/api/logout', methods=['POST'])
def logout_agent():
    # Security: This does not prevent replay attacks
    session.clear()
    return jsonify({'result': 'ok'})


@socketio.on('connected')
def user_connected():
    send(json.dumps({'msg': 'Hello!'}))
    pass

TIMEOUT_SECONDS = 60

def update_in_realtime_data(ticket):
    # remove users that have timed out
    # and returns remaining users    
    print(ticket)
    data = json.loads(ticket['real_time_state'])
    curtime = datetime.datetime.now()    
    for user in list(data):
        if (curtime - dateutil.parser.parse(data[user])).total_seconds() >= TIMEOUT_SECONDS:
            del data[user]
    return data
        
def include_in_realtime_data(ticket, user):
    # add the user with the current timestamp to the object
    db = get_db()
    ticket = dict(db.execute('select * from tickets where id=?', [ticket]).fetchone())
    data = update_in_realtime_data(ticket)
    data[user] = datetime.datetime.now()
    print(data)
    db.execute('update tickets set real_time_state = ? where id=?', [json.dumps(data, default=json_serial), ticket['id']])
    db.commit()
    
def remove_in_realtime_data(ticket, user):
    # remove the user with the current timestamp to the object
    db = get_db()
    ticket = dict(db.execute('select * from tickets where id=?', [ticket]).fetchone())
    data = update_in_realtime_data(ticket)
    if user in data:
        del data[user]
    db.execute('update tickets set real_time_state = ? where id = ?', [json.dumps(data, default=json_serial), ticket['id']])
    db.commit()
    
@socketio.on('ticket-opened')
def ticket_opened(data):
    print(data)
    room = 'ticket:{}'.format(data['id'])
    send(json.dumps({'msg': 'Opened by: ' + data['user_name']}), room=room)
    include_in_realtime_data(data['id'], data['user_name'])
    join_room(room)

@socketio.on('ticket-closed')
def ticket_closed(data):
    room = 'ticket:{}'.format(data['id'])
    remove_in_realtime_data(data['id'], data['user_name'])
    leave_room(room)
    send(json.dumps({'msg': 'Closed by: ' + data['user_name']}), room=room)

@socketio.on('ticket-editing')
def ticket_editing(data):
    room = 'ticket:{}'.format(data['id'])
    include_in_realtime_data(data['id'], data['user_name'])
    send(json.dumps({'msg': 'Editing by: ' + data['user_name']}), room=room)

@socketio.on('ticket-changed')
def ticket_changed(data):
    room = 'ticket:{}'.format(data['id'])
    include_in_realtime_data(data['id'], data['user_name'])
    send(json.dumps({'msg': 'Changed by: ' + data['user_name']}), room=room)
