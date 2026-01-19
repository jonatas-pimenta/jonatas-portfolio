#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Estoque com MongoDB
Interface Gráfica com Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from db import EstoqueDB

class EstoqueGUI:
    """Interface gráfica principal do sistema de estoque"""
    
    def __init__(self):
        """Inicializa a interface gráfica"""
        
        # Conecta ao banco de dados
        try:
            self.db = EstoqueDB()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", 
                               f"Não foi possível conectar ao MongoDB:\n{e}\n\n"
                               "Verifique se o MongoDB está rodando:\n"
                               "sudo systemctl start mongod")
            return
        
        # Cria a janela principal
        self.root = tk.Tk()
        self.root.title("StockFlow – Fluxo Inteligente de Estoques")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configura o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Cria a interface
        self.criar_interface()
        
        # Atualiza a lista de produtos
        self.atualizar_lista_produtos()
    
    def criar_interface(self):
        """Cria todos os elementos da interface"""
        
        # Frame principal com notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Produtos
        self.frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_produtos, text="📦 Produtos")
        self.criar_aba_produtos()
        
        # Aba 2: Movimentações
        self.frame_movimentacoes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_movimentacoes, text="🔄 Movimentações")
        self.criar_aba_movimentacoes()
        
        # Aba 3: Relatórios
        self.frame_relatorios = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_relatorios, text="📊 Relatórios")
        self.criar_aba_relatorios()
        
        # Barra de status
        self.status_bar = tk.Label(self.root, text="Sistema iniciado", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg='#e0e0e0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def criar_aba_produtos(self):
        """Cria a aba de gerenciamento de produtos"""
        
        # Frame para formulário
        form_frame = ttk.LabelFrame(self.frame_produtos, text="Cadastro de Produtos")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Campos do formulário
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Categoria:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.entry_categoria = ttk.Entry(form_frame, width=20)
        self.entry_categoria.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Preço:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_preco = ttk.Entry(form_frame, width=15)
        self.entry_preco.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Quantidade:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.entry_quantidade = ttk.Entry(form_frame, width=10)
        self.entry_quantidade.grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Estoque Mínimo:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_estoque_min = ttk.Entry(form_frame, width=10)
        self.entry_estoque_min.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Fornecedor:").grid(row=2, column=2, sticky='w', padx=5, pady=2)
        self.entry_fornecedor = ttk.Entry(form_frame, width=25)
        self.entry_fornecedor.grid(row=2, column=3, padx=5, pady=2)
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Adicionar Produto", 
                  command=self.adicionar_produto).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Atualizar Produto", 
                  command=self.atualizar_produto).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Deletar Produto", 
                  command=self.deletar_produto).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", 
                  command=self.limpar_campos).pack(side='left', padx=5)
        
        # Frame para pesquisa
        search_frame = ttk.LabelFrame(self.frame_produtos, text="Pesquisar Produtos")
        search_frame.pack(fill='x', padx=5, pady=5)

        self.search_var = tk.StringVar(value="nome")
        ttk.Radiobutton(search_frame, text="Nome", variable=self.search_var, value="nome").pack(side='left', padx=(10, 5))
        ttk.Radiobutton(search_frame, text="Categoria", variable=self.search_var, value="categoria").pack(side='left', padx=5)

        self.entry_pesquisa = ttk.Entry(search_frame, width=40)
        self.entry_pesquisa.pack(side='left', fill='x', expand=True, padx=5)
        self.entry_pesquisa.bind("<Return>", self.pesquisar_produtos) # Bind Enter key

        ttk.Button(search_frame, text="Pesquisar", command=self.pesquisar_produtos).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Limpar", command=self.limpar_pesquisa).pack(side='left', padx=5)
        
        # Lista de produtos
        list_frame = ttk.LabelFrame(self.frame_produtos, text="Lista de Produtos")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para mostrar produtos
        colunas = ('Nome', 'Categoria', 'Preço', 'Quantidade', 'Est.Min', 'Fornecedor', 'Status')
        self.tree_produtos = ttk.Treeview(list_frame, columns=colunas, show='headings', height=15)
        
        # Configura as colunas
        for col in colunas:
            self.tree_produtos.heading(col, text=col)
            if col == 'Nome':
                self.tree_produtos.column(col, width=200)
            elif col == 'Preço':
                self.tree_produtos.column(col, width=80)
            elif col in ['Quantidade', 'Est.Min']:
                self.tree_produtos.column(col, width=70)
            else:
                self.tree_produtos.column(col, width=120)
        
        # Scrollbar para a treeview
        scrollbar_produtos = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar_produtos.set)
        
        self.tree_produtos.pack(side='left', fill='both', expand=True)
        scrollbar_produtos.pack(side='right', fill='y')
        
        # Bind para seleção de produto
        self.tree_produtos.bind('<<TreeviewSelect>>', self.on_produto_select)
    
    def criar_aba_movimentacoes(self):
        """Cria a aba de movimentações"""
        
        # Frame para entrada/saída
        mov_frame = ttk.LabelFrame(self.frame_movimentacoes, text="Registrar Movimentação")
        mov_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(mov_frame, text="Produto:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.combo_produto = ttk.Combobox(mov_frame, width=30, state='readonly')
        self.combo_produto.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(mov_frame, text="Tipo:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.combo_tipo = ttk.Combobox(mov_frame, values=['entrada', 'saida'], width=10, state='readonly')
        self.combo_tipo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(mov_frame, text="Quantidade:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_qtd_mov = ttk.Entry(mov_frame, width=10)
        self.entry_qtd_mov.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(mov_frame, text="Observação:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.entry_observacao = ttk.Entry(mov_frame, width=40)
        self.entry_observacao.grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Button(mov_frame, text="Registrar Movimentação", 
                  command=self.registrar_movimentacao).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Atualizar combo de produtos
        self.atualizar_combo_produtos()
        
        # Lista de movimentações
        hist_frame = ttk.LabelFrame(self.frame_movimentacoes, text="Histórico de Movimentações")
        hist_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para movimentações
        colunas_mov = ('Data', 'Produto', 'Tipo', 'Quantidade', 'Usuário', 'Observação')
        self.tree_movimentacoes = ttk.Treeview(hist_frame, columns=colunas_mov, show='headings', height=15)
        
        for col in colunas_mov:
            self.tree_movimentacoes.heading(col, text=col)
            if col == 'Data':
                self.tree_movimentacoes.column(col, width=150)
            elif col == 'Produto':
                self.tree_movimentacoes.column(col, width=200)
            elif col in ['Tipo', 'Quantidade']:
                self.tree_movimentacoes.column(col, width=80)
            else:
                self.tree_movimentacoes.column(col, width=120)
        
        scrollbar_mov = ttk.Scrollbar(hist_frame, orient='vertical', command=self.tree_movimentacoes.yview)
        self.tree_movimentacoes.configure(yscrollcommand=scrollbar_mov.set)
        
        self.tree_movimentacoes.pack(side='left', fill='both', expand=True)
        scrollbar_mov.pack(side='right', fill='y')
        
        # Atualizar movimentações
        self.atualizar_lista_movimentacoes()
    
    def criar_aba_relatorios(self):
        """Cria a aba de relatórios"""
        
        # Frame para estatísticas gerais
        stats_frame = ttk.LabelFrame(self.frame_relatorios, text="Estatísticas Gerais")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.label_stats = tk.Text(stats_frame, height=8, width=80, state='disabled')
        self.label_stats.pack(padx=10, pady=10)
        
        # Frame para produtos em falta
        falta_frame = ttk.LabelFrame(self.frame_relatorios, text="Produtos em Falta ou Estoque Baixo")
        falta_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        colunas_falta = ('Produto', 'Categoria', 'Estoque Atual', 'Estoque Mínimo', 'Necessário')
        self.tree_falta = ttk.Treeview(falta_frame, columns=colunas_falta, show='headings', height=10)
        
        for col in colunas_falta:
            self.tree_falta.heading(col, text=col)
            self.tree_falta.column(col, width=120)
        
        scrollbar_falta = ttk.Scrollbar(falta_frame, orient='vertical', command=self.tree_falta.yview)
        self.tree_falta.configure(yscrollcommand=scrollbar_falta.set)
        
        self.tree_falta.pack(side='left', fill='both', expand=True)
        scrollbar_falta.pack(side='right', fill='y')
        
        # Frame para botões de relatório
        btn_relatorio_frame = ttk.Frame(self.frame_relatorios)
        btn_relatorio_frame.pack(pady=10)

        # Botão para atualizar relatórios
        ttk.Button(btn_relatorio_frame, text="Atualizar Relatórios", 
                  command=self.atualizar_relatorios).pack(side='left', padx=5)
        ttk.Button(btn_relatorio_frame, text="Exportar para Excel",
                  command=self.exportar_para_excel).pack(side='left', padx=5)
        
        # Atualizar relatórios
        self.atualizar_relatorios()
    
    def adicionar_produto(self):
        """Adiciona um novo produto"""
        try:
            nome = self.entry_nome.get().strip()
            categoria = self.entry_categoria.get().strip()
            preco = float(self.entry_preco.get())
            quantidade = int(self.entry_quantidade.get())
            estoque_min = int(self.entry_estoque_min.get())
            fornecedor = self.entry_fornecedor.get().strip()
            
            if not all([nome, categoria, fornecedor]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return
            
            sucesso = self.db.criar_produto(nome, categoria, preco, quantidade, estoque_min, fornecedor)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado com sucesso!")
                self.limpar_campos()
                self.atualizar_lista_produtos()
                self.atualizar_combo_produtos()
                self.atualizar_status(f"Produto '{nome}' adicionado")
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")
    
    def atualizar_produto(self):
        """Atualiza um produto existente"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para atualizar!")
            return
        
        try:
            nome_original = self.tree_produtos.item(selecionado[0])['values'][0]
            
            dados = {}
            if self.entry_categoria.get().strip():
                dados['categoria'] = self.entry_categoria.get().strip()
            if self.entry_preco.get().strip():
                dados['preco'] = float(self.entry_preco.get())
            if self.entry_quantidade.get().strip():
                dados['quantidade'] = int(self.entry_quantidade.get())
            if self.entry_estoque_min.get().strip():
                dados['estoque_minimo'] = int(self.entry_estoque_min.get())
            if self.entry_fornecedor.get().strip():
                dados['fornecedor'] = self.entry_fornecedor.get().strip()
            
            if not dados:
                messagebox.showwarning("Aviso", "Nenhum campo foi alterado!")
                return
            
            sucesso = self.db.atualizar_produto(nome_original, dados)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{nome_original}' atualizado!")
                self.limpar_campos()
                self.atualizar_lista_produtos()
                self.atualizar_status(f"Produto '{nome_original}' atualizado")
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {e}")
    
    def deletar_produto(self):
        """Deleta um produto"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para deletar!")
            return
        
        nome = self.tree_produtos.item(selecionado[0])['values'][0]
        
        resposta = messagebox.askyesno("Confirmar", 
                                     f"Tem certeza que deseja deletar o produto '{nome}'?")
        
        if resposta:
            sucesso = self.db.deletar_produto(nome)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{nome}' deletado!")
                self.limpar_campos()
                self.atualizar_lista_produtos()
                self.atualizar_combo_produtos()
                self.atualizar_status(f"Produto '{nome}' deletado")
    
    def registrar_movimentacao(self):
        """Registra uma movimentação"""
        try:
            produto = self.combo_produto.get()
            tipo = self.combo_tipo.get()
            quantidade = int(self.entry_qtd_mov.get())
            observacao = self.entry_observacao.get().strip()
            
            if not all([produto, tipo]):
                messagebox.showerror("Erro", "Selecione produto e tipo de movimentação!")
                return
            
            sucesso = self.db.registrar_movimentacao(produto, tipo, quantidade, observacao, "Usuário GUI")
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"Movimentação registrada: {tipo} de {quantidade} unidades")
                self.entry_qtd_mov.delete(0, tk.END)
                self.entry_observacao.delete(0, tk.END)
                self.atualizar_lista_produtos()
                self.atualizar_lista_movimentacoes()
                self.atualizar_status(f"Movimentação registrada: {tipo} {quantidade} {produto}")
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar movimentação: {e}")
    
    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.entry_nome.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_estoque_min.delete(0, tk.END)
        self.entry_fornecedor.delete(0, tk.END)
    
    def on_produto_select(self, event):
        """Preenche formulário com dados do produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if selecionado:
            valores = self.tree_produtos.item(selecionado[0])['values']
            
            self.limpar_campos()
            self.entry_nome.insert(0, valores[0])  # Nome
            self.entry_categoria.insert(0, valores[1])  # Categoria
            self.entry_preco.insert(0, valores[2])  # Preço
            self.entry_quantidade.insert(0, valores[3])  # Quantidade
            self.entry_estoque_min.insert(0, valores[4])  # Est.Min
            self.entry_fornecedor.insert(0, valores[5])  # Fornecedor
    
    def pesquisar_produtos(self, event=None):
        """Filtra a lista de produtos com base na pesquisa."""
        filtro = self.search_var.get()
        termo = self.entry_pesquisa.get().strip()
        
        if not termo:
            self.atualizar_lista_produtos()
            return
            
        produtos_filtrados = self.db.buscar_produtos_filtrados(filtro, termo)
        self.atualizar_lista_produtos(produtos_filtrados)
        self.atualizar_status(f"{len(produtos_filtrados)} produtos encontrados para '{termo}'")

    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e reexibe todos os produtos."""
        self.entry_pesquisa.delete(0, tk.END)
        self.atualizar_lista_produtos()
        self.atualizar_status("Pesquisa limpa. Exibindo todos os produtos.")

    def atualizar_lista_produtos(self, produtos_para_exibir=None):
        """Atualiza a lista de produtos na interface.
        Se 'produtos_para_exibir' for fornecido, exibe essa lista.
        Caso contrário, busca todos os produtos do banco.
        """
        # Limpa a treeview
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        
        # Busca produtos do banco se nenhuma lista for fornecida
        produtos = produtos_para_exibir if produtos_para_exibir is not None else self.db.listar_produtos()
        
        for produto in produtos:
            # Determina status do estoque
            if produto['quantidade'] <= produto['estoque_minimo']:
                status = "🔴 CRÍTICO"
            elif produto['quantidade'] <= produto['estoque_minimo'] * 2:
                status = "🟡 BAIXO"
            else:
                status = "🟢 OK"
            
            self.tree_produtos.insert('', 'end', values=(
                produto['nome'],
                produto['categoria'],
                f"R$ {produto['preco']:.2f}",
                produto['quantidade'],
                produto['estoque_minimo'],
                produto['fornecedor'],
                status
            ))
    
    def atualizar_combo_produtos(self):
        """Atualiza o combo de produtos na aba de movimentações"""
        produtos = self.db.listar_produtos()
        nomes = [produto['nome'] for produto in produtos]
        self.combo_produto['values'] = nomes
    
    def atualizar_lista_movimentacoes(self):
        """Atualiza a lista de movimentações"""
        # Limpa a treeview
        for item in self.tree_movimentacoes.get_children():
            self.tree_movimentacoes.delete(item)
        
        # Busca movimentações do banco
        movimentacoes = self.db.listar_movimentacoes(100)
        
        for mov in movimentacoes:
            data_formatada = mov['data_movimentacao'].strftime("%d/%m/%Y %H:%M")
            tipo_emoji = "📈 Entrada" if mov['tipo'] == 'entrada' else "📉 Saída"
            
            self.tree_movimentacoes.insert('', 'end', values=(
                data_formatada,
                mov['produto_nome'],
                tipo_emoji,
                mov['quantidade'],
                mov['usuario'],
                mov['observacao']
            ))
    
    def atualizar_relatorios(self):
        """Atualiza os relatórios na aba de relatórios"""
        # Estatísticas gerais
        relatorio = self.db.relatorio_estoque()
        
        self.label_stats.config(state='normal')
        self.label_stats.delete(1.0, tk.END)
        
        stats_text = f"""📊 ESTATÍSTICAS GERAIS DO ESTOQUE

💼 Total de produtos cadastrados: {relatorio.get('total_produtos', 0)}
📦 Total de itens em estoque: {relatorio.get('quantidade_total', 0)}
💰 Valor total do estoque: R$ {relatorio.get('valor_total', 0):,.2f}
🔄 Total de movimentações: {relatorio.get('total_movimentacoes', 0)}
⚠️  Produtos em situação crítica: {relatorio.get('produtos_criticos', 0)}

📈 Valor médio por item: R$ {relatorio.get('valor_total', 0) / max(relatorio.get('quantidade_total', 1), 1):.2f}

Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        self.label_stats.insert(1.0, stats_text)
        self.label_stats.config(state='disabled')
        
        # Produtos em falta
        for item in self.tree_falta.get_children():
            self.tree_falta.delete(item)
        
        produtos_criticos = self.db.produtos_em_falta()
        
        for produto in produtos_criticos:
            necessario = max(produto['estoque_minimo'] - produto['quantidade'], 0)
            
            self.tree_falta.insert('', 'end', values=(
                produto['nome'],
                produto['categoria'],
                produto['quantidade'],
                produto['estoque_minimo'],
                necessario
            ))
    
    def exportar_para_excel(self):
        """Abre um diálogo para salvar o relatório em Excel."""
        try:
            # Sugere um nome de arquivo com a data atual
            default_filename = f"relatorio_estoque_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
            
            caminho_arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Salvar Relatório Excel"
            )

            if caminho_arquivo:
                sucesso = self.db.exportar_para_excel(caminho_arquivo)
                if sucesso:
                    messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{caminho_arquivo}")
                    self.atualizar_status("Relatório exportado para Excel")
                else:
                    messagebox.showerror("Erro", "Falha ao exportar o relatório para Excel.")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao exportar: {e}")

    def atualizar_status(self, mensagem):
        """Atualiza a barra de status"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"{timestamp} - {mensagem}")
    
    def on_closing(self):
        """Gerencia o fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja fechar o sistema?"):
            self.db.fechar_conexao()
            self.root.destroy()
    
    def executar(self):
        """Executa a aplicação"""
        self.atualizar_status("Sistema iniciado e pronto para uso")
        self.root.mainloop()

# Função principal
def main():
    """Função principal da aplicação"""
    try:
        app = EstoqueGUI()
        app.executar()
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        messagebox.showerror("Erro", f"Erro ao iniciar aplicação:\n{e}")

if __name__ == "__main__":
    main()
