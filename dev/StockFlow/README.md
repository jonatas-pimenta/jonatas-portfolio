# StockFlow – Gestão de Estoque com GUI e MongoDB

Aplicação desktop em Python com interface Tkinter, banco NoSQL MongoDB e geração de relatórios via Pandas/Excel. Permite cadastro, consulta, movimentação e controle de estoque, com exportação e visão analítica para apoiar operação de pequenas empresas.

## Arquitetura Implementada

Aplicação monolítica desktop com GUI em Tkinter, camada de dados em MongoDB e camada de relatórios em Pandas/Excel.

<p align="center">
  <img src="screenshots/relatorios.png" width="70%" alt="Relatórios do StockFlow">
</p>

| Componente | Detalhe Técnico | Função Principal |
| :--- | :--- | :--- |
| **GUI Desktop** | Python 3.12 + Tkinter | Cadastro, consultas, movimentações, filtros |
| **Banco de Dados** | MongoDB 4.4+ (coleções produtos/movimentacoes) | Persistência de estoque e histórico |
| **Relatórios** | Pandas + OpenPyXL | Geração e exportação para Excel |
| **Scripts de Execução** | executar.sh + venv | Criação de ambiente e bootstrap da aplicação |

## Principais Funcionalidades

**Cadastro e Consulta**
- CRUD de produtos (nome, tipo, quantidade, preço, etc.)
- Busca por nome, tipo ou código

**Movimentação de Estoque**
- Registro de entradas e saídas
- Histórico detalhado de movimentações

**Relatórios e Exportação**
- Relatórios filtrados por período, produto ou tipo
- Exportação para Excel (Pandas/OpenPyXL)
- Visão de produtos críticos (estoque baixo)

**Interface e Usabilidade**
- GUI em abas separando produtos, movimentações e relatórios
- Feedback visual e formulários simples

## Aplicação Profissional / Valor para Empresas

- Reduz esforço manual no controle de estoque e minimiza erros
- Centraliza dados em MongoDB, facilitando integrações futuras
- Geração rápida de relatórios para tomada de decisão e auditoria
- Exportação para Excel para compartilhamento com áreas de negócio

## Competências Técnicas Demonstradas

- **Python Desktop (Tkinter):** Construção de GUI em abas e formulários
- **MongoDB (pymongo):** Persistência NoSQL para produtos e movimentações
- **Pandas/OpenPyXL:** Relatórios e exportação para Excel
- **Estruturação de Projeto:** Separação de camadas (GUI, dados, execução)
- **Automação de Ambiente:** Script executar.sh com venv e dependências

## 📁 Estrutura do Projeto

```
StockFlow/
├── main.py             # Interface e fluxo principal
├── db.py               # Integração com MongoDB
├── executar.sh         # Criação/ativação de venv e execução
├── requirements.txt    # Dependências Python
├── screenshots/
│   ├── relatorios.png
│   ├── produtos.png
│   └── movimentacao.png
└── README.md
```

## 🔧 Demonstração Técnica

### Integração com MongoDB
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["adega"]
produtos = db["produtos"]

# Inserir produto
produtos.insert_one({"nome": "Vinho Tinto", "quantidade": 10})

# Buscar produto
for produto in produtos.find({"nome": "Vinho Tinto"}):
    print(produto)
```

### Exportação de Relatório para Excel
```python
import pandas as pd

# Exemplo de dados previamente carregados do Mongo
dados = list(produtos.find())
df = pd.DataFrame(dados)
df.to_excel("relatorio_estoque.xlsx", index=False)
```

## ⚡ Como Executar

```bash
cd /home/lion/Documentos/Projetos/jonatas-portfolio/dev/StockFlow
chmod +x executar.sh
./executar.sh
```

Notas:
- O script cria/usa venv em ./venv e executa main.py.
- Se necessário, ative manualmente: `. ./venv/bin/activate && python3 main.py`.
- Se o MongoDB não estiver rodando localmente: `sudo systemctl start mongod`.

## 💡 Desafios e Soluções (Troubleshooting)

**Desafio 1: MongoDB não iniciado**
- Solução: iniciar serviço (`sudo systemctl start mongod`) ou apontar para instância remota.

**Desafio 2: Dependências não instaladas**
- Solução: executar `./executar.sh` ou `pip install -r requirements.txt` dentro do venv.

**Desafio 3: Exportação para Excel falhando**
- Solução: garantir `openpyxl` instalado (já listado em requirements).

## 📸 Screenshots

<p align="center">
  <img src="screenshots/relatorios.png" alt="Relatórios" width="70%"><br>
  <em>Relatórios — estatísticas gerais e produtos críticos</em>
</p>

<p align="center">
  <img src="screenshots/produtos.png" alt="Produtos" width="70%"><br>
  <em>Produtos — cadastro/edição e lista</em>
</p>

<p align="center">
  <img src="screenshots/movimentacao.png" alt="Movimentações" width="70%"><br>
  <em>Movimentações — entrada/saída e histórico</em>
</p>

---

<div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>
