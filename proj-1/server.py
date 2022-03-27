from concurrent import futures
import socket
import sys
import grpc
import service_pb2
import service_pb2_grpc

MAX_GRPC_WORKERS = 10
GRPC_PORT = 5050

HASH = dict()
HASH = {'S1':'192.168.0.1|5051', 'S2':'192.168.0.2|5052'}

def verifica_existencia(CHAVE):
    if HASH == {}:
        return False
    else:
        for ch in HASH.keys():
            if ch == CHAVE:
                return True
            
        return False

def create(chave, valor):
    if verifica_existencia(chave) == False:
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


def read(chave):

    if verifica_existencia(chave) == True:
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

def update(chave, valor):
    if verifica_existencia(chave) == True:
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

def delete(chave):
    valor = HASH[chave]
    
    if verifica_existencia(chave) == True:
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
        CHAVE = request.chave
        VALOR = request.valor

        resp = create(CHAVE, VALOR)
        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Read(self, request, context):
        CHAVE = request.chave

        resp = read(CHAVE)

        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Update(self, request, context):
        CHAVE = request.chave
        VALOR = request.valor

        resp = update(CHAVE, VALOR)

        if resp[0] == 0:
            return service_pb2.HashReply(codigo=0, pacote=resp[1])
        else:
            return service_pb2.HashReply(codigo=1, pacote=resp[1])

    def Delete(self, request, context):
        CHAVE = request.chave

        resp = delete(CHAVE)

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

        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[-] Forçando parada via terminal")
        server.stop(True)

if __name__ == "__main__":
    start_grpc()
