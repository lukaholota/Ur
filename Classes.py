class GamingField:
    def __init__(self, *, turn, roll, win_0, win_1):
        self.field = dict(zip(range(15), [None for _ in range(16)]))
        self.player_0 = Player(0, self, roll, win_0)
        self.player_1 = Player(1, self, roll, win_1)
        self.players = {0: self.player_0, 1: self.player_1}
        self.turn = turn
        self.current_player = self.players[self.turn]

        for i in range(5):
            self.field[i] = [None, None]
        for i in range(13, 15):
            self.field[i] = [None, None]

    def reserve_place(self, piece):
        if piece.pos > 14:
            piece_index = self.current_player.active_pieces.index(piece)
            del self.current_player.active_pieces[piece_index]
            self.minor_all_other_pieces()
            return 'win'

        elif piece.pos < 5 or piece.pos > 12 and piece.old_pos > 12:
            if self.is_reserve_valid(piece):
                self.field[piece.old_pos][piece.player] = None
                self.field[piece.pos][piece.player] = piece
                return True
            else:
                piece.pos = piece.old_pos
                return False

        elif piece.pos > 12 > piece.old_pos:
            if self.is_reserve_valid(piece):
                if piece.old_pos != 0:
                    self.field[piece.old_pos] = None
                self.field[piece.pos][piece.player] = piece
                return True
        else:
            if self.is_reserve_valid(piece):
                if piece.old_pos != 0:
                    self.field[piece.old_pos] = None
                self.field[piece.pos] = piece
                return True
            else:
                piece.pos = piece.old_pos
                return False

    def is_reserve_valid(self, piece):
        if piece.pos < 5 or piece.pos > 12:
            if self.field[piece.pos][piece.player] is None:
                return True
            return False
        else:
            if self.field[piece.pos] is None:
                return True
            return False

    def minor_all_other_pieces(self):
        player = self.current_player
        for piece in player.active_pieces:
            piece.id -= 1


class Player:
    def __init__(self, num, field, roll, win):
        self.active_pieces = []
        self.num = num
        self.field = field
        self.roll = roll
        self.win = win

    def place_new_piece(self, pos):
        pieces_amount = len(self.active_pieces)
        left = 7 - self.win - pieces_amount
        if left > 0:
            new_piece = Piece(self)
            self.active_pieces.append(new_piece)
            new_piece.old_pos = 0
            new_piece.pos = pos
            is_placed = self.field.reserve_place(new_piece)
            return is_placed
        return 'too'

    def move_piece(self, piece):
        piece.old_pos = piece.pos
        piece.pos += self.roll
        is_moved = self.field.reserve_place(piece)
        return is_moved


class Piece:
    def __init__(self, player):
        self.id = len(player.active_pieces) + 1
        self.pos = 0
        self.player = player.num
