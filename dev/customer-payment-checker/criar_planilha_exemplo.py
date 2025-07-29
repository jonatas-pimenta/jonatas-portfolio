"""
Customer Payment Checker - Gerador de Planilha de Exemplo
=========================================================

Este módulo cria uma planilha Excel com dados fictícios para demonstração
e teste do sistema de verificação de pagamentos.

Autor: Jonatas Pimenta
Data: 2024
Licença: MIT
"""

import openpyxl
import os
from datetime import datetime

def criar_planilha_exemplo():
    """
    Cria uma planilha de exemplo com dados fictícios para teste.
    
    A planilha criada contém:
    - 5 clientes fictícios com dados realistas
    - Estrutura compatível com o sistema principal
    - CPFs fictícios (não reais) para teste seguro
    
    Returns:
        str: Caminho do arquivo criado
    """
    
    print("🏗️  Criando planilha de exemplo...")
    
    # Configurar workspace path dinamicamente
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    
    # Criar nova planilha
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sheet1'
    
    # Adicionar cabeçalho com formatação
    headers = ["Nome", "Valor", "CPF", "Vencimento"]
    sheet.append(headers)
    
    # Formatar cabeçalho (negrito)
    for cell in sheet[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Dados de exemplo (CPFs fictícios e seguros para teste)
    dados_exemplo = [
        ["João Silva", 1500.00, "12345678901", "2024-01-15"],
        ["Maria Santos", 2300.50, "98765432100", "2024-01-20"],
        ["Carlos Oliveira", 850.75, "11122233344", "2024-01-25"],
        ["Ana Costa", 1200.00, "55566677788", "2024-02-01"],
        ["Pedro Souza", 950.25, "99988877766", "2024-02-05"]
    ]
    
    # Adicionar dados à planilha
    for linha in dados_exemplo:
        sheet.append(linha)
    
    # Ajustar largura das colunas automaticamente
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Salvar planilha
    caminho = os.path.join(workspace_path, "dados_clientes_exemplo.xlsx")
    workbook.save(caminho)
    
    print(f"✅ Planilha de exemplo criada em: {caminho}")
    print(f"📊 Clientes de exemplo: {len(dados_exemplo)}")
    print("💡 Renomeie para 'dados_clientes.xlsx' para usar no programa principal")
    print("⚠️  IMPORTANTE: CPFs são fictícios e seguros para teste")
    
    return caminho

def validar_estrutura_planilha(caminho_planilha):
    """
    Valida se a planilha tem a estrutura correta.
    
    Args:
        caminho_planilha (str): Caminho para a planilha a ser validada
        
    Returns:
        bool: True se a estrutura estiver correta
    """
    try:
        workbook = openpyxl.load_workbook(caminho_planilha)
        sheet = workbook.active
        
        # Verificar cabeçalhos esperados
        headers_esperados = ["Nome", "Valor", "CPF", "Vencimento"]
        headers_planilha = [cell.value for cell in sheet[1]]
        
        return headers_planilha == headers_esperados
    except Exception as e:
        print(f"❌ Erro ao validar planilha: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Customer Payment Checker - Gerador de Planilha")
    print("=" * 50)
    print()
    
    # Verificar se já existe planilha de exemplo
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    caminho_exemplo = os.path.join(workspace_path, "dados_clientes_exemplo.xlsx")
    
    if os.path.exists(caminho_exemplo):
        print("⚠️  Planilha de exemplo já existe!")
        resposta = input("Deseja sobrescrever? (s/n): ").lower().strip()
        if resposta != 's':
            print("❌ Operação cancelada.")
            exit(0)
    
    # Criar planilha
    caminho_criado = criar_planilha_exemplo()
    
    # Validar estrutura
    if validar_estrutura_planilha(caminho_criado):
        print("✅ Estrutura da planilha validada com sucesso!")
    else:
        print("⚠️  Aviso: Estrutura da planilha pode ter problemas")
    
    print()
    print("🎯 Próximos passos:")
    print("1. Renomeie para 'dados_clientes.xlsx' ou use como exemplo")
    print("2. Execute './executar.sh' para iniciar o sistema")
    print("3. Execute './teste_rapido.sh' para teste automático")
