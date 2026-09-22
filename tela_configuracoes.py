import customtkinter as ctk
from tkinter import messagebox, filedialog
import shutil
import os

def renderizar(frame_pai, controller, app):
    COR_CARD = "#18181B"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)


    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(30, 20))
    ctk.CTkLabel(top, text="Configurações do Sistema", font=FONT_TITULO).pack(side="left")

    container = ctk.CTkFrame(frame_pai, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=30)

    # ==========================================
    # LÓGICA DE BACKUP E RESTAURAÇÃO
    # ==========================================
    nome_bd_padrao = "glvf.db"

    def exportar_dados():
        if not os.path.exists(nome_bd_padrao):
            return messagebox.showerror("Erro", "Banco de dados não encontrado no diretório atual.")
            
        destino = filedialog.asksaveasfilename(
            defaultextension=".db", 
            initialfile="glvf_backup.db", 
            title="Salvar Cópia de Segurança", 
            filetypes=[("Banco de Dados SQLite", "*.db")]
        )
        
        if destino:
            try:
                shutil.copy2(nome_bd_padrao, destino)
                messagebox.showinfo("Sucesso", "Backup do banco de dados concluído com segurança!")
            except Exception as e:
                messagebox.showerror("Falha Crítica", f"Não foi possível criar a cópia de segurança:\n\n{e}")

    def importar_dados():
        origem = filedialog.askopenfilename(
            title="Selecionar Arquivo de Restauração", 
            filetypes=[("Banco de Dados SQLite", "*.db")]
        )
        
        if origem:
            aviso = "ATENÇÃO!\n\nIsso substituirá TODOS os dados atuais do sistema pelos dados contidos no arquivo selecionado. Esta ação não pode ser desfeita.\n\nDeseja realmente prosseguir com a restauração?"
            resposta = messagebox.askyesno("Confirmação de Segurança", aviso)
            
            if resposta:
                try:
                    shutil.copy2(origem, nome_bd_padrao)
                    messagebox.showinfo("Restauração Concluída", "Banco de dados atualizado com sucesso!\n\nO sistema será encerrado automaticamente para aplicar as alterações. Abra-o novamente em seguida.")
                    app.quit()
                except Exception as e:
                    messagebox.showerror("Falha Crítica", f"Ocorreu um erro durante a restauração:\n\n{e}")


    card_backup = ctk.CTkFrame(container, fg_color=COR_CARD, corner_radius=12)
    card_backup.pack(fill="x", pady=15)
    
    info_backup = ctk.CTkFrame(card_backup, fg_color="transparent")
    info_backup.pack(side="left", padx=25, pady=25, fill="both", expand=True)
    
    ctk.CTkLabel(info_backup, text="Exportar Banco de Dados (Backup)", font=FONT_CARD_TIT, text_color="#10B981").pack(anchor="w")
    ctk.CTkLabel(info_backup, text="Guarde uma cópia de segurança de toda a frota, locações e financeiro no seu computador, Google Drive ou pen drive. Ideal para auditorias ou partilha de dados.", text_color=COR_TEXTO_SEC, font=FONT_TXT, wraplength=700, justify="left").pack(anchor="w", pady=(8, 0))
    
    ctk.CTkButton(card_backup, text="⬇️  Fazer Backup do Sistema", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), height=40, width=220, command=exportar_dados).pack(side="right", padx=25)

    card_restore = ctk.CTkFrame(container, fg_color=COR_CARD, corner_radius=12)
    card_restore.pack(fill="x", pady=15)
    
    info_restore = ctk.CTkFrame(card_restore, fg_color="transparent")
    info_restore.pack(side="left", padx=25, pady=25, fill="both", expand=True)
    
    ctk.CTkLabel(info_restore, text="Importar Banco de Dados (Restauração)", font=FONT_CARD_TIT, text_color="#EF4444").pack(anchor="w")
    ctk.CTkLabel(info_restore, text="Carregue um arquivo de backup (.db) anterior. Aviso: Isto substituirá todos os registos que constam atualmente no sistema de forma irreversível.", text_color=COR_TEXTO_SEC, font=FONT_TXT, wraplength=700, justify="left").pack(anchor="w", pady=(8, 0))
    
    ctk.CTkButton(card_restore, text="⬆️  Carregar Backup Antigo", fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(weight="bold"), height=40, width=220, command=importar_dados).pack(side="right", padx=25)


    rodape_info = ctk.CTkFrame(container, fg_color="transparent")
    rodape_info.pack(fill="x", pady=30)
    ctk.CTkLabel(rodape_info, text="Recomenda-se realizar o backup da operação semanalmente para garantir a integridade do património da GLV Táxi.", text_color="#52525B", font=ctk.CTkFont(size=12, slant="italic")).pack()