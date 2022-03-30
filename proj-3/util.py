import hashlib
import service_pb2
import service_pb2_grpc

def treat_command(channel, comando, chave, valor, atual = False):
    stub = service_pb2_grpc.HashStub(channel)

    if comando == 'create':
        return stub.Create(service_pb2.HashRequest(comando=comando,
                                                   chave=chave,
                                                   valor=valor,
                                                   atual=atual))
    elif comando == 'read':
        return stub.Read(service_pb2.HashRequest(comando=comando,
                                                 chave=chave,
                                                 valor=valor,
                                                 atual=atual))
    elif comando == 'update':
        return stub.Update(service_pb2.HashRequest(comando=comando,
                                                   chave=chave,
                                                   valor=valor,
                                                   atual=atual))
    elif comando == 'delete':
        return stub.Delete(service_pb2.HashRequest(comando=comando,
                                                   chave=chave,
                                                   valor=valor,
                                                   atual=atual))

def gen_finger_table(max_keys, id, servers, N):
    finger_table = dict()

    for i in range(int(max_keys)):
        tam_salto = 2**i
        
        if tam_salto > int(max_keys/2):
            break

        pos_salto = (id + tam_salto)%max_keys

        for i in range(N):
            if pos_salto <= servers[i].id:
                responsavel = servers[i]
                break

        finger_table[pos_salto] = responsavel

    return finger_table

INITIAL_PORT = 4000

def gen_group_hosts(group_id, group_count):
    return [f'localhost:{INITIAL_PORT + (group_count * group_id) + i}' for i in range(group_count)]
