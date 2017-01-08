import os
import logging

logger = logging.getLogger(__name__)

class Game(object):
    def __init__(self, sio, owner, players={}, room_id=None):
        self.sio = sio
        self.owner = owner
        self.players = players or {} # dict({user_id: User})
        self.room_id = room_id or os.urandom(16).hex()

    def broadcast(self, message):
        logger.info('[+] Broadcast message: %r' % message)
        self.sio.send(message, room=self.room_id, namespace='/game')

    def shutdown(self):
        self.broadcast('Goodbye')
        for sid in list(self.players):
            self.sio.disconnect(sid, namespace='/game')
            try:
                del self.players[sid]
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
