from copy import deepcopy

from . import blocks

class State:
    AllGreen = 0
    OutOfBoard = 1
    ConflictWithBlock = 2

class BoolState(object):
    def __init__(self, bool_, status=None):
        self.status = status
        self.bool_ = bool(bool_)

    def __bool__(self):
        return self.bool_

    def __str__(self):
        return str(self.status)

    def __repr__(self):
        return 'BoolState(bool_=%r, status=%r)' % (self.bool_, self.status)

class GameBoard(object):
    def __init__(self, _width = 10, _height=20):
        """
        add first block and next block
        """

        self.height = _height
        self._height = _height + 4 # for inner use, add hidden row on it
        self.width = _width

        # (0, 0) is leftest and highest corner
        self._board = [[0 for y in range(self.width)] for x in range(self._height)]

        self.current_block_pos = (0, int(self.width/2))
        self.current_block = blocks.random_block()
        self.next_block = blocks.random_block()

        self.freeze = False

    # Game control related API

    def next_tick(self):
        """
        next game tick
        """
        x, y = self.current_block_pos
        next_block_pos = (x+1, y)
        next_state = self._conflict_detect(self.current_block, next_block_pos)

        if self.is_gameover():
            self.freeze = True
            return BoolState(False, 'gameover')

        if next_state is State.AllGreen:
            self.current_block_pos = next_block_pos
            return BoolState(False, 'step')

        elif next_state is State.ConflictWithBlock or next_state is State.OutOfBoard:
            self._make_deposit()
            return BoolState(True, 'deposit')


    def is_gameover(self):
        """
        return a bool indicate that is game over or not
        """
        for x in range(4):
            for y in range(self.width):
                if self._board[x][y] != 0:
                    return True

        return False

    def swap_block(self):
        """
        swap current block and next block
        """

        self.current_block, self.next_block = self.next_block, self.current_block

    # Game input API

    def move(self, direction):
        """
        direction: -1 for left, 1 for right
        """
        if self.freeze:
            return

        if direction not in ['right', 'left']:
            raise ValueError('direction should be right or left')

        x, y = self.current_block_pos
        if direction == 'left':
            next_block_pos = (x, y - 1)

        if direction == 'right':
            direction = 1
            next_block_pos = (x, y + 1)

        if self._conflict_detect(self.current_block, next_block_pos) is State.AllGreen:
            self.current_block_pos = next_block_pos

    def down(self):
        """
        move down 1 line immediately
        """
        self.next_tick()

    def deposit(self):
        """
        put down current block immediately
        """
        if self.freeze:
            return

        while not self.next_tick():
            pass

    def rotate(self, direction):
        """
        Rotate the block, left for anticlockwise, right for clockwise
        """
        if self.freeze:
            return

        if direction not in ['right', 'left']:
            raise ValueError('direction should be right or left')

        block = self.current_block
        self.current_block = self.current_block.rotate(direction)

        if self._conflict_detect() is not State.AllGreen:
            self.current_block = block

    def __getitem__(self, pos):
        """
        raw board accessor

        p = block[0, 0]
        """
        x, y = pos
        return self._board[x][y]

    def get_board_copy(self):
        return deepcopy(self._board)

    def clear(self):
        self._board = [[0 for y in range(self.width)] for x in range(self._height)]

    def __str__(self):
        out = ''
        y, x = self.current_block_pos
        for i, row in enumerate(self._board):
            line = ''
            for j, block in enumerate(row):
                B = '#'
                p = B if block else ' '
                if i - y in range(4) and j - x in range(4) and self.current_block[i - y, j - x] == 'O':
                    p = '@'
                line += p
            out += line + '\n'
        return out

    # Private functionis
    def _conflict_detect(self, block=None, pos=None):
        if block is None:
            block = self.current_block
        if pos is None:
            pos = self.current_block_pos

        for row in range(4):
            for column in range(4):
                if block[row, column] == 'O':
                    offset = (row + pos[0], column + pos[1])
                    if not offset[0] < self._height:
                        return State.OutOfBoard

                    if not self.width > offset[1] >= 0:
                        return State.OutOfBoard

                    if self._board[offset[0]][offset[1]] > 0:
                        return State.ConflictWithBlock

        return State.AllGreen

    def _make_deposit(self, block=None, pos=None):
        """
        Make current block deposit
        """
        if block is None:
            block = self.current_block
        if pos is None:
            pos = self.current_block_pos

        for row in range(4):
            for column in range(4):
                offset = (row + pos[0], column + pos[1])
                if block[row, column] == 'O':
                    self._board[offset[0]][offset[1]] = 1

        self.current_block = self.next_block
        self.current_block_pos = (0, int(self.width/2))
        self.next_block = blocks.random_block()

        # clean the line
        remap = []
        for line in self._board:
            if not all(line):
                remap.append(line)

        for idx, line in enumerate(reversed(remap)):
            self._board[-idx-1] = deepcopy(line)

        self.remap = remap
