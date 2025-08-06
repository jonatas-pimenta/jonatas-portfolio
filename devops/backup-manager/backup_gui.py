import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.filedialog as filedialog
import subprocess
import os
import threading
from datetime import datetime

import tkinter.filedialog
print("filedialog path:", tkinter.filedialog.__file__)

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        # Definir caminho do arquivo de histórico
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_history.log")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='white', font=('Segoe UI', 10))
        self.style.configure('TRadiobutton', background='#2b2b2b', foreground='white', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), borderwidth=0)
        self.style.map('TButton',
                      foreground=[('pressed', 'white'), ('active', 'white')],
                      background=[('pressed', '!disabled', '#3a3a3a'), ('active', '#4a4a4a')])
        
        # Frame principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        self.title_label = ttk.Label(self.main_frame, text="BACKUP MANAGER", font=('Segoe UI', 16, 'bold'))
        self.title_label.pack(pady=(0, 20))
        
        # Frame de seleção de tipo
        self.type_frame = ttk.Frame(self.main_frame)
        self.type_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.backup_type = tk.StringVar(value="folder")
        ttk.Label(self.type_frame, text="Backup Type:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(self.type_frame, text="Folder", variable=self.backup_type, value="folder").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(self.type_frame, text="File", variable=self.backup_type, value="file").pack(side=tk.LEFT)
        
        # Frame de origem
        self.source_frame = ttk.Frame(self.main_frame)
        self.source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_path = tk.StringVar()
        ttk.Label(self.source_frame, text="Source:").pack(side=tk.LEFT)
        self.source_entry = ttk.Entry(self.source_frame, textvariable=self.source_path, width=50)
        self.source_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        self.source_button = ttk.Button(self.source_frame, text="Browse", command=self.browse_source, style='TButton')
        self.source_button.pack(side=tk.LEFT)
        
        # Frame de destino
        self.dest_frame = ttk.Frame(self.main_frame)
        self.dest_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.dest_path = tk.StringVar()
        ttk.Label(self.dest_frame, text="Destination:").pack(side=tk.LEFT)
        self.dest_entry = ttk.Entry(self.dest_frame, textvariable=self.dest_path, width=50)
        self.dest_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        self.dest_button = ttk.Button(self.dest_frame, text="Browse", command=self.browse_dest, style='TButton')
        self.dest_button.pack(side=tk.LEFT)
        
        # Frame de botões
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=(0, 20))
        
        # Botão de execução
        self.run_button = ttk.Button(self.button_frame, text="Run Backup", command=self.run_backup, style='Accent.TButton')
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão para limpar log (protegido por senha)
        self.clear_button = ttk.Button(self.button_frame, text="🔒 Clear Log", command=self.clear_log, style='Warning.TButton')
        self.clear_button.pack(side=tk.LEFT)
        
        # Área de log
        self.log_label = ttk.Label(self.main_frame, text="Backup History & Log:")
        self.log_label.pack(anchor=tk.W)
        
        self.log_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg="black",
            fg="#4CAF50",
            insertbackground="white",
            font=('Consolas', 10),
            state=tk.NORMAL
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Configurar botões com estilos especiais
        self.style.configure('Accent.TButton', foreground='white', background='#4CAF50')
        self.style.map('Accent.TButton',
                     background=[('pressed', '!disabled', '#3d8b40'), ('active', '#5CBF60')])
        
        # Estilo para botão de limpeza (laranja/aviso)
        self.style.configure('Warning.TButton', foreground='white', background='#FF9800')
        self.style.map('Warning.TButton',
                     background=[('pressed', '!disabled', '#E68900'), ('active', '#FFB74D')])
        
        # Separador
        self.separator = ttk.Separator(self.main_frame, orient='horizontal')
        self.separator.pack(fill=tk.X, pady=10)
        
        # Rodapé
        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill=tk.X)
        
        ttk.Label(self.footer_frame, text="Backup Manager v1.1", foreground="gray").pack(side=tk.LEFT)
        ttk.Label(self.footer_frame, text="© 2025 Your Company", foreground="gray").pack(side=tk.RIGHT)
        
        # Carregar histórico de backups ao inicializar
        self.load_history_log()
    
    def browse_source(self):
        if self.backup_type.get() == "folder":
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
        
        if path:
            self.source_path.set(path)
    
    def browse_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path.set(path)
    
    def clear_log(self):
        """Limpa apenas a área de log visual, mas mantém o histórico no arquivo"""
        # Solicitar senha para limpeza
        password = self.ask_password()
        if password == "1234":
            self.log_area.delete(1.0, tk.END)
            self.log_to_screen("Log visual limpo. Histórico mantido em arquivo.\n")
            self.log_security_event(f"Log limpo com sucesso - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        elif password is not None:  # Se não cancelou
            messagebox.showerror("Acesso Negado", "Senha incorreta! Não foi possível limpar o log.")
            self.log_security_event(f"Tentativa de acesso negada - senha incorreta - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    def ask_password(self):
        """Janela para solicitar senha"""
        password_window = tk.Toplevel(self.root)
        password_window.title("Autenticação Necessária")
        password_window.geometry("300x150")
        password_window.configure(bg="#2b2b2b")
        password_window.resizable(False, False)
        
        # Centralizar janela
        password_window.transient(self.root)
        password_window.grab_set()
        
        # Configurar estilo para a janela de senha
        style = ttk.Style()
        style.configure('Password.TLabel', background='#2b2b2b', foreground='white', font=('Segoe UI', 10))
        style.configure('Password.TButton', font=('Segoe UI', 9))
        
        # Frame principal
        main_frame = ttk.Frame(password_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔒 Área Restrita", 
                               font=('Segoe UI', 12, 'bold'), style='Password.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Instrução
        info_label = ttk.Label(main_frame, text="Digite a senha para limpar o log:", 
                              style='Password.TLabel')
        info_label.pack(pady=(0, 10))
        
        # Campo de senha
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, 
                                  show="*", width=20, font=('Segoe UI', 10))
        password_entry.pack(pady=(0, 15))
        password_entry.focus()
        
        # Variável para armazenar resultado
        result = {'password': None}
        
        def on_ok():
            result['password'] = password_var.get()
            password_window.destroy()
        
        def on_cancel():
            result['password'] = None
            password_window.destroy()
        
        def on_enter(event):
            on_ok()
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ok_button = ttk.Button(button_frame, text="OK", command=on_ok, style='Password.TButton')
        ok_button.pack(side=tk.LEFT, padx=(0, 5))
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=on_cancel, style='Password.TButton')
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key
        password_entry.bind('<Return>', on_enter)
        password_window.bind('<Escape>', lambda e: on_cancel())
        
        # Aguardar fechamento da janela
        password_window.wait_window()
        
        return result['password']
    
    def log_to_screen(self, message):
        """Adiciona mensagem apenas na tela"""
        self.log_area.insert(tk.END, message)
        self.log_area.see(tk.END)
        self.root.update_idletasks()
    
    def log_to_file(self, message):
        """Salva mensagem no arquivo de histórico"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        except Exception as e:
            self.log_to_screen(f"Erro ao salvar no histórico: {e}\n")
    
    def log(self, message):
        """Adiciona mensagem tanto na tela quanto no arquivo"""
        # Adicionar na tela
        self.log_to_screen(message + "\n")
        # Salvar no arquivo (sem timestamp duplicado se já tiver)
        if not message.startswith("20"):  # Se não começar com ano, adicionar timestamp
            self.log_to_file(message)
        else:
            # Se já tem timestamp, salvar sem adicionar outro
            try:
                with open(self.history_file, 'a', encoding='utf-8') as f:
                    f.write(f"{message}\n")
            except Exception as e:
                self.log_to_screen(f"Erro ao salvar no histórico: {e}\n")
    
    def log_security_event(self, event):
        """Log especial para eventos de segurança"""
        security_msg = f"[SEGURANÇA] {event}"
        self.log_to_file(security_msg)
        self.log_to_screen(f"🔒 {event}\n")
    
    def run_backup(self):
        source = self.source_path.get()
        dest = self.dest_path.get()
        
        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination paths")
            return
        
        # Não limpar o log, apenas adicionar nova sessão
        self.log("\n" + "="*60)
        self.log("NOVA SESSÃO DE BACKUP INICIADA")
        self.log(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log(f"Origem: {source}")
        self.log(f"Destino: {dest}")
        self.log(f"Tipo: {'Pasta' if self.backup_type.get() == 'folder' else 'Arquivo'}")
        self.log("="*60)
        self.log("Iniciando processo de backup...")
        
        # Executar em uma thread separada para não travar a interface
        threading.Thread(target=self.execute_backup, args=(source, dest), daemon=True).start()
    
    def execute_backup(self, source, dest):
        backup_type = self.backup_type.get()
        
        try:
            if backup_type == "folder":
                self.log("Executando backup de pasta usando backup_engine.sh...")
                
                # Verificar se o script existe
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_engine.sh")
                if not os.path.exists(script_path):
                    self.log(f"ERRO: backup_engine.sh não encontrado em {script_path}")
                    return
                
                # Executar o script
                process = subprocess.Popen(
                    ["bash", script_path, source, dest],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True
                )
                
                # Ler saída em tempo real
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.log(output.strip())
                
                # Verificar se houve erro
                return_code = process.poll()
                if return_code != 0:
                    error = process.stderr.read()
                    self.log(f"ERRO: {error}")
                    self.log("BACKUP FALHOU!")
                else:
                    self.log("BACKUP DE PASTA CONCLUÍDO COM SUCESSO!")
            
            else:  # backup de arquivo
                self.log(f"Executando backup de arquivo usando rsync...")
                self.log(f"Copiando de {source} para {dest}...")
                
                process = subprocess.Popen(
                    ["rsync", "-avh", "--progress", source, dest + "/"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True
                )
                
                # Ler saída em tempo real
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.log(output.strip())
                
                # Verificar se houve erro
                return_code = process.poll()
                if return_code != 0:
                    error = process.stderr.read()
                    self.log(f"ERRO: {error}")
                    self.log("BACKUP FALHOU!")
                else:
                    self.log("BACKUP DE ARQUIVO CONCLUÍDO COM SUCESSO!")
                    
        except Exception as e:
            self.log(f"ERRO INESPERADO: {str(e)}")
        
        finally:
            self.log(f"Sessão finalizada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            self.log("="*60 + "\n")
    
    def load_history_log(self):
        """Carrega o histórico completo de backups"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        self.log_area.delete(1.0, tk.END)
                        self.log_area.insert(1.0, content)
                        self.log_area.insert(tk.END, "\n--- HISTÓRICO CARREGADO ---\n")
                        self.log_area.see(tk.END)
                    else:
                        self.log_to_screen("Nenhum histórico encontrado. Pronto para novos backups.\n")
            else:
                # Criar arquivo de histórico se não existir
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Histórico de Backups - Criado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                self.log_to_screen("Arquivo de histórico criado. Pronto para novos backups.\n")
                
        except Exception as e:
            self.log_to_screen(f"Erro ao carregar histórico: {e}\n")
            self.log_to_screen("Iniciando com histórico vazio.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()