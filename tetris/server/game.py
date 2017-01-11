import os
import logging
from greenlet import GreenletExit
from eventlet import greenthread

logger = logging.getLogger(__name__)

class Game(object):
    def __init__(self, sio, owner, speed=0.75, players={}, room_id=None):
        self.sio = sio
        self.owner = owner
        self.players = players or {} # dict({user_id: User})
        self.room_id = room_id or os.urandom(16).hex()
        self.worker = None # GreenThread
        self.speed = speed # second(s)
        self.started = False

    def emit(self, event, data, *args, **kwargs):
        event = kwargs.pop('event', event)
        data = kwargs.pop('data', data)
        self.sio.emit(event, data, *args, room=self.room_id, namespace='/game', **kwargs)

    def work(self): # background worker
        for sid, user in self.players.items():
            with user.board_lock:
                user.board.next_tick()
                user.report_state()
            if user.board.is_gameover():
                self.broadcast('User %s dead, gameover!' % user.name)
                self.emit('game over', None)
                return False

        return True

    def worker_loop(self):
        try:
            while self.work():
                greenthread.sleep(self.speed)
        except GreenletExit:
            pass
        finally:
            logger.debug('[*] R:%s - Worker exited' % self.room_id)

    def start(self): # start game
        if self.started:
            return
        self.started = True
        self.worker = greenthread.spawn(self.worker_loop)
        self.broadcast('Game Start!')

    def broadcast(self, message):
        logger.debug('[+] R:%s - Broadcast message: %r' % (self.room_id, message))
        self.sio.send(message, room=self.room_id, namespace='/game')

    def shutdown(self):
        self.broadcast('Goodbye')
        logger.info('[*] R:%s - Room shutting down' % self.room_id)
        for sid in list(self.players):
            self.sio.disconnect(sid, namespace='/game')
            try:
                del self.players[sid]
                logger.warn('[-] R:%s - KeyError (%r) while remove user from room' % (self.room_id, sid))
            except KeyError:
                pass

    def remove_user(self, sid):
        user = self.players.get(sid, None)
        if not user:
            return

        del self.players[sid]
        self.broadcast('User "%s" leaved' % user.name)

        if user is self.owner:
            self.broadcast('Game owner leaved, this game is shutting down.')
            self.shutdown()
            if self.worker:
                self.worker.kill()
                self.worker = None

    def add_user(self, user):
        if user.game:
            return
        user.game = self
        self.players[user.sid] = user
        self.broadcast('User "%s" entered' % user.name)

    def __repr__(self):
        return 'Game(sio=%r, players=%r, room_id=%r)' % (
            self.sio, self.players, self.room_id
        )
