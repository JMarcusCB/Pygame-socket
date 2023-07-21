import pygame
import socket
import threading
import sys
import selectors
import json

from data6 import Data_manager

from player import Player
from button import Button, BUTTON_WIDTH, BUTTON_HEIGHT

class GameServer:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.resolution = (600, 600)
        self.display_surface = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Block mp - HOST")
        self.display_rect = pygame.Rect(0, 0, self.resolution[0], self.resolution[1])

        self.server_ip, self.server_port = "192.168.1.105", 9999

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen()

        self.selector = selectors.DefaultSelector()

        self.data = Data_manager()
        self.client_sockets = []
        self.id = "0"

        self.lock = threading.Lock()

        self.running = False

    def main_loop(self):
        self.menu()

    def game(self):
        self.create_thread(self.wait_connections)
        self.selector.register(self.server_socket, selectors.EVENT_READ, self.wait_connections)

        self.running = True

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update_game()
            self.send_data_to_clients()
            self.draw_game()

        self.disconnect_clients()
        self.close_server()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.print_debug_info()

    def quit_game(self):
        self.running = False
        self.disconnect_clients()
        pygame.quit()
        sys.exit()
        
    def print_debug_info(self):
        print(self.client_sockets)
        print(self.data.get_ids())
        print(self.data.get_players_list())
        print(self.data.get_players_datas())
        print(self.data.get_players_connected())
        print("-----------------------------------")

    def update_game(self):
        self.data.verify_sockets_conn(self.client_sockets)
        self.update_position()
        self.sync_players()

        for player in self.data.get_players_list():
            if player.id == self.id:
                player.update()
                player.rect.clamp_ip(self.display_rect)

    def send_data_to_clients(self):
        for sock in self.client_sockets:
            data = self.prepare_game_data()
            self.send_data(sock, data)

    def send_data(self, sock, data):
        try:
            sock.sendall(data)
        except socket.error as e:
            print("Erro ao enviar dados para o cliente:", str(e))
            self.disconnect_client(sock)

    def prepare_game_data(self):
        game_data = {
            "players_datas": self.data.get_players_datas(),
            "ids": self.data.get_ids(),
            "players_connected": self.data.get_players_connected()
        }
        return json.dumps(game_data).encode()

    def draw_game(self):
        try:
            self.display_surface.fill((0, 0, 0))
            for player in self.data.get_players_list():
                player.draw()
            pygame.display.flip()
        except pygame.error as e:
            print(e)
            print("DRAW_GAME")

    def update_player_data(self, id, x, y):
        if id in self.data.get_players_datas():
            self.data.modify_players_data_pos(id, "x", x)
            self.data.modify_players_data_pos(id, "y", y)
        for player in self.data.get_players_list():
            if id == player.id:
                player.set_position(int(x), int(y))

    def update_position(self):
        players_datas = self.data.get_players_datas().copy()
        for key in players_datas:
            for player in self.data.get_players_list():
                if key == player.id:
                    self.data.modify_players_data_pos(key, "x", player.rect.x)
                    self.data.modify_players_data_pos(key, "y", player.rect.y)

    def create_player(self):
        self.data.add_players_connected()
        self.data.add_ids("0")
        p = Player(100, 100, (50, 50), "0")
        self.data.add_players_list(p)
        self.data.add_players_data("0", p.get_position())
        self.data.add_player_conn_state("0", "True")
        self.data.add_player_addr("0", self.server_port)

    def menu(self):
        button_play = Button(
            x=self.resolution[0] // 2 - BUTTON_WIDTH // 2,
            y=self.resolution[1] // 2 - BUTTON_HEIGHT // 2,
            action=self.button_player_action
        )

        while True:
            try:
                self.clock.tick(self.fps)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_game()

                    button_play.handle_event(event)

                self.display_surface.fill((0, 0, 0))
                button_play.draw(self.display_surface)
                pygame.display.flip()
            except pygame.error as e:
                print(e)
                print("MENU")
                self.disconnect_clients()
                self.close_server()
                self.quit_game()
                

    def button_player_action(self):
        self.create_player()
        self.game()

    def wait_connections(self, server_socket):
        try:
            client_socket, client_address = server_socket.accept()
            
            self.selector.register(client_socket, selectors.EVENT_READ, self.recv_data)
            
            print("ESTABELECENDO CONEXÃO")
            with self.lock:
                self.client_sockets.append(client_socket)
            

            self.data.add_players_connected()
            if len(self.data.get_ids()) > 0:
                id = str(int(self.data.get_ids()[-1])+1)
            else:
                id = "0"
            self.data.add_ids(id)
            p = Player(500, 500, (50, 50), id=id)
            self.data.add_players_list(p)
            self.data.add_players_data(id, p.get_position())
            self.data.add_player_conn_state(id, "True")
            self.data.add_player_addr(id, client_address[1])

            data = self.prepare_game_data()
            self.send_data(client_socket, data)

            self.loop_data()

        except socket.error as e:
            print("Erro ao aguardar conexões:", str(e))

    
    def loop_data(self):
        try:
            while True:
                events = self.selector.select()

                for key, _ in events:
                    callback = key.data
                    callback(key.fileobj)
        except Exception as e:
            print(f"Erro no loop de dados: {e}")
            for sock in self.client_sockets:
                self.disconnect_client(sock)

    def recv_data(self, sock):
        try:
            data = sock.recv(128).decode()
            if len(data.split(",")) == 4:  
                id, x, y, conn = data.split(",")
                if id in self.data.get_ids():
                    self.update_player_conn_state(id, conn)
                    self.update_player_data(id, x, y)
                    if conn == "False":
                        print(data)
                        self.disconnect_client(sock)
                        self.remove_player(id)
            else:
                pass

            

        except socket.error as e:
            print("Erro ao receber dados do cliente:", str(e))
            self.disconnect_client(sock)

    def update_player_conn_state(self, id, conn):
        for id in self.data.get_ids():
            for player in self.data.get_players_list():
                if id == player.id:
                    self.data.set_conn_state(id, conn)

    def sync_players(self):
        for id in self.data.get_ids():
            for player in self.data.get_players_list():
                if id == player.id:
                    state = self.data.get_conn_state(id)
                    if state == "False":
                        self.data.remove_player(id)

    def disconnect_client(self, client_socket):
        try:
            with self.lock:
                if client_socket in self.client_sockets:
                    self.client_sockets.remove(client_socket)
            client_socket.close()
            self.selector.unregister(client_socket)

        except socket.error:
            pass

    def disconnect_clients(self):
        for sock in self.client_sockets:
            sock.close()
            self.selector.unregister(sock)

    def close_server(self):
        self.server_socket.close()

    def remove_player(self, id):
        self.data.remove_player(id)

    def create_thread(self, target):
        thread = threading.Thread(target=target, args=(self.server_socket,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    game_server = GameServer()
    game_server.main_loop()
