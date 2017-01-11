Vue.use(VueSocketio.default, 'http://' + document.domain + ':' + location.port + '/game')

var THEMES = {
	minecraft: {
		size: '16px',
		blocks: {
			DEFAULT: 'url("assets/textures/minecraft/bedrock.png")',
			1: 'url("assets/textures/minecraft/grass_side.png")',
			2: 'url("assets/textures/minecraft/diamond_ore.png")',
		}
	},
	plain: {
		size: '16px',
		blocks: {
			DEFAULT: '#ddd',
			1: '#3fe',
			2: '#69f'
		}
	}
}

var DEFAULT_DATA = function (msg) {
	return {
		messages: msg || [],
		uid: '',
		join_room_id: '',
		room_id: '',
		joined_room: false,
		username: '',
		username_set: false,
		board_state: '',
		is_owner: false,
		gameover: false,
		themes: THEMES,
		curr_theme: 'plain'
	}
}

Vue.component('block', {
	template: '#block-t',
	props: ['block', 'theme'],
	computed: {
		background: function () {
			return this.theme.blocks[this.block] || this.theme.blocks.DEFAULT || ''
		}
	}
})

Vue.component('row', {
	template: '#row-t',
	props: ['row', 'theme']
})

Vue.component('board', {
	template: '#board-t',
	props: ['board', 'theme']
})

new Vue({
	el: '#app',
	template: '#app-t',

	created: function () {
		this.$keyboard_event = this.keydown.bind(this)
		window.addEventListener('keydown', this.$keyboard_event)

		var room_id = location.hash.substr(1)
		if(room_id.length > 0) {
			this.join_room(room_id)
		}
	},
	destroyed: function () {
		window.removeEventListener('keydown', this.$keyboard_event)
	},

	sockets: {
		connect: function () { this.msg('Connected'); this.reset() },
		disconnect: function () { this.msg('Disconnected') },
		'user id': function (id) { this.uid = id },

		message: function (msg) {
			this.msg(msg)
		},

		'room id': function (id) {
			if(this.joined_room) return;
			this.joined_room = true
			this.room_id = id
			this.msg('Join game room: ' + id)
		},

		'board state': function (state) {
			this.board_state = state
		},

		'game over': function () {
			this.gameover = true
		}
	},

	methods: {
		reset: function () {
			Object.assign(this.$data, DEFAULT_DATA(this.messages))
		},

		msg: function (m) {
			this.messages.unshift(m)
		},

		create_room: function () {
			this.$socket.emit('create room')
			this.is_owner = true
		},

		join_room: function (id) {
			if(!id) {
				this.msg('Can not join room (Invalid ID)')
				return
			}
			this.$socket.emit('join room', id)
		},

		set_username: function (name) {
			this.username_set = true
			this.$socket.emit('set name', name)
		},

		start_game: function () {
			this.$socket.emit('start game')
		},

		keydown: function (e) {
			if(this.gameover)
				return

			var op = null

			switch(e.code) {
				case 'Space':
					op = 'BOOM'
					break
				case 'ArrowLeft':
				case 'KeyH':
					op = 'MOVE_LEFT'
					break
				case 'ArrowRight':
				case 'KeyL':
					op = 'MOVE_RIGHT'
					break
				case 'ArrowUp':
				case 'KeyK':
					op = 'ROTATE_LEFT'
					break
				case 'ArrowDown':
					op = 'DOWN'
					break
				case 'KeyJ':
					op = 'ROTATE_RIGHT'
					break
			}

			if(op) {
				console.log('Fire: ' + op)
				this.$socket.emit('game input', op)
			}
		}
	},

	data: DEFAULT_DATA,

	computed: {
		game_url: function () {
			return location.href.replace(/#.*$/, '') + '#' + this.room_id
		}
	}
})
