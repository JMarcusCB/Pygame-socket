import pygame
import socket
import threading
import sys
import selectors
import json

from data6 import Data_manager

from player import Player
from button import Button, BUTTON_WIDTH, BUTTON_HEIGHT

class GameClient:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.resolution = (600, 600)
        self.display_surface = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Block mp - CLIENT")
        self.display_rect = pygame.Rect(0, 0, self.resolution[0], self.resolution[1])

        self.selector = selectors.DefaultSelector()
        self.server_ip, self.server_port = "192.168.1.105", 9999

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.data = Data_manager()

        self.id = None
        self.conn = True

        self.lock = threading.Lock()

        self.running = False

    def main_loop(self):
        self.menu()

    def game(self):
        try:
            self.running = True
            self.socket.connect((self.server_ip, self.server_port))
            self.selector.register(self.socket, selectors.EVENT_READ | selectors.EVENT_WRITE, self.recv_data)
            self.create_thread(self.loop_data)

            while self.running:
                self.clock.tick(60)
                self.handle_events()
                self.update_game()
                self.send_player_data()
                self.draw_game()
        except socket.error as e:
            print("Não foi possível se conectar:")
            print(e)
            self.disconnect()
        except Exception as e:
            print("Não foi possível se conectar:")
            print(e)
            self.disconnect()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.disconnect()
                self.quit_game()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.print_debug_info()

    def print_debug_info(self):
        with self.lock:
            print("=====================================================")
            print("meu id: ", self.id)
            print("lista de ids: ", self.data.get_ids())
            print("lista de players: ", self.data.get_players_list())
            print(self.data.get_players_datas())
            print("players conectados: ", self.data.get_players_connected())
            print()

    def update_game(self):
        self.sync_players()
        for player in self.data.get_players_list():
            if player.id == self.id:
                player.update()
                player.rect.clamp_ip(self.display_rect)

    def get_my_pos(self):
        for player in self.data.get_players_list():
            if player.id == self.id:
                x = player.rect.x
                y = player.rect.y
                return x, y
        
        return 10,10

    def draw_game(self):
        self.display_surface.fill((0, 0, 0))
        for player in self.data.get_players_list():
            player.draw()
        pygame.display.flip()

    def create_player(self):
        with self.lock:
            self.data.add_players_connected()
            self.data.add_ids("0")
            p = Player(10, 10, (50, 50), "0")
            self.data.add_players_list(p)
            self.data.add_players_data("0", p.get_position())

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
            except pygame.error:
                self.disconnect()       

            try:
                self.display_surface.fill((0, 0, 0))
                button_play.draw(self.display_surface)
                pygame.display.flip()
            except pygame.error:
                self.disconnect()

    def button_player_action(self):
        self.create_player()
        self.game()

    def loop_data(self):
        try:
            response = self.recv_data_from_server(self.socket)
            self.handle_response(response)
            while self.running:
                events = self.selector.select()
                for key, _ in events:
                    callback = key.data
                    callback(key.fileobj)
        except socket.error as e:
            print("Erro no loop de dados:")
            print(e)
            self.disconnect()

    def recv_data_from_server(self, sock):
        try:
            response = sock.recv(1024).decode()
            try:
                return json.loads(response)
            except json.decoder.JSONDecodeError as e:
                print(e)
                print("RECV_DATA_FROM SERVER")

        except socket.error as e:
            print("Erro ao receber dados do servidor:")
            print(e)
            self.disconnect()

    def handle_response(self, response):
        with self.lock:
            self.data.set_players_connected(int(response["players_connected"]))
            self.data.set_ids(response["ids"])
            if self.id is None:                                                  
                self.id = response["ids"][-1]
                print("Meu ID:", self.id)
            self.data.set_players_data(response["players_datas"])

    def recv_data(self, sock):
        data = self.recv_data_from_server(sock)
        self.handle_response(data)
        
        with self.lock:
            for key in self.data.get_players_datas():
                id = key
                x, y = self.data.get_players_datas([key, "pos", "x"]), self.data.get_players_datas([key,"pos","y"])
                conn = self.data.get_players_datas([key, "conn_state"])
                self.update_player_conn_state(id, conn)
                self.update_player_data(id, x, y)


    def update_player_conn_state(self, id, conn):
        for id in self.data.get_ids():
            for player in self.data.get_players_list():
                if id == player.id:
                    self.data.set_conn_state(id, conn)
                if id == self.id:
                    self.conn = self.data.get_conn_state(id)

    def send_player_data(self):
        x, y = self.get_my_pos()
        data = f"{self.id},{x},{y},{self.conn}"
        self.send_data(data)

    def update_player_data(self, id, x, y):
        if id in self.data.get_players_datas():
            self.data.modify_players_data_pos(id, "x", x)
            self.data.modify_players_data_pos(id, "y", y)
        for player in self.data.get_players_list():
            if id == player.id:
                player.set_position(x, y)

    def send_data(self, data):
        try:
            self.socket.sendall(data.encode())
        except socket.error as e:
            print("Erro ao enviar mensagem:")
            print(e)
            self.disconnect()

    def sync_players(self):

        players_id_list = []
        players_data_list = []
        for player_id in self.data.get_players_datas().keys():
            players_id_list.append(str(player_id))
        
        for player in self.data.get_players_list():
            players_data_list.append(str(player.id))
        # ["0", "1"]
        # ["0"]

        for p_id in players_id_list:
            if p_id not in players_data_list:
                print("player criado")
                self.data.add_ids(str(p_id))
                p = Player(
                    int(self.data.get_players_datas([str(p_id), "pos", "x"])),
                    self.data.get_players_datas([str(p_id), "pos", "y"]),
                    (50, 50),
                    str(p_id)
                )
                self.data.add_players_list(p)

        with self.lock:
            self.data.remove_players_clients()

    def disconnect(self):
        with self.lock:
            self.running = False
            self.data.print_status()
            self.close_socket()
            self.quit_game()
            sys.exit()

    def close_socket(self, not_sock_register=True):
        try:
            if self.socket.fileno() != -1:
                if not_sock_register:
                    pass
                else:
                    self.selector.unregister(self.socket)
                self.socket.close()
        except socket.error as e:
            print("Erro ao fechar o socket:", str(e))

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def create_thread(self, target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    game_client = GameClient()
    game_client.main_loop()
