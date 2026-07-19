#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera dados de demonstracao para o STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM (cenario: adega)."""

import argparse
import random
from typing import Dict, List

from backend.database import EstoqueDB


PRODUTOS_BASE: List[Dict] = [
    {"nome": "Vinho Tinto Reserva Cabernet", "categoria": "Vinho Tinto", "preco": 89.90, "fornecedor": "Vinicola Serra Azul"},
    {"nome": "Vinho Tinto Merlot Classico", "categoria": "Vinho Tinto", "preco": 64.50, "fornecedor": "Casa do Vale Vinhos"},
    {"nome": "Vinho Tinto Malbec Premium", "categoria": "Vinho Tinto", "preco": 98.00, "fornecedor": "Andes Selection"},
    {"nome": "Vinho Branco Sauvignon Blanc", "categoria": "Vinho Branco", "preco": 72.40, "fornecedor": "Vinicola Serra Azul"},
    {"nome": "Vinho Branco Chardonnay", "categoria": "Vinho Branco", "preco": 78.90, "fornecedor": "Cantina Sol Nascente"},
    {"nome": "Vinho Rose Seco", "categoria": "Vinho Rose", "preco": 59.90, "fornecedor": "Casa do Vale Vinhos"},
    {"nome": "Espumante Brut Tradicional", "categoria": "Espumante", "preco": 84.90, "fornecedor": "Cantina Sol Nascente"},
    {"nome": "Espumante Moscatel", "categoria": "Espumante", "preco": 54.90, "fornecedor": "Cantina Sol Nascente"},
    {"nome": "Champagne Importado NV", "categoria": "Espumante", "preco": 249.90, "fornecedor": "Premium Beverage Import"},
    {"nome": "Whisky 12 Anos", "categoria": "Destilados", "preco": 189.00, "fornecedor": "Premium Beverage Import"},
    {"nome": "Whisky Blended", "categoria": "Destilados", "preco": 119.90, "fornecedor": "Distribuidora Norte Sul"},
    {"nome": "Gin London Dry", "categoria": "Destilados", "preco": 139.90, "fornecedor": "Distribuidora Norte Sul"},
    {"nome": "Vodka Premium", "categoria": "Destilados", "preco": 99.90, "fornecedor": "Distribuidora Norte Sul"},
    {"nome": "Rum Envelhecido", "categoria": "Destilados", "preco": 109.00, "fornecedor": "Premium Beverage Import"},
    {"nome": "Licor de Amaretto", "categoria": "Licores", "preco": 79.50, "fornecedor": "Cia de Licores Brasil"},
    {"nome": "Licor de Creme Irlandes", "categoria": "Licores", "preco": 94.00, "fornecedor": "Cia de Licores Brasil"},
    {"nome": "Cerveja Artesanal IPA 600ml", "categoria": "Cervejas", "preco": 19.90, "fornecedor": "Malte e Lupulo Co"},
    {"nome": "Cerveja Artesanal Weiss 600ml", "categoria": "Cervejas", "preco": 18.90, "fornecedor": "Malte e Lupulo Co"},
    {"nome": "Cerveja Stout Especial 600ml", "categoria": "Cervejas", "preco": 21.50, "fornecedor": "Malte e Lupulo Co"},
    {"nome": "Taca de Vinho Cristal", "categoria": "Acessorios", "preco": 29.90, "fornecedor": "Casa dos Acessorios Gourmet"},
    {"nome": "Saca-Rolhas Profissional", "categoria": "Acessorios", "preco": 49.90, "fornecedor": "Casa dos Acessorios Gourmet"},
    {"nome": "Decanter de Vidro", "categoria": "Acessorios", "preco": 119.90, "fornecedor": "Casa dos Acessorios Gourmet"},
    {"nome": "Kit Queijos Gourmet", "categoria": "Gourmet", "preco": 69.90, "fornecedor": "Emporio Central"},
    {"nome": "Kit Frios Selecionados", "categoria": "Gourmet", "preco": 89.90, "fornecedor": "Emporio Central"},
    {"nome": "Azeite Extra Virgem Premium", "categoria": "Gourmet", "preco": 45.90, "fornecedor": "Emporio Central"},
]


USUARIOS = ["ADM", "Operador1", "Operador2", "Gerente"]
OBSERVACOES_ENTRADA = [
    "Reposicao semanal",
    "Compra promocional",
    "Entrada de lote novo",
    "Ajuste de inventario",
    "Mercadoria recebida do fornecedor",
]
OBSERVACOES_SAIDA = [
    "Venda no balcao",
    "Venda para evento",
    "Pedido online",
    "Ajuste por avaria",
    "Baixa por degustacao",
]

