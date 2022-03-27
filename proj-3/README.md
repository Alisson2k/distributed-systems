# Chord Node #

Para rodar utilize `python3+`, primeiro instale as dependências com

    $ pip install -r requirements.txt

Use o seguinte comando para gerar o código Python:

    $ python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./service.proto
    
Para rodar o servidor:

    $ python server.py

Para rodar de uma forma mais verbosa utilize `--verbose` no comando acima

Para rodar o cliente:

    $ python client.py
