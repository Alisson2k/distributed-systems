from concurrent import futures
import grpc
from matplotlib.pyplot import connect
from client import ServiceCommand
import service_pb2
import service_pb2_grpc

MAX_GRPC_WORKERS = 10
GRPC_PORT = 5050

def verifica_existencia(CHAVE, HASH):
    if HASH == {}:
        return False
    else:
        for ch in HASH.keys():
            if ch == CHAVE:
                return True
            
        return False

def create(chave, valor, HASH):
    if verifica_existencia(chave, HASH) == False:
        HASH[chave] = valor
        mensagem = f'Chave: [{chave}] e Valor: [{valor}] foram cadastrados com sucesso!'
        pacote = f'4;{str(len(chave))};{chave};{str(len(valor))};{valor}'

        print(f'[+] {mensagem}')
        return (0, pacote)
    else:
        mensagem = f'A chave [{chave}] ja existe!'
        pacote = f'5;{str(len(chave))};{chave};{str(len(valor))};{valor};0'
        print(f'[-] {mensagem}')

        return (1, pacote)


def read(chave, HASH):
    if verifica_existencia(chave, HASH) == True:
        valor = HASH[chave]
        mensagem = f'Chave: [{chave}] e Valor: [{valor}] encontrados com sucesso!'
        pacote = f'4;{str(len(chave))};{chave};{str(len(valor))};{valor}'
        print(f'[+] {mensagem}')
        
        return (0, pacote)
    else:
        mensagem = f'A chave [{chave}] nao existe!'
        pacote = f'5;{str(len(chave))};{chave};1'
        print(f'[-] {mensagem}')

        return (1, pacote)

def update(chave, valor, HASH):
    if verifica_existencia(chave, HASH) == True:
        HASH[chave] = valor
        mensagem = f'Chave: [{chave}] e Valor: [{valor}] foram atualizados com sucesso!'
        pacote = f'4;{str(len(chave))};{chave};{str(len(valor))};{valor}'
        print(f'[+] {mensagem}')

        return (0, pacote)
    else:
        mensagem = f'A chave [{chave}] nao existe!'
        pacote = f'5;{str(len(chave))};{chave};{str(len(valor))};{valor};1'
        print(f'[-] {mensagem}')

        return (1, pacote)

def delete(chave, HASH):
    valor = HASH[chave]
    
    if verifica_existencia(chave, HASH) == True:
        del HASH[chave]

        mensagem = f'Chave: [{chave}] e Valor: [{valor}] foram apagados com sucesso!'
        pacote = f'4;{str(len(chave))};{chave};{str(len(valor))};{valor}'
        print(f'[+] {mensagem}')
        return (0, pacote)
    else:
        mensagem = f'A chave [{chave}] nao existe!'
        pacote = f'5;{str(len(chave))};{chave};{str(len(valor))};{valor};1'
        print(f'[-] {mensagem}')

        return (1, pacote)

class HashService(service_pb2_grpc.HashServicer):

    def Create(self, request, context):
        CHAVE = request.chave.lower()
        VALOR = request.valor
        SERVICO = request.servico

        if SERVICO == '0':
            resp = create(CHAVE, VALOR, HASH)
        elif SERVICO == 'ServiceCommand.SERVICO_1':
            resp = create(CHAVE, VALOR, HASH_S1)
        else:
            resp = create(CHAVE, VALOR, HASH_S2)


        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Read(self, request, context):
        CHAVE = request.chave.lower()
        SERVICO = request.servico

        if SERVICO == '0':
            resp = read(CHAVE, HASH)
        elif SERVICO == 'ServiceCommand.SERVICO_1':
            resp = read(CHAVE, HASH_S1)
        else:
            resp = read(CHAVE, HASH_S2)

        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Update(self, request, context):
        CHAVE = request.chave.lower()
        VALOR = request.valor
        SERVICO = request.servico
        
        if SERVICO == '0':
            resp = update(CHAVE, VALOR, HASH)
        elif SERVICO == 'ServiceCommand.SERVICO_1':
            resp = update(CHAVE, VALOR, HASH_S1)
        else:
            resp = update(CHAVE, VALOR, HASH_S2)

        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Delete(self, request, context):
        CHAVE = request.chave.lower()
        SERVICO = request.servico

        if SERVICO == '0':
            resp = delete(CHAVE, HASH)
        elif SERVICO == 'ServiceCommand.SERVICO_1':
            resp = delete(CHAVE, HASH_S1)
        else:
            resp = delete(CHAVE, HASH_S2)

        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])


def start_grpc():
    print("[+] Usando gRPC...")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_GRPC_WORKERS))

    try:
        service_pb2_grpc.add_HashServicer_to_server(HashService(), server)
        server.add_insecure_port(f'[::]:{GRPC_PORT}')
        server.start()

        print(f"[+] Host do servidor: [localhost:{GRPC_PORT}]")
        print("[+] gRPC conectado e pronto para receber chamadas!")

        start_service_1()

        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[-] Forçando parada via terminal")
        server.stop(True)


def start_service_1():
    print("\n[+] Inicializando Servico 1...")

    server1 = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_GRPC_WORKERS))

    con = HASH['receitas salgadas'].split('|')
    ip = con[0]
    porta = con[1]

    try:
        service_pb2_grpc.add_HashServicer_to_server(HashService(), server1)
        server1.add_insecure_port(f'{ip}:{porta}')
        server1.start()

        print(f"[+] Host do servico 1: {ip}:{porta}")
        print("[+] gRPC conectado e pronto para receber chamadas!")

        start_service_2()

        server1.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[-] Forçando parada via terminal")
        server1.stop(True)


def start_service_2():
    print("\n[+] Inicializando Servico 2...")

    server1 = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_GRPC_WORKERS))

    con = HASH['receitas doces'].split('|')
    ip = con[0]
    porta = con[1]

    try:
        service_pb2_grpc.add_HashServicer_to_server(HashService(), server1)
        server1.add_insecure_port(f'{ip}:{porta}')
        server1.start()

        print(f"[+] Host do servico 2: {ip}:{porta}")
        print("[+] gRPC conectado e pronto para receber chamadas!")

        server1.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[-] Forçando parada via terminal")
        server1.stop(True)

if __name__ == "__main__":
    HASH = dict()
    HASH = {'receitas salgadas':'127.0.0.1|5051', 'receitas doces':'127.0.0.2|5052'}

    HASH_S1 = dict()
    HASH_S2 = dict()
    start_grpc()
    