USUARIOS_DEMO = [
    {"username": "ADM", "senha": "123qwe", "perfil": "ADM"},
    {"username": "Gerente", "senha": "123qwe", "perfil": "gerente"},
    {"username": "Operador1", "senha": "123qwe", "perfil": "operador"},
    {"username": "Operador2", "senha": "123qwe", "perfil": "operador"},
]


def limpar_base(db: EstoqueDB) -> None:
    """Remove todos os registros do banco para gerar uma base limpa."""
    with db.conexao:
        db.conexao.execute("DELETE FROM movimentacoes")
        db.conexao.execute("DELETE FROM produtos")


def gerar_usuarios_demo(db: EstoqueDB) -> int:
    """Gera usuários padrão para testes de perfil de acesso."""
    total = 0
    for item in USUARIOS_DEMO:
        senha_hash = db.gerar_hash_senha(item["senha"])

        if item["perfil"] == "ADM":
            # Mantem a regra de nunca ficar sem ADM e atualiza senha/perfil quando ja existir.
            if db.atualizar_usuario(
                username_original=item["username"],
                novo_perfil="ADM",
                nova_senha_hash=senha_hash,
                sistema=True,
            ):
                total += 1
                continue

        # Remove versões anteriores para manter senha/perfil previsíveis em demo
        db.deletar_usuario(item["username"], sistema=True)
        if db.criar_usuario(item["username"], senha_hash, item["perfil"], sistema=True):
            total += 1
    return total


def gerar_produtos(db: EstoqueDB, seed: int) -> List[str]:
    """Cria produtos de adega com quantidades e estoques minimos variados."""
    random.seed(seed)
    nomes_criados: List[str] = []

    for item in PRODUTOS_BASE:
        quantidade = random.randint(8, 70)
        estoque_minimo = random.randint(4, 18)
        ok = db.criar_produto(
            nome=item["nome"],
            categoria=item["categoria"],
            preco=item["preco"],
            quantidade=quantidade,
            estoque_minimo=estoque_minimo,
            fornecedor=item["fornecedor"],
        )
        if ok:
            nomes_criados.append(item["nome"])

    return nomes_criados


def gerar_movimentacoes(db: EstoqueDB, produtos: List[str], quantidade_movs: int, seed: int) -> int:
    """Gera historico de entradas e saidas em produtos existentes."""
    random.seed(seed + 100)
    total_ok = 0

    for _ in range(quantidade_movs):
        nome_produto = random.choice(produtos)
        tipo = random.choices(["entrada", "saida"], weights=[0.45, 0.55], k=1)[0]
        quantidade = random.randint(1, 12)
        usuario = random.choice(USUARIOS)
        observacao = random.choice(OBSERVACOES_ENTRADA if tipo == "entrada" else OBSERVACOES_SAIDA)

        if db.registrar_movimentacao(nome_produto, tipo, quantidade, observacao, usuario):
            total_ok += 1

    return total_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerador de dados de demonstracao para adega")
    parser.add_argument("--db", default="estoque.db", help="Arquivo do banco SQLite (padrao: estoque.db)")
    parser.add_argument("--seed", type=int, default=42, help="Seed para resultados repetiveis")
    parser.add_argument("--movimentacoes", type=int, default=120, help="Quantidade de movimentacoes para gerar")
    parser.add_argument("--limpar", action="store_true", help="Limpa produtos/movimentacoes antes de gerar")
    args = parser.parse_args()

    db = EstoqueDB(args.db)

    try:
        if args.limpar:
            limpar_base(db)
            print("🧹 Base limpa com sucesso")

        total_usuarios = gerar_usuarios_demo(db)

        produtos = gerar_produtos(db, args.seed)
        movs = gerar_movimentacoes(db, produtos, args.movimentacoes, args.seed)

        relatorio = db.relatorio_estoque()
        print("\n✅ Dados de demonstracao gerados")
        print(f"Usuarios demo criados: {total_usuarios}")
        print(f"Produtos criados: {len(produtos)}")
        print(f"Movimentacoes registradas: {movs}")
        print(f"Total de produtos no banco: {relatorio.get('total_produtos', 0)}")
        print(f"Total de movimentacoes no banco: {relatorio.get('total_movimentacoes', 0)}")
        print(f"Produtos criticos: {relatorio.get('produtos_criticos', 0)}")
    finally:
        db.fechar_conexao()


if __name__ == "__main__":
    main()
