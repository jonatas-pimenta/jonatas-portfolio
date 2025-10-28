# 1. Usar uma imagem base oficial do Python.
# A tag "slim" é uma versão mais leve, ótima para economizar espaço.
FROM python:3.9-slim

# 2. Definir o diretório de trabalho dentro do container.
# Todos os comandos seguintes serão executados a partir daqui.
WORKDIR /app

# 3. Copiar os arquivos da nossa pasta local para dentro do container.
# O primeiro "." significa "tudo na pasta atual" (sniffer.py e Dockerfile).
# O segundo "." significa o diretório de trabalho definido acima ("/app").
COPY . .

# 4. Instalar as dependências do nosso projeto (apenas Scapy).
# Este comando é executado durante a construção da imagem.
RUN pip install scapy

# 5. (LINHA NOVA) Atualiza a lista de pacotes e instala a libpcap.
# A libpcap é uma dependência de sistema para o Scapy poder filtrar pacotes.
RUN apt-get update && apt-get install -y libpcap-dev && rm -rf /var/lib/apt/lists/*

# 6. Comando que será executado quando o container iniciar.
# Diz ao container para rodar o nosso script Python. O "-u" garante que a saída
# apareça no terminal em tempo real.
CMD ["python", "-u", "sniffer.py"]
