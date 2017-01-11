import time
import logging
import functools

from ..game import GameBoard
from ..game.board_renderer import TextRenderer, JSONRenderer
from eventlet.semaphore import Semaphore

logger = logging.getLogger(__name__)

class User(object):
    def __init__(self, sio, sid, name=None, game=None, board=None):
        self.sio = sio
        self.sid = sid
        self.name = name or ('User_%s' % sid[:12])
        self.game = None
        self.board = GameBoard()
        self.renderer = JSONRenderer(self.board)
        self.board_lock = Semaphore(1)
        self.op_map = {
            'BOOM': self.board.deposit,
            'MOVE_LEFT': functools.partial(self.board.move, 'left'),
            'MOVE_RIGHT': functools.partial(self.board.move, 'right'),
            'ROTATE_RIGHT': functools.partial(self.board.rotate, 'right'),
            'ROTATE_LEFT': functools.partial(self.board.rotate, 'left'),
            'DOWN': self.board.down
        }

    def emit(self, event, data, *args, **kwargs):
        event = kwargs.pop('event', event)
        data = kwargs.pop('data', data)
        self.sio.emit(event, data, *args, room=self.sid, namespace='/game', **kwargs)

    def send(self, op):
        act = self.op_map.get(op, None)
        if not act:
            return

        with self.board_lock:
            act()
            self.report_state()

    def report_state(self):
        state = self.renderer.render()
        self.emit('board state', state)
        return state

    def __repr__(self):
        return 'User(sid=%r, game=%r, name=%r, board=%r)' % (
            self.sid, self.game, self.name, self.board
        )
