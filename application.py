from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from random import randrange
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


# restores field from database
def restore_field():
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    field = GamingField(roll=current_roll, turn=current_turn)
    pieces = PiecesTable.query.all()
    for piece in pieces:
        field.players[piece.player].place_new_piece(piece.pos)
    return field


def start_next_turn():
    state = GameState.query.all()[0]
    current_roll, current_turn = state.roll, state.turn
    next_turn = (current_turn + 1) % 2
    next_roll = roll()
    GameState.query.delete()
    state = GameState(turn=next_turn, roll=next_roll)
    db.session.add(state)
    db.session.commit()


# saves field to database
def save_field():
    field = restore_field()
    PiecesTable.query.delete()
    db.session.commit()
    players = (field.player_1, field.player_2)
    for player in players:
        for piece in player.active_pieces:
            piece_object = PiecesTable(piece_id=piece.id, player=piece.player, pos=piece.pos)
            db.session.add(piece_object)
    db.session.commit()


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


@app.route('/roll', methods=['POST'])
def get_roll():
    result = GameState.query.all()[0]
    return result


@app.route('/place-new-piece', methods=['POST'])
def place_new_piece():
    field = restore_field()
    player = field.current_player
    pos = player.roll
    player.place_new_piece(pos)
    added_piece = player.active_pieces[-1]
    piece_id = added_piece.id
    player_id = field.turn
    piece = PiecesTable(piece_id=piece_id, pos=pos, player=player_id)
    db.session.add(piece)
    db.session.commit()
    start_next_turn()
    save_field()
    return 'placed, go to /game-state'


# roll and turn system
@app.route('/move-piece', methods=['PUT'])
def move_piece():
    field = restore_field()
    player = field.current_player
    piece_id = request.json['piece_id']
    piece = convert_pieces_list_to_dict(player)[piece_id]
    player.move_piece(piece)
    start_next_turn()
    save_field()
    return 'moved. go to /game-state'


@app.route('/start-game')
def start_game():
    start_roll = roll()
    null_state = GameState(roll=start_roll, turn=0)
    GameState.query.delete()
    db.session.add(null_state)
    PiecesTable.query.delete()
    db.session.commit()
    return 'game status annulled, go to /game-state'


if __name__ == "__main__":
    app.run(debug=True)


