import json
from copy import deepcopy

class Renderer(object):
    def __init__(self, board):
        self.board = board

class TextRenderer(Renderer):
    __allow__ = (
        'PREFIX', 'SUFFIX',
        'ROW_PREFIX', 'ROW_SUFFIX',
        'CURRENT_BLOCK', 'FIXED_BLOCK', 'SPACE'
    )

    PREFIX = ''
    SUFFIX = ''
    ROW_PREFIX = ''
    ROW_SUFFIX = ''
    CURRENT_BLOCK = '@'
    FIXED_BLOCK = '#'
    SPACE = ' '

    def __init__(self, *args):
        super().__init__(*args)

    def render(self):
        """
        return list of str, each element is one row
        """

        lines = [self.PREFIX]
        y, x = self.board.current_block_pos

        for i, row in enumerate(self.board.get_board_copy()):
            line = self.ROW_PREFIX
            for j, block in enumerate(row):
                p = self.FIXED_BLOCK if block else self.SPACE
                if i - y in range(4) and j - x in range(4) \
                    and self.board.current_block[i - y, j - x] == 'O':
                    p = self.CURRENT_BLOCK
                line += p
            lines.append(line + self.ROW_SUFFIX)
        lines.append(self.SUFFIX)
        return lines

    def __str__(self):
        return '\n'.join(self.render())

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(
                '%s=%r' % (key, getattr(self, key, None))
                for key in self.__allow__
            )
        )

class FancyTextRenderer(TextRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        for key, val in kwargs.items():
            if key in self.__allow__:
                setattr(self, key, val)

class JSONRenderer(Renderer):
    def __init__(self, *args):
        super().__init__(*args)

    def render(self):
        board = self.board.get_board_copy()
        curr_block = self.board.current_block
        y, x = self.board.current_block_pos

        for row in range(4):
            for col in range(4):
                if curr_block[row, col] == 'O':
                    board[row + y][col + x] = 2

        data = {
            'board': board,
            'next_block': self.board.next_block.block
        }

        return data

    def __str__(self):
        return json.dumps(self.render())
