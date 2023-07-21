
class Data_manager():
    def __init__(self) -> None:
        self._players_list = []
        self._players_datas = {} # "0": {"pos": {"x": 0, "y": 0}}, "1": {"pos": {"x": 1, "y": 1}}

        self._ids = []

        self._players_connected = 0

    # players_list
    def add_players_list(self, player):
        self._players_list.append(player)

    def get_players_list(self):
        return self._players_list

    # players_datas
    def set_players_data(self, new_data):
        self._players_datas = new_data

    def modify_players_data_pos(self, id, axle, new_value):
        self._players_datas[id]["pos"][axle] = new_value

    def add_players_data(self, key, value):
        self._players_datas[key] = value
    
    # CONN
    def add_player_conn_state(self, id, state):
        self._players_datas[id]["conn_state"] = state
    
    def set_conn_state(self, id, state):
        self._players_datas[id]["conn_state"] = state

    def get_conn_state(self, id):
        return self._players_datas[id]["conn_state"]
    
    # ADDR
    def add_player_addr(self, key, addr):
        self._players_datas[key]["addr"] = addr

    def get_players_datas(self, keys=None):
        if keys is not None:
            current_dict = self._players_datas
            for key in keys:
                if key in current_dict:
                    current_dict = current_dict[key]
                else:
                    return None
                
            return current_dict
        else:
            return self._players_datas
    

    # ids
    def set_ids(self, new_id_list):
        self._ids = new_id_list[:]

    def add_ids(self, id):
        self._ids.append(id)

    def get_ids(self):
        return self._ids

    # players_connected
    def set_players_connected(self, new_value):
        self._players_connected = new_value

    def add_players_connected(self):
        self._players_connected += 1

    def remove_players_connected(self):
        self._players_connected -= 1

    def get_players_connected(self):
        return int(self._players_connected)
    
    def print_status(self):
        print("---------------------------------------------")
        #print("Players conectados: ", self._players_connected)
        #print("Players ids: ", self._ids)
        #print("Players lista: ", self._players_list)
        #print("Players data: ", self._players_datas)
        print()
        print()
        pass


    # ------------------------- #
    def remove_players_list(self, player):

        self._players_list.remove(player)

    def remove_id(self, id):
        if id in self.get_ids():
            self._ids.remove(id)

    def remove_player_data(self, id):
        for key in self._players_datas:
            if key == id:
                del self._players_datas[key]
                break

    def verify_sockets_conn(self, clients_sockets):
        temp_list_client_socket = []
        temp_list_ids = []
        count = 0
        for client in clients_sockets:  
            temp_list_client_socket.append(client.getpeername()[1])
            temp_list_ids.append(count)
            count += 1
        
        copy_dict = self.get_players_datas().copy()
        for i, item in copy_dict.items():
            if i != "0":
                if item["addr"] not in temp_list_client_socket:
                    self.remove_player(i)

    def remove_players_clients(self):
        players_list = []
        for player in self.get_players_list():
            players_list.append(player.id)


        for p_id in players_list:
            if p_id not in self.get_ids():
                print("REMOVENDO: ", p_id)
                self.remove_player(p_id)


    def remove_player(self, id):
        for player in self._players_list:
            if player.id == id:
                print("PLAYER REMOVIDO: ", id)
                print("LISTA ANTES -> ", self.get_players_list())
                self.remove_players_list(player)
                self.remove_id(id)
                self.remove_player_data(id)
                self.remove_players_connected()
                print()
                print("LISTA atual -> ", self.get_players_list())
                



d = Data_manager()


