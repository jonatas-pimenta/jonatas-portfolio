#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Estoque com MongoDB
Módulo de Banco de Dados - Lógica de Negócio
"""

from pymongo import MongoClient
import datetime
import pandas as pd
from typing import List, Dict, Optional

class EstoqueDB:
    """Classe para gerenciar operações do banco de dados MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        """
        Inicializa a conexão com MongoDB
        
        Args:
            connection_string (str): String de conexão do MongoDB
        """
        try:
            self.cliente = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Testa a conexão
            self.cliente.admin.command('ping')
            print("✅ Conexão com MongoDB estabelecida")
            
            # Seleciona o banco de dados
            self.banco = self.cliente["Controle_de_Estoque"]
            
            # Define as coleções
            self.produtos = self.banco["produtos"]
            self.movimentacoes = self.banco["movimentacoes"]
            
        except Exception as e:
            print(f"❌ Erro na conexão com MongoDB: {e}")
            raise
    
    def criar_produto(self, nome: str, categoria: str, preco: float, 
                      quantidade: int, estoque_minimo: int, fornecedor: str) -> bool:
        """Cria um novo produto na adega"""
        try:
            # Verifica se produto já existe
            if self.produtos.find_one({"nome": nome}):
                print(f"❌ Produto '{nome}' já existe!")
                return False
            
            produto = {
                "nome": nome,
                "categoria": categoria,
                "preco": float(preco),
                "quantidade": int(quantidade),
                "estoque_minimo": int(estoque_minimo),
                "fornecedor": fornecedor,
                "data_cadastro": datetime.datetime.now()
            }
            
            resultado = self.produtos.insert_one(produto)
            print(f"✅ Produto '{nome}' adicionado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar produto: {e}")
            return False
    
    def listar_produtos(self) -> List[Dict]:
        """Lista todos os produtos"""
        try:
            return list(self.produtos.find())
        except Exception as e:
            print(f"❌ Erro ao listar produtos: {e}")
            return []
    
    def buscar_produto(self, nome: str) -> Optional[Dict]:
        """Busca um produto pelo nome"""
        try:
            return self.produtos.find_one({"nome": nome})
        except Exception as e:
            print(f"❌ Erro ao buscar produto: {e}")
            return None
    
    def buscar_produtos_filtrados(self, filtro_por: str, termo_pesquisa: str) -> List[Dict]:
        """Busca produtos com base em um filtro e termo de pesquisa (case-insensitive)."""
        try:
            if not termo_pesquisa:
                return self.listar_produtos()
            
            # Usando regex para busca case-insensitive e parcial
            query = {filtro_por: {"$regex": termo_pesquisa, "$options": "i"}}
            return list(self.produtos.find(query))
        except Exception as e:
            print(f"❌ Erro ao buscar produtos filtrados: {e}")
            return []

    def atualizar_produto(self, nome: str, dados: Dict) -> bool:
        """Atualiza dados de um produto"""
        try:
            resultado = self.produtos.update_one(
                {"nome": nome},
                {"$set": dados}
            )
            
            if resultado.matched_count > 0:
                print(f"✅ Produto '{nome}' atualizado!")
                return True
            else:
                print(f"❌ Produto '{nome}' não encontrado!")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar produto: {e}")
            return False
    
    def deletar_produto(self, nome: str) -> bool:
        """Deleta um produto"""
        try:
            resultado = self.produtos.delete_one({"nome": nome})
            
            if resultado.deleted_count > 0:
                print(f"✅ Produto '{nome}' deletado!")
                return True
            else:
                print(f"❌ Produto '{nome}' não encontrado!")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar produto: {e}")
            return False
    
    def registrar_movimentacao(self, nome_produto: str, tipo_movimento: str, 
                              quantidade: int, observacao: str = "", usuario: str = "Sistema") -> bool:
        """Registra uma movimentação de estoque"""
        try:
            # Busca o produto
            produto = self.produtos.find_one({"nome": nome_produto})
            
            if not produto:
                print(f"❌ Produto '{nome_produto}' não encontrado!")
                return False
            
            # Verifica estoque para saídas
            if tipo_movimento.lower() == 'saida' and produto['quantidade'] < quantidade:
                print(f"❌ Estoque insuficiente! Disponível: {produto['quantidade']}, Solicitado: {quantidade}")
                return False
            
            # Registra a movimentação
            movimentacao = {
                "produto_id": produto["_id"],
                "produto_nome": nome_produto,
                "tipo": tipo_movimento.lower(),
                "quantidade": quantidade,
                "data_movimentacao": datetime.datetime.now(),
                "observacao": observacao,
                "usuario": usuario
            }
            
            self.movimentacoes.insert_one(movimentacao)
            
            # Atualiza estoque
            if tipo_movimento.lower() == 'entrada':
                nova_quantidade = produto['quantidade'] + quantidade
            else:
                nova_quantidade = produto['quantidade'] - quantidade
            
            self.produtos.update_one(
                {"_id": produto["_id"]},
                {"$set": {"quantidade": nova_quantidade}}
            )
            
            print(f"✅ Movimentação registrada: {tipo_movimento} de {quantidade} unidades")
            
            # Verifica alerta de estoque baixo
            if nova_quantidade <= produto['estoque_minimo']:
                print(f"⚠️ ALERTA: Estoque baixo para '{nome_produto}'!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao registrar movimentação: {e}")
            return False
    
    def listar_movimentacoes(self, limite: int = 50) -> List[Dict]:
        """Lista as movimentações mais recentes"""
        try:
            return list(self.movimentacoes.find().sort("data_movimentacao", -1).limit(limite))
        except Exception as e:
            print(f"❌ Erro ao listar movimentações: {e}")
            return []
    
    def produtos_em_falta(self) -> List[Dict]:
        """Lista produtos com estoque baixo ou em falta"""
        try:
            return list(self.produtos.find({
                "$expr": {"$lte": ["$quantidade", "$estoque_minimo"]}
            }))
        except Exception as e:
            print(f"❌ Erro ao buscar produtos em falta: {e}")
            return []
    
    def relatorio_estoque(self) -> Dict:
        """Gera relatório geral do estoque"""
        try:
            total_produtos = self.produtos.count_documents({})
            
            # Aggregation pipeline para calcular totais
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "valor_total": {"$sum": {"$multiply": ["$preco", "$quantidade"]}},
                        "quantidade_total": {"$sum": "$quantidade"}
                    }
                }
            ]
            
            resultado = list(self.produtos.aggregate(pipeline))
            valor_total = resultado[0]['valor_total'] if resultado else 0
            quantidade_total = resultado[0]['quantidade_total'] if resultado else 0
            
            produtos_criticos = len(self.produtos_em_falta())
            total_movimentacoes = self.movimentacoes.count_documents({})
            
            return {
                'total_produtos': total_produtos,
                'valor_total': valor_total,
                'quantidade_total': quantidade_total,
                'produtos_criticos': produtos_criticos,
                'total_movimentacoes': total_movimentacoes
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            return {}
    
    def exportar_para_excel(self, caminho_arquivo: str) -> bool:
        """Exporta os dados do inventário e produtos críticos para um arquivo Excel."""
        try:
            # Busca os dados
            produtos = self.listar_produtos()
            produtos_criticos = self.produtos_em_falta()

            # Formata datas e remove o _id para não aparecer na planilha
            for p in produtos:
                if 'data_cadastro' in p and isinstance(p['data_cadastro'], datetime.datetime):
                    p['data_cadastro'] = p['data_cadastro'].strftime("%d/%m/%Y %H:%M:%S")
                p.pop('_id', None)

            for p in produtos_criticos: p.pop('_id', None)

            # Cria DataFrames do Pandas
            df_produtos = pd.DataFrame(produtos)
            df_criticos = pd.DataFrame(produtos_criticos)

            # Cria o arquivo Excel com duas abas (sheets)
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                df_produtos.to_excel(writer, sheet_name='Inventário Completo', index=False)
                
                # Apenas cria a aba de críticos se houver produtos nessa condição
                if not df_criticos.empty:
                    df_criticos.to_excel(writer, sheet_name='Produtos Críticos', index=False)

            print(f"✅ Relatório exportado para {caminho_arquivo}")
            return True

        except Exception as e:
            print(f"❌ Erro ao exportar para Excel: {e}")
            return False


    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if hasattr(self, 'cliente'):
            self.cliente.close()
            print("🔌 Conexão com MongoDB fechada")

# Teste básico da classe
if __name__ == "__main__":
    # Testa a conexão e funcionalidades básicas
    try:
        db = EstoqueDB()
        
        # Testa criação de produto
        print("\n🧪 Testando funcionalidades...")
        
        print("\n📦 Listando produtos:")
        produtos = db.listar_produtos()
        for produto in produtos:
            print(f"  • {produto['nome']} - Estoque: {produto['quantidade']}")
        
        print(f"\n📊 Relatório:")
        relatorio = db.relatorio_estoque()
        for chave, valor in relatorio.items():
            print(f"  • {chave}: {valor}")
        
        db.fechar_conexao()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
