from random import randrange, choice
from string import ascii_letters, digits, punctuation

from flask import request, make_response
from database import app, db
from Classes import *


class Games(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_tables = db.relationship('PiecesTable', backref='game', lazy=True,
                                   primaryjoin="Games.id==PiecesTable.game_id")
    states = db.relationship('GameState', backref='game', lazy=True,
                             primaryjoin="Games.id==GameState.game_id")


class PiecesTable(db.Model):
    __tablename__ = 'pieces_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_id = db.Column(db.Integer)
    pos = db.Column(db.Integer)
    player = db.Column(db.Integer)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)


class GameState(db.Model):
    __tablename__ = 'game_state'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    turn = db.Column(db.Integer)
    roll = db.Column(db.Integer)
    win_0 = db.Column(db.Integer)
    win_1 = db.Column(db.Integer)
    player_id_0 = db.Column(db.String)
    player_id_1 = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)


# restores field from database
def restore_field(game_id):
    state = GameState.query.filter_by(game_id=game_id).first()
    current_roll, current_turn = state.roll, state.turn
    win_0, win_1 = state.win_0, state.win_1
    field = GamingField(roll=current_roll, turn=current_turn, win_0=win_0, win_1=win_1)
    pieces = PiecesTable.query.filter_by(game_id=game_id)
    for piece in pieces:
        field.players[piece.player].restore_piece(piece.pos)
    return field


# saves field to database
def save_field(field, game_id):
    PiecesTable.query.filter_by(game_id=game_id).delete()
    db.session.commit()
    players = (field.player_0, field.player_1)
    for player in players:
        for piece in player.active_pieces:
            piece_object = PiecesTable(piece_id=piece.id, player=piece.player, pos=piece.pos, game_id=game_id)
            db.session.add(piece_object)
    state = GameState.query.filter_by(game_id=game_id).first()
    state.turn = field.turn
    db.session.commit()


def start_next_turn(game_id):
    state = GameState.query.filter_by(game_id=game_id).first()
    current_roll, current_turn = state.roll, state.turn
    next_turn = (current_turn + 1) % 2
    next_roll = None
    state.roll = next_roll
    state.turn = next_turn
    db.session.commit()


def add_win_piece():
    state = GameState.query.all()[0]
    if state.turn == 0:
        state.win_0 += 1
    else:
        state.win_1 += 1
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


def check_player_valid(turn, req, game_id):
    state = GameState.query.filter_by(game_id=game_id).first()
    cookie_id = req.cookies.get('id')
    db_ids = {0: state.player_id_0, 1: state.player_id_1}
    if db_ids[turn] == cookie_id and cookie_id is not None:
        return True
    elif cookie_id not in db_ids.values() or not cookie_id:
        if db_ids[turn] is None:
            new_id = generate_password()
            if turn == 0:
                state.player_id_0 = new_id
            else:
                state.player_id_1 = new_id
            db.session.commit()
            response = make_response('Player identifier set in cookie.')
            response.set_cookie('id', new_id)
            return response
    return False


def generate_password(length=15):
    chars = ascii_letters + digits + punctuation
    password = ''.join(choice(chars) for _ in range(length))
    return password


def roll(game_id):
    result = 0
    for _ in range(4):
        result += randrange(2)
    state = GameState.query.filter_by(game_id=game_id).first()
    state.roll = result
    db.session.commit()
    return result


@app.route('/game-state/<game_id>')
def return_game_state_dict_v2(game_id):
    state = GameState.query.all()[0]
    win_0, win_1 = state.win_0, state.win_1
    field = restore_field(game_id)
    return {'current_turn': str(field.turn),
            'finished_pieces_player_0': str(win_0),
            'finished_pieces_player_1': str(win_1),
            'field': get_converted_field(field)}


@app.route('/roll/<game_id>', methods=['POST'])
def get_roll_v2(game_id):
    old_roll = GameState.query.filter_by(game_id=game_id).first().roll
    if old_roll is None:
        current_roll = roll(game_id)
        if current_roll == 0:
            start_next_turn(game_id)
            return {'roll': str(current_roll), 'problem': "roll is zero! You skip the turn"}
        return {'roll': str(current_roll)}
    else:
        return {'roll': str(old_roll), 'problem': "you've already rolled this turn"}


@app.route('/place-new-piece/<game_id>', methods=['POST'])
def place_new_piece(game_id):
    field = restore_field(game_id)
    current_roll = GameState.query.filter_by(game_id=game_id).first().roll
    if current_roll is None:
        return "roll first, then move"
    res = check_player_valid(field.turn, request, game_id)
    response = make_response()
    if isinstance(res, bool):
        if not res:
            return "dont cheat"
    else:
        response = res
    player = field.current_player
    pos = player.roll
    player_id = field.turn
    is_placed = player.place_new_piece(pos)
    if is_placed == 'too':
        response.data = "You can't place anymore"
        return response
    elif is_placed:
        added_piece = player.active_pieces[-1]
        piece_id = added_piece.id
        piece = PiecesTable(piece_id=piece_id, pos=pos, player=player_id, game_id=game_id)
        db.session.add(piece)
        db.session.commit()
        save_field(field, game_id)
        start_next_turn(game_id)
        response.data = 'placed, go to /game-state'
        return response
    else:
        response.data = "not placed. The field you tried to put " \
                        "the piece onto is occupied. You can't place during this turn"
        return response


# roll and turn system
@app.route('/move-piece/<game_id>', methods=['PUT'])
def move_piece(game_id):
    field = restore_field(game_id)
    current_roll = GameState.query.filter_by(game_id=game_id).first().roll
    if current_roll is None:
        return "roll first, then move"
    res = check_player_valid(field.turn, request, game_id)
    response = make_response()
    if isinstance(res, bool):
        if not res:
            return "dont cheat"
    else:
        response = res
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
        save_field(field, game_id)
        start_next_turn(game_id)
        state = GameState.query.all()[0]
        win = (state.win_0, state.win_1)[turn]
        response.data = f'moved to win position. You still got {7 - win} pieces left to win'
        return response
    elif is_moved:
        save_field(field, game_id)
        start_next_turn(game_id)
        response.data = 'moved. go to /game-state'
        return response
    else:
        response.data = 'not moved. Try to move another one or place a new one'
        return response


# to do: add deleting useless data
@app.route('/start-game')
def start_game():
    # old_game = GameState.query.filter_by(game_id=)
    new_game = Games()
    db.session.add(new_game)
    db.session.flush()
    null_state = GameState(roll=None, turn=0, win_0=0, win_1=0,
                           player_id_0=None, player_id_1=None, game_id=new_game.id)
    # GameState.query.filter_by(game_id=.delete()
    db.session.add(null_state)
    # PiecesTable.query.filter_by(game_id=game_id).delete()
    db.session.commit()
    return {'game_id': new_game.id}


if __name__ == "__main__":
    app.run(debug=True)
