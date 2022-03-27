# Hash table - gRPC #

Para rodar utilize `python3+`, primeiro instale as dependências com

    $ pip install -r requirements.txt

Use o seguinte comando para gerar o código Python:

    $ python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./service.proto
    
Execute:

    $ python server.py grpc
    $ python client.py grpc
