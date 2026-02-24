"""
Problema 8: Servidor de Juegos Tic-Tac-Toe
- Estado compartido del juego
- Matchmaking de jugadores
- Validación de movimientos
- Sistema de espectadores
"""

import socket
import threading
import time

class Game:
    def __init__(self, id, player1, player2, name1, name2):
        self.id = id
        self.players = [player1, player2]  # [socket_X, socket_O]
        self.names = [name1, name2]        # [nombre_X, nombre_O]
        self.board = [' '] * 9
        self.turn = 0  # 0 = X, 1 = O
        self.winner = None
        self.spectators = []                # Lista de sockets espectadores
        self.game_over = False
    
    def make_move(self, player_sock, pos):
        # Validar turno
        if player_sock != self.players[self.turn]:
            return False, "No es tu turno"
        
        # Validar posición
        if pos < 0 or pos > 8 or self.board[pos] != ' ':
            return False, "Movimiento inválido"
        
        # Hacer movimiento
        self.board[pos] = 'X' if self.turn == 0 else 'O'
        
        # Verificar victoria
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a,b,c in lines:
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.game_over = True
        
        # Verificar empate
        if ' ' not in self.board:
            self.game_over = True
        
        # Cambiar turno
        self.turn = 1 - self.turn
        return True, "Movimiento aceptado"
    
    def board_str(self):
        b = self.board
        return f"""
 {b[0]} | {b[1]} | {b[2]}
---+---+---
 {b[3]} | {b[4]} | {b[5]}
---+---+---
 {b[6]} | {b[7]} | {b[8]}"""
    
    def get_state_message(self):
        """Genera el mensaje completo del estado actual"""
        msg = self.board_str()
        if self.winner:
            msg += f"\n Gana {self.winner}!"
        elif self.game_over:
            msg += "\n Empate!"
        else:
            turno = 'X' if self.turn == 0 else 'O'
            nombre_turno = self.names[self.turn]
            msg += f"\n Turno de {nombre_turno} ({turno})"
        return msg

