import os
import enum
import grpc
from markupsafe import re
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
            comando = input("\n[*] Meu Livro de Receitas: \n\n1 - Receitas Salgadas\n2 - Receitas Doces\nX - Sair\n\n")

            if comando.lower() == 'x':                
                print('\n[*] Desconectado!')
                break

            try:
                serv_command = ServiceCommand(int(comando))
                res = send_for_server(serv_command, client)
                if res is not None:
                    ip = res[4].split("|")[0]
                    port = res[4].split("|")[1]
                    print(f'[+] Conectando ao servico [{res[2]}] no HOST: [{ip}:{port}]')

                    connect_in_server(ip, port, serv_command)

            except Exception as e:
                print(f'ERRO 1: {e}')
                print("\n[*] Comando invalido! Tente novamente...\n")

        except KeyboardInterrupt:
            print("\n[-] Forçando a parada via terminal")
            break

def connect_in_server(ip, port, serv_command):
    try:
        with grpc.insecure_channel(f'{ip}:{port}') as channel:
            while True:
                try:
                    comando = input("\n[*] Escolha a opcao desejada: \n\n0 - Adicionar Receita\n1 - Ler Receita\n2 - Atualizar Receita\n3 - Deletar Receita\nX - Sair\n\n")

                    if comando.lower() == 'x':
                        print('\n[*] Desconectado!')
                        break

                    try:
                        enum_comando = Command(int(comando))
                        send_with_grpc(enum_comando, channel, serv_command)
                    except Exception as e:
                        print(f'ERRO 2: {e}')
                        print("\n[*] Comando invalido! Tente novamente...\n")

                except KeyboardInterrupt:
                    print("\n[-] Forçando a parada via terminal")
                    break
    except:
        print(f'[-] Erro ao conectar em [{ip}:{port}]')

def erro(cod, chave):
    if cod == '0':
        return f'A Receita: [{chave}] ja existe!'
    elif cod == '1':
        return f'A Receita: [{chave}] nao existe!'
    elif cod == 'servico':
        return f'Servico Indisponivel!'
    else:
        return 'Erro nao identificado!'

def sucesso(cod, chave, valor):
    if cod == 'create':
        return f'A receita [{chave}] foi cadastrada com sucesso!'
    elif cod == 'read':
        return f'[{chave}]\nReceita: \n{valor}'
    elif cod == 'update':
        return f'A receita [{chave}] foi atualizada com sucesso!'
    elif cod == 'delete':
        return f'A rececita [{chave}] foi deletada com sucesso!'
    elif cod == 'servico':
        return f'Servico: {chave} - Servidor: {valor}'
    else:
        return 'Operação realizada com sucesso!'

def send_with_grpc(command: Command, channel, serv_command):

    if command == Command.CREATE:
        
        cmd = 'create'
        CHAVE = input('[*] Digite o nome da receita: ')
        VALOR = input('[*] Digite a receita: ')
        
        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Create(service_pb2.HashRequest(conteudo='0',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE,
                                                       tam_valor=len(VALOR),
                                                       valor=VALOR,
                                                       servico = str(serv_command)))
    elif command == Command.READ:
        cmd = 'read'
        CHAVE = input('[*] Digite a receita que deseja ler: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE,
                                                     servico = str(serv_command)))
    elif command == Command.UPDATE:
        cmd = 'update'
        CHAVE = input('[*] Digite a receita para atualizacao: ')
        VALOR = input('[*] Digite a nova receita: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Update(service_pb2.HashRequest(conteudo='2',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE,
                                                       tam_valor=len(VALOR),
                                                       valor=VALOR,
                                                       servico = str(serv_command)))
    elif command == Command.DELETE:
        cmd = 'delete'
        CHAVE = input('[*] Digite a receita para exclusao: ')

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Delete(service_pb2.HashRequest(conteudo='3',
                                                       tam_chave=len(CHAVE),
                                                       chave=CHAVE,
                                                       servico = str(serv_command)))

    # clear()

    if response is None:
        print("[-] Nenhuma resposta obtido pelo servidor")
    else:
        pacote = response.pacote
        pac = pacote.split(';')

        if pac[0] == '4':
            print(f'[+] {sucesso(cmd, pac[2], pac[4])}')
        else:
            print(f'[-] ERRO: {erro(pac[-1], pac[2])}')

def send_for_server(command: ServiceCommand, channel):
    if command == ServiceCommand.SERVICO_1:
        cmd = 'servico'
        CHAVE = 'Receitas Salgadas'

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE,
                                                     servico = '0'))
    elif command == ServiceCommand.SERVICO_2:
        cmd = 'servico'
        CHAVE = 'Receitas Doces'

        stub = service_pb2_grpc.HashStub(channel)
        response = stub.Read(service_pb2.HashRequest(conteudo='1',
                                                     tam_chave=len(CHAVE),
                                                     chave=CHAVE,
                                                     servico = '0'))

    # clear()

    if response is None:
        print("[-] Nenhuma resposta obtido pelo servidor")
        return None
    else:
        pacote = response.pacote
        pac = pacote.split(';')

        if pac[0] == '4':
            print(f'[+] {sucesso(cmd, pac[2], pac[4])}')
        else:
            print(f'[-] ERRO: {erro("servico", pac[2])}')
        
        return pac

if __name__ == "__main__":
    start_grpc()