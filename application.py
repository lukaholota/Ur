from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from random import randrange
from Classes import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class PiecesTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pos = db.Column(db.Integer)
    player = db.Column(db.Integer)


@app.route('/')
def start():
    return get_converted_field(restore_field())


@app.route('/roll')
def roll():
    result = 0
    for _ in range(4):
        result += randrange(2)
    return result


@app.route('/place_new_peace', methods=['POST'])
def place_new_peace():
    piece = PiecesTable(id=request.json['id'], pos=request.json['pos'], player=request.json['player'])
    db.session.add(piece)
    db.session.commit()
    return "ok nie"


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
    field = GamingField()
    players = {0: field.player_1,
               1: field.player_2}
    pieces = PiecesTable.query.all()
    for piece in pieces:
        players[piece.player].place_new_piece(piece.pos)
    return field


# saves field to database
def save_field():
    PiecesTable.quary.delete()
    db.session.commit()
    field = restore_field()
    players = (field.player_1, field.player_2)
    for player in players:
        for piece in player.active_pieces:
            db.session.add(id=piece.id, player=piece.player, pos=piece.pos)
            db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
