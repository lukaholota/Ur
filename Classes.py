from random import randrange

from exceptions import *
# from application import roll


class GamingField:
    def __init__(self, *, turn, roll):
        self.field = dict(zip(range(15), [None for _ in range(15)]))
        self.player_1 = Player(0, self, roll)
        self.player_2 = Player(1, self, roll)
        self.players = {0: self.player_1, 1: self.player_2}
        self.turn = turn
        self.current_player = self.players[self.turn]

        for i in range(5):
            self.field[i] = [None, None]
        for i in range(13, 15):
            self.field[i] = [None, None]

    def reserve_place(self, piece):
        if piece.pos < 5 or piece.pos > 12:
            try:
                if self.is_reserve_valid(piece):
                    self.field[piece.old_pos][piece.player] = None
                    self.field[piece.pos][piece.player] = piece
                    self.change_turn()
                else:
                    piece.pos = piece.old_pos
                    raise InvalidMove
            except InvalidMove:
                return {'error': 'Sorry, your move is invalid'}
        else:
            try:
                if self.is_reserve_valid(piece):
                    self.field[piece.old_pos] = None
                    self.field[piece.pos] = piece
                    self.change_turn()
                else:
                    piece.pos = piece.old_pos
                    raise InvalidMove
            except InvalidMove:
                return {'error': 'Sorry, your move is invalid'}

    def is_reserve_valid(self, piece):
        if self.field[piece.pos][piece.player] is None:
            return True
        return False

    def change_turn(self):
        self.turn = (self.turn + 1) % 2
        player = self.current_player


class Player:
    def __init__(self, num, field, roll):
        self.active_pieces = []
        self.num = num
        self.field = field
        self.roll = None

    def place_new_piece(self, pos):
        new_piece = Piece(self)
        self.active_pieces.append(new_piece)
        new_piece.old_pos = new_piece.pos
        new_piece.pos = pos
        self.field.reserve_place(new_piece)

    def move_piece(self, piece):
        piece.old_pos = piece.pos
        piece.pos += self.roll
        self.field.reserve_place(piece)


class Piece:
    def __init__(self, player):
        self.id = len(player.active_pieces) + 1
        self.pos = 0
        self.player = player.num

    def __repr__(self):
        return self.id
