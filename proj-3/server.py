from concurrent import futures
import hashlib
import grpc
import service_pb2
import service_pb2_grpc
import multiprocessing
import sys
import util
import math
import logging as log
log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] -- [%(levelname)s] %(message)s",
    handlers=[
        log.StreamHandler()
    ]
)

NODES = 5
MAX_KEYS = 32
MAX_GRPC_WORKERS = 10
HOST = 'localhost'
INITIAL_PORT = 5050
VERBOSE = len(sys.argv) > 1 and sys.argv[1] == "--verbose"

def str_to_bits(key):
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'little') % MAX_KEYS

class HashService(service_pb2_grpc.HashServicer):

    def __init__(self, node, send_to):
        self.node = node
        self.send_to = send_to

    def available_node(self, chave, atual):
        hash_key = str_to_bits(chave)

        if atual:
            return (-1, True)

        val = list(map(lambda x : x.id, self.node.fingertable.values()))

        escolha = 0
        maior_limite = True
 
        for id in val:
            if int(hash_key) == int(id):
                choice = id
                maior_limite = False
                break
            elif int(hash_key) < int(id):
                choice = val[escolha]
                maior_limite = False
                break

            escolha += 1

        if maior_limite:
            if val[escolha-1] < val[escolha-2]:
                choice = val[escolha-2]
            else:
                choice = val[escolha-1]

        print(f'[+] Chave: [{hash_key}], requisição transferida do nó [{self.node.id}] para o nó [{choice}]')

        return (choice, not maior_limite)

    def Create(self, request, context):
        (node_id, atual) = self.available_node(request.chave, request.atual)

        if request.atual or node_id == self.node.id:
            try:
                self.node.hash[request.chave] = request.valor
                return service_pb2.HashReply(codigo=0, resposta=f'Receita [{request.chave}] criada com sucesso')
            except Exception as e:
                return service_pb2.HashReply(codigo=1, resposta=f'ERRO: {str(e)}')
        else:
            return self.send_to(node_id, request.comando, request.chave, request.valor, atual)

    def Read(self, request, context):
        (node_id, atual) = self.available_node(request.chave, request.atual)
        
        if request.atual or node_id == self.node.id:
            try:
                valor = self.node.hash[request.chave]
                return service_pb2.HashReply(codigo=0, resposta=valor)
            except Exception as e:
                return service_pb2.HashReply(codigo=1, resposta=f'ERRO: {str(e)}')
        else:
            return self.send_to(node_id, request.comando, request.chave, request.valor, atual)

    def Update(self, request, context):
        (node_id, atual) = self.available_node(request.chave, request.atual)
        
        if request.atual or node_id == self.node.id:
            try:
                self.node.hash[request.chave] = request.valor
                return service_pb2.HashReply(codigo=0, resposta=f'Receita [{request.chave}] atualizada com sucesso')
            except Exception as e:
                return service_pb2.HashReply(codigo=1, resposta=f'ERRO: {str(e)}')
        else:
            return self.send_to(node_id, request.comando, request.chave, request.valor, atual)

    def Delete(self, request, context):
        (node_id, atual) = self.available_node(request.chave, request.atual)
        
        if request.atual or node_id == self.node.id:
            try:
                del self.node.hash[request.chave]
                return service_pb2.HashReply(codigo=0, resposta=f'Receita [{request.chave}] deletada com sucesso')
            except Exception as e:
                return service_pb2.HashReply(codigo=1, resposta=f'ERRO: {str(e)}')
        else:
            return self.send_to(node_id, request.comando, request.chave, request.valor, atual)

class Node(object):
    def __init__(self, ip, port, index, id, value_range, send_to):
        self.ip = ip
        self.port = port
        self.index = index
        self.id = id
        self.range = value_range
        self.send_to = send_to
        self.hash = dict()
        self.fingertable = dict()

    def run(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_GRPC_WORKERS))

        service_pb2_grpc.add_HashServicer_to_server(HashService(self, self.send_to), self.server)
        self.server.add_insecure_port(f'{self.ip}:{self.port}')
        self.server.start()

        log.info(f"Host conectado: [{self.ip}:{self.port}]")

        while True:
            pass

class MainServer(object):
    def __init__(self, count_nodes, max_keys):
        self.count_nodes = count_nodes
        self.max_keys = max_keys
        self.range_size = math.ceil(max_keys/count_nodes)
        self.servers = self._start_servers()

    def _start_servers(self):
        servers = []
        for i in range(0, self.count_nodes):
            port = 5050 + i

            if i == 0 :
                value_range = (
                    (i * self.range_size),((i + 1) * self.range_size) - 1
                )
            else:
                value_range = (
                    (i * self.range_size)+1,((i + 1) * self.range_size) - 1
                )

            servers.append(Node(HOST, port, i, (i + 1) * self.range_size, value_range, self.send_to))

        for i in range(0, self.count_nodes):
            servers[i].fingertable = util.gen_finger_table(MAX_KEYS, servers[i].id, servers, self.count_nodes)

            if VERBOSE:
                print(f'\nServer: {servers[i].id}\nFinger Table:')
                for key, val in servers[i].fingertable.items():
                    print(f'{key} : {val.id}')

        return servers

    def send_to(self, node_id, comando, chave, valor, atual):
        cur_node = None
        for server in self.servers:
            if server.id == node_id:
                cur_node = server

        if cur_node is not None:
            with grpc.insecure_channel(f'{cur_node.ip}:{cur_node.port}') as channel:
                return util.treat_command(channel, comando, chave, valor, atual)

    def start(self):
        workers = []
        for server in self.servers:
            worker = multiprocessing.Process(target=server.run)
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()

if __name__ == '__main__':
    srv = MainServer(NODES, MAX_KEYS)
    srv.start()
