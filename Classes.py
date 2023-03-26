class GamingField:
    def __init__(self):
        self.field = dict(zip(range(15), [None for _ in range(15)]))
        self.player_1 = Player(0, self)
        self.player_2 = Player(1, self)
        for i in range(5):
            self.field[i] = [None, None]
        for i in range(13, 15):
            self.field[i] = [None, None]

    def reserve_place(self, piece):
        if piece.pos < 5 or piece.pos > 12:
            if self.field[piece.pos][piece.player] is None:
                self.field[piece.old_pos][piece.player] = None
                self.field[piece.pos][piece.player] = piece
        else:
            if self.field[piece.pos] is None:
                self.field[piece.old_pos] = None
                self.field[piece.pos] = piece

    def is_move_valid(self):
        pass


class Player:
    def __init__(self, num, field):
        self.active_pieces = []
        self.num = num
        self.field = field

    def place_new_piece(self, pos):
        new_piece = Piece(self)
        self.active_pieces.append(new_piece)
        new_piece.old_pos = new_piece.pos
        new_piece.pos = pos
        self.field.reserve_place(new_piece)

    def move_piece(self, piece, roll):
        piece.old_pos = piece.pos
        piece.pos += roll
        self.field.reserve_place(piece)


class Piece:
    def __init__(self, player):
        self.id = len(player.active_pieces) + 1
        self.pos = 0
        self.player = player.num

    def __repr__(self):
        return self.id
