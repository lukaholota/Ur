from random import randrange
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from Classes import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class PiecesTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    piece_id = db.Column(db.Integer)
    pos = db.Column(db.Integer)
    player = db.Column(db.Integer)


class GameState(db.Model):
    turn = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.Integer)
    win_0 = db.Column(db.Integer)
    win_1 = db.Column(db.Integer)


# restores field from database
def restore_field():
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    win_0, win_1 = state.win_0, state.win_1
    field = GamingField(roll=current_roll, turn=current_turn, win_0=win_0, win_1=win_1)
    pieces = PiecesTable.query.all()
    for piece in pieces:
        field.players[piece.player].restore_piece(piece.pos)
    return field


# saves field to database
def save_field(field):
    PiecesTable.query.delete()
    db.session.commit()
    players = (field.player_0, field.player_1)
    for player in players:
        for piece in player.active_pieces:
            piece_object = PiecesTable(piece_id=piece.id, player=piece.player, pos=piece.pos)
            db.session.add(piece_object)
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    win_0, win_1 = state.win_0, state.win_1
    turn = field.turn
    GameState.query.delete()
    state = GameState(turn=turn, roll=current_roll, win_0=win_0, win_1=win_1)
    db.session.add(state)
    db.session.commit()


def start_next_turn():
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    win_0, win_1 = state.win_0, state.win_1
    next_turn = (current_turn + 1) % 2
    next_roll = roll()
    GameState.query.delete()
    state = GameState(turn=next_turn, roll=next_roll, win_0=win_0, win_1=win_1)
    db.session.add(state)
    db.session.commit()


def check_turn_possibility(field):
    player = field.current_player
    pieces = player.active_pieces
    possible = []
    for piece in pieces:
        move = player.move_piece(piece)
        if move == 'win':
            move = True
        if move == 'too':
            move = False
        possible.append(move)
    place = player.place_new_piece(player.roll)
    possible.append(place)
    return any(possible)


def add_win_piece():
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    win_0, win_1 = state.win_0, state.win_1
    if current_turn == 0:
        win_0 += 1
    else:
        win_1 += 1
    GameState.query.delete()
    state = GameState(turn=current_turn, roll=current_roll, win_0=win_0, win_1=win_1)
    db.session.add(state)
    db.session.commit()


# returns field dictionary with piece objects as a value
def get_converted_field(field):
    result = {}
    for key, val in field.field.items():
        if isinstance(val, Piece):
            result[key] = {'id': val.id, 'pos': val.pos, 'player': val.player}
        elif isinstance(val, list):
            val_list = []
            for el in val:
                if isinstance(el, Piece):
                    val_list.append({'id': el.id, 'pos': el.pos, 'player': el.player})
                else:
                    val_list.append(el)
            result[key] = val_list
        else:
            result[key] = val
    return result


def convert_pieces_list_to_dict(player):
    converted = {}
    pieces = player.active_pieces
    for piece in pieces:
        converted[piece.id] = piece
    return converted


def roll():
    result = 0
    for _ in range(4):
        result += randrange(2)
    return result


@app.route('/game-state')
def return_game_state_dict():
    return get_converted_field(restore_field())


@app.route('/game-state/v2')
def return_game_state_dict_v2():
    state = GameState.query.all()[0]
    win_0, win_1 = state.win_0, state.win_1
    field = restore_field()
    return {'current_turn': str(field.turn),
            'finished_pieces_player_0': str(win_0),
            'finished_pieces_player_1': str(win_1),
            'field': get_converted_field(field)}


@app.route('/roll/v2', methods=['POST'])
def get_roll():
    state = GameState.query.all()[0]
    current_roll = state.roll
    if current_roll == 0:
        start_next_turn()
        return {'roll': str(current_roll), 'problem': "roll is zero! You skip the turn"}
    return {'roll': str(current_roll)}


@app.route('/roll', methods=['POST'])
def get_roll():
    state = GameState.query.all()[0]
    current_roll = state.roll
    if current_roll == 0:
        start_next_turn()
        return str(current_roll) + "roll is zero! You skip the turn"
    return str(current_roll)


@app.route('/place-new-piece', methods=['POST'])
def place_new_piece():
    field = restore_field()
    player = field.current_player
    pos = player.roll
    player_id = field.turn
    is_placed = player.place_new_piece(pos)
    if is_placed == 'too':
        return "You can't place anymore"
    elif is_placed:
        added_piece = player.active_pieces[-1]
        piece_id = added_piece.id
        piece = PiecesTable(piece_id=piece_id, pos=pos, player=player_id)
        db.session.add(piece)
        db.session.commit()
        save_field(field)
        start_next_turn()
        return 'placed, go to /game-state'
    else:
        return "not placed. The field you tried to put the piece onto is occupied. You can't place during this turn"


# roll and turn system
@app.route('/move-piece', methods=['PUT'])
def move_piece():
    field = restore_field()
    player = field.players[field.turn]
    player_id = request.json['player']
    if int(player_id) != field.turn:
        return 'wrong player'
    piece_id = request.json['piece_id']
    piece = convert_pieces_list_to_dict(player)[piece_id]
    turn = field.turn
    is_moved = player.move_piece(piece)
    if is_moved == 'win':
        add_win_piece()
        save_field(field)
        start_next_turn()
        state = GameState.query.all()[0]
        win = (state.win_0, state.win_1)[turn]
        return f'moved to win position. You still got {7 - win} pieces left to win'
    elif is_moved:
        save_field(field)
        start_next_turn()
        return 'moved. go to /game-state'
    else:
        return 'not moved. Try to move another one or place a new one'


@app.route('/start-game')
def start_game():
    start_roll = roll()
    null_state = GameState(roll=start_roll, turn=0, win_0=0, win_1=0)
    GameState.query.delete()
    db.session.add(null_state)
    PiecesTable.query.delete()
    db.session.commit()
    if start_roll == 0:
        start_next_turn()
    return 'game status annulled, go to /game-state'


@app.route('/win-pieces-amount')
def get_win_pieces_amount():
    state = GameState.query.all()[0]
    win_0, win_1 = state.win_0, state.win_1
    return {0: win_0, 1: win_1}


@app.route('/left-pieces')
def get_left_pieces():
    field = restore_field()
    player_0, player_1 = field.player_0, field.player_1
    pieces_amount_0, pieces_amount_1 = player_0.active_pieces, player_1.active_pieces
    state = GameState.query.all()[0]
    left_0 = 7 - state.win_0 - pieces_amount_0
    left_1 = 7 - state.win_1 - pieces_amount_1
    return {0: left_0, 1: left_1}


@app.route('/current-turn')
def get_current_turn():
    state = GameState.query.all()[0]
    return str(state.turn)


@app.route('/skip-turn')
def skip_turn():
    return 'sorry. With your roll you can do nothing during this turn.'


if __name__ == "__main__":
    app.run(debug=True)