class GameServer:
    def __init__(self):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('localhost', 9999))
        self.server.listen(10)
        
        self.waiting = []           # (socket, nombre) esperando partida
        self.games = {}              # id -> Game
        self.client_game = {}        # socket -> game_id
        self.client_name = {}        # socket -> nombre
        self.next_id = 1
        self.lock = threading.Lock()
        
    def broadcast_to_game(self, game, msg, exclude=None):
        """Envía mensaje a todos en la partida (jugadores + espectadores)"""
        print(f"   Broadcast a {len(game.players)} jugadores y {len(game.spectators)} espectadores")
        destinatarios = game.players + game.spectators
        for sock in destinatarios:
            if sock != exclude:
                try:
                    sock.send(f"{msg}\n".encode())
                    print(f"    Mensaje enviado a {self.client_name.get(sock, 'desconocido')}")
                except Exception as e:
                    print(f"    Error enviando a {self.client_name.get(sock, 'desconocido')}: {e}")
    
    def handle_player(self, sock, addr):
        """Maneja un jugador o espectador"""
        nombre = None
        try:
            # Recibir tipo (player/spectator) y nombre
            sock.send("¿Eres jugador (J) o espectador (E)? ".encode())
            tipo = sock.recv(1024).decode().strip().upper()
            
            sock.send("¿Cuál es tu nombre? ".encode())
            nombre = sock.recv(1024).decode().strip()
            
            with self.lock:
                self.client_name[sock] = nombre
            
            print(f"\n Conexión: {nombre} como {tipo}")
            
            if tipo == 'J':
                with self.lock:
                    self.waiting.append((sock, nombre))
                sock.send(f" {nombre}, esperando oponente...\n".encode())
                print(f" Jugador {nombre} en espera ({len(self.waiting)} jugadores)")
                
            elif tipo == 'E':
                # Listar partidas disponibles
                with self.lock:
                    games_list = []
                    for gid, game in self.games.items():
                        if not game.game_over:
                            games_list.append(f"  {gid}: {game.names[0]} vs {game.names[1]}")
                
                if not games_list:
                    sock.send(" No hay partidas activas\n".encode())
                    sock.close()
                    return
                
                sock.send(" Partidas disponibles:\n".encode())
                for g in games_list:
                    sock.send(f"{g}\n".encode())
                sock.send("ID de partida: ".encode())
                
                try:
                    data = sock.recv(1024).decode().strip()
                    game_id = int(data)
                    with self.lock:
                        if game_id in self.games:
                            game = self.games[game_id]
                            game.spectators.append(sock)
                            self.client_game[sock] = game_id
                            sock.send(f" {nombre}, ahora observas partida {game_id}\n".encode())
                            
                            # Enviar estado actual inmediatamente
                            estado = game.get_state_message()
                            sock.send(f"{estado}\n".encode())
                            
                            # Notificar a todos
                            self.broadcast_to_game(game, f"👀 {nombre} está observando", exclude=sock)
                            print(f" Espectador {nombre} en partida {game_id}")
                        else:
                            sock.send(" Partida no encontrada\n".encode())
                            sock.close()
                            return
                except Exception as e:
                    print(f"Error espectador: {e}")
                    sock.close()
                    return
            else:
                sock.send(" Opción inválida\n".encode())
                sock.close()
                return
            
            # Loop principal de mensajes
            while True:
                data = sock.recv(1024).decode().strip()
                if not data:
                    break
                
                print(f" {nombre}: {data}")
                
                # Procesar movimiento (solo jugadores)
                if tipo == 'J' and sock in self.client_game:
                    game_id = self.client_game[sock]
                    game = self.games[game_id]
                    
                    try:
                        pos = int(data) - 1
                        success, msg = game.make_move(sock, pos)
                        
                        if success:
                            # Enviar nuevo estado a todos
                            estado = game.get_state_message()
                            self.broadcast_to_game(game, estado)
                            
                            if game.game_over:
                                self.broadcast_to_game(game, "🎮 Juego terminado")
                                # Limpiar después de 5 segundos
                                threading.Timer(5, self.cleanup_game, args=[game_id]).start()
                                break
                        else:
                            sock.send(f" {msg}\n".encode())
                    except ValueError:
                        sock.send(" Usa número 1-9\n".encode())
                
        except Exception as e:
            print(f"Error con {nombre}: {e}")
        finally:
            self.remove_client(sock)
    
    def cleanup_game(self, game_id):
        """Limpia una partida terminada"""
        with self.lock:
            if game_id in self.games:
                print(f" Limpiando partida {game_id}")
                del self.games[game_id]
    
    def remove_client(self, sock):
        """Elimina cliente desconectado"""
        with self.lock:
            nombre = self.client_name.get(sock, "Desconocido")
            print(f" Cliente {nombre} desconectado")
            
            if sock in self.waiting:
                self.waiting.remove(sock)
            
            if sock in self.client_game:
                game_id = self.client_game[sock]
                if game_id in self.games:
                    game = self.games[game_id]
                    if sock in game.players:
                        # Jugador se desconectó
                        self.broadcast_to_game(game, f" {nombre} se desconectó")
                        game.game_over = True
                    elif sock in game.spectators:
                        game.spectators.remove(sock)
                        self.broadcast_to_game(game, f" {nombre} dejó de observar")
                del self.client_game[sock]
            
            if sock in self.client_name:
                del self.client_name[sock]
        
        try: sock.close()
        except: pass
    
    def matchmaking_loop(self):
        """Loop de matchmaking - empareja jugadores"""
        while True:
            time.sleep(1)
            with self.lock:
                while len(self.waiting) >= 2:
                    p1_sock, p1_name = self.waiting.pop(0)
                    p2_sock, p2_name = self.waiting.pop(0)
                    
                    game_id = self.next_id
                    self.next_id += 1
                    
                    game = Game(game_id, p1_sock, p2_sock, p1_name, p2_name)
                    self.games[game_id] = game
                    self.client_game[p1_sock] = game_id
                    self.client_game[p2_sock] = game_id
                    
                    # Notificar a jugadores
                    p1_sock.send(" Partida encontrada! Eres X\n".encode())
                    p2_sock.send(" Partida encontrada! Eres O\n".encode())
                    
                    # Enviar estado inicial
                    estado_inicial = game.get_state_message()
                    p1_sock.send(f"{estado_inicial}\n".encode())
                    p2_sock.send(f"{estado_inicial}\n".encode())
                    
                    print(f" Partida {game_id}: {p1_name} (X) vs {p2_name} (O)")
    
    def start(self):
        """Inicia el servidor"""
        # Hilo de matchmaking
        threading.Thread(target=self.matchmaking_loop, daemon=True).start()
        
        print("="*30)
        print(" SERVIDOR TIC-TAC-TOE")
        print("="*30)
        print("Esperando Jugadores/Espectadores...")
        
        while True:
            sock, addr = self.server.accept()
            threading.Thread(target=self.handle_player, args=(sock, addr), daemon=True).start()

if __name__ == "__main__":
    GameServer().start()