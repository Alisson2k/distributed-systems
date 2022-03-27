import os
import sys
import enum
import grpc
import socket
import service_pb2
import service_pb2_grpc

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class ServiceCommand(enum.Enum):
    SERVICO_1 = 1
    SERVICO_2 = 2

class Command(enum.Enum):
    CREATE = 0
    READ = 1
    UPDATE = 2
    DELETE = 3

def start_grpc():
    print("[+] Usando gRPC...")
    ip = input("[+] Digite o IP do servidor: ")
    port = input("[+] Digite a porta do servidor: ")

    try:
        with grpc.insecure_channel(f'{ip}:{port}') as channel:
            print("[+] Conectado com sucesso!")
            run_client(channel)
    except:
        print("[-] Erro durante a conexão com o servidor")


def run_client(client):
    while True:
        try:
            comando = input("\n[*] Escolha o serviço desejado: \n\n1 - Servico 1\n2 - Servico 2\nX - Sair\n\n")

            if comando.lower() == 'x':                
                print('\n[*] Desconectado!')
                break

            try:
                enum_comando = ServiceCommand(int(comando))
                res = send_for_server(enum_comando, client)
                
                if res is not None:
                    ip = res[4].split("|")[0]
                    port = res[4].split("|")[1]
                    print(f'[+] Conectando ao servico [{res[2]}] no HOST: [{ip}:{port}]')

                    connect_in_server(ip, port)

            except Exception as e:
                print(f'EXE: {e}')
                print("\n[*] Comando invalido! Tente novamente...\n")

        except KeyboardInterrupt:
            print("\n[-] Forçando a parada via terminal")
            break

def connect_in_server(ip, port):
    try:
        with grpc.insecure_channel(f'{ip}:{port}') as channel:
            while True:
                try:
                    comando = input("\n[*] Escolha a opcao desejada: \n\n0 - Create\n1 - Read\n2 - Update\n3 - Delete\nX - Sair\n\n")

                    if comando.lower() == 'x':
                        print('\n[*] Desconectado!')
                        break

                    try:
                        enum_comando = Command(int(comando))
                        send_with_grpc(enum_comando, channel)
                    except:
                        print("\n[*] Comando invalido! Tente novamente...\n")

                except KeyboardInterrupt:
                    print("\n[-] Forçando a parada via terminal")
                    break
    except:
        print(f'[-] Erro ao conectar em [{ip}:{port}]')

def erro(cod, chave):
    if cod == '0':
        return f'A Chave: [{chave}] ja existe!'
    elif cod == '1':
        return f'A chave: [{chave}] nao existe!'
    else:
        return 'Erro nao identificado!'

def sucesso(cod, chave, valor):
    if cod == 'create':
        return f'Servico: [{chave}] e IP/PORTA: [{valor}] foram cadastrados com sucesso!'
    elif cod == 'read':
        return f'Servico: [{chave}] e IP/PORTA: [{valor}] encontrados com sucesso!'
    elif cod == 'update':
        return f'Servico: [{chave}] e IP/PORTA: [{valor}] foram atualizados com sucesso!'
    elif cod == 'delete':
        return f'Servico: [{chave}] e IP/PORTA: [{valor}] foram apagados com sucesso!'
    else:
        return 'Operação realizada com sucesso!'

def send_with_grpc(command: Command, channel):
    if command == Command.CREATE:
        cmd = 'create'
        CHAVE = input('[*] Digite a chave que deseja inserir: ')
        VALOR = input('[*] Digite o valor a ser atribuido a chave: ')
        
        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Create(service_pb2.HashRequest(conteudo='0',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE,
                                                       tam_valor=len(VALOR),
                                                       valor=VALOR))
    elif command == Command.READ:
        cmd = 'read'
        CHAVE = input('[*] Digite a chave que deseja ler: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE))
    elif command == Command.UPDATE:
        cmd = 'update'
        CHAVE = input('[*] Digite a chave para atualizacao: ')
        VALOR = input('[*] Digite o novo Valor: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Update(service_pb2.HashRequest(conteudo='2',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE,
                                                       tam_valor=len(VALOR),
                                                       valor=VALOR))
    elif command == Command.DELETE:
        cmd = 'delete'
        CHAVE = input('[*] Digite a chave para exclusao: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Delete(service_pb2.HashRequest(conteudo='3',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE))

    clear()

    if response is None:
        print("[-] Nenhuma resposta obtido pelo servidor")
    else:
        pacote = response.pacote
        pac = pacote.split(';')

        if pac[0] == '4':
            print(f'[+] SUCESSO: {sucesso(cmd, pac[2], pac[4])}')
        else:
            print(f'[-] ERRO: {erro(pac[-1], pac[2])}')

def send_for_server(command: ServiceCommand, channel):
    if command == ServiceCommand.SERVICO_1:
        cmd = 'read'
        CHAVE = 'S1'

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE))
    elif command == ServiceCommand.SERVICO_2:
        cmd = 'read'
        CHAVE = 'S2'

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE))

    # clear()

    if response is None:
        print("[-] Nenhuma resposta obtido pelo servidor")
        return None
    else:
        pacote = response.pacote
        pac = pacote.split(';')

        if pac[0] == '4':
            print(f'[+] SUCESSO: {sucesso(cmd, pac[2], pac[4])}')
        else:
            print(f'[-] ERRO: {erro(pac[-1], pac[2])}')
        
        return pac

if __name__ == "__main__":
    start_grpc()