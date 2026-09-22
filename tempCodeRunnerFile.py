import customtkinter as ctk
import importlib
import os
from PIL import Image, ImageOps


from database import engine, Base
import models
Base.metadata.create_all(bind=engine)
from controllers import CarroController


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COR_FUNDO = "#09090B"         
COR_MENU = "#18181B"          
COR_BOTAO_ATIVO = "#2563EB"   
COR_HOVER_MENU = "#27272A"    

class GLVApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão Corporativa - TNE / GLV Táxi")
        self.geometry("1280x760") 
        self.configure(fg_color=COR_FUNDO)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.controller = CarroController()

        self.fonte_titulo = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.fonte_menu = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.botoes_menu = {}

        self.criar_menu_lateral()
        self.main_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#131316") 
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.carregar_tela("tela_dashboard")
        self.atualizar_sino()

    def criar_menu_lateral(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COR_MENU)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar.grid_rowconfigure(9, weight=1) 

        caminho_logo = "logo.png" if os.path.exists("logo.png") else "logo.jpg" if os.path.exists("logo.jpg") else None
        
        if caminho_logo:
            try:
                img_original = Image.open(caminho_logo)
                img_logo = ctk.CTkImage(light_image=img_original, dark_image=img_original, size=(240, 150))
                ctk.CTkLabel(self.sidebar, image=img_logo, text="").grid(row=0, column=0, padx=20, pady=(25, 10))
            except Exception as e:
                ctk.CTkLabel(self.sidebar, text="GLV TÁXI", font=self.fonte_titulo, text_color="#FFFFFF").grid(row=0, column=0, padx=20, pady=(35, 10))
        else:
            ctk.CTkLabel(self.sidebar, text="GLV TÁXI", font=self.fonte_titulo, text_color="#FFFFFF").grid(row=0, column=0, padx=20, pady=(35, 10))
        
        self.btn_sino = ctk.CTkButton(self.sidebar, text="🔔 Alertas (0)", font=self.fonte_menu, fg_color="#3F3F46", hover_color="#52525B", command=self.mostrar_alertas)
        self.btn_sino.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        abas = [
            ("📊  Painel Executivo", "tela_dashboard"), 
            ("🚗  Frota e Vendas", "tela_frota"), 
            ("👥  Motoristas", "tela_motoristas"), 
            ("🔑  Locações", "tela_locacoes"), 
            ("📄  Alvarás Oficiais", "tela_alvaras"), 
            ("💰  Fluxo de Caixa", "tela_caixa"),
            ("🛑  Multas e Débitos", "tela_multas")
        ]
        
        for idx, (txt, modulo) in enumerate(abas):
            btn = ctk.CTkButton(
                self.sidebar, text=txt, font=self.fonte_menu, anchor="w", height=45, corner_radius=8,
                fg_color="transparent", hover_color=COR_HOVER_MENU, text_color="#A1A1AA",
                command=lambda m=modulo: self.carregar_tela(m)
            )
            btn.grid(row=idx+2, column=0, padx=15, pady=6, sticky="ew")
            self.botoes_menu[modulo] = btn


        btn_config = ctk.CTkButton(
            self.sidebar, text="⚙️  Configurações", font=self.fonte_menu, anchor="w", height=45, corner_radius=8,
            fg_color="transparent", hover_color=COR_HOVER_MENU, text_color="#A1A1AA",
            command=lambda: self.carregar_tela("tela_configuracoes")
        )
        btn_config.grid(row=10, column=0, padx=15, pady=(10, 25), sticky="ew")
        self.botoes_menu["tela_configuracoes"] = btn_config

    def atualizar_sino(self):
        alertas = self.controller.obter_alertas()
        if alertas:
            self.btn_sino.configure(text=f"🔔 Alertas ({len(alertas)})", fg_color="#EF4444", hover_color="#DC2626")
        else:
            self.btn_sino.configure(text="🔔 Tudo OK", fg_color="#10B981", hover_color="#059669")

    def mostrar_alertas(self):
        alertas = self.controller.obter_alertas()
        win = ctk.CTkToplevel(self)
        win.title("Central de Alertas")
        win.geometry("480x450")
        win.attributes("-topmost", True)
        win.configure(fg_color=COR_FUNDO)
        
        ctk.CTkLabel(win, text="Pendências da Frota", font=self.fonte_titulo).pack(pady=20)
        
        sc = ctk.CTkScrollableFrame(win, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=15, pady=10)
        
        if not alertas:
            ctk.CTkLabel(sc, text="Nenhum alerta pendente! Frota e documentos em dia.", text_color="#10B981", font=ctk.CTkFont(size=14)).pack(pady=20)
        else:
            for aviso in alertas:
                cor_aviso = "#F59E0B" if "óleo" in aviso.lower() else "#EF4444"
                card_aviso = ctk.CTkFrame(sc, fg_color="#18181B", corner_radius=8)
                card_aviso.pack(fill="x", pady=5)
                ctk.CTkLabel(card_aviso, text=aviso, font=ctk.CTkFont(size=14, weight="bold"), text_color=cor_aviso, wraplength=400, justify="left").pack(anchor="w", padx=15, pady=15)

    def carregar_tela(self, nome_modulo):
        for widget in self.main_frame.winfo_children(): widget.destroy()

        for mod, btn in self.botoes_menu.items():
            if mod == nome_modulo: btn.configure(fg_color=COR_BOTAO_ATIVO, text_color="#FFFFFF", hover_color=COR_BOTAO_ATIVO)
            else: btn.configure(fg_color="transparent", text_color="#A1A1AA", hover_color=COR_HOVER_MENU)

        self.atualizar_sino()

        try:
            modulo = importlib.import_module(nome_modulo)
            importlib.reload(modulo) 
            modulo.renderizar(self.main_frame, self.controller, self)
        except ModuleNotFoundError:
            ctk.CTkLabel(self.main_frame, text=f"⚠️ O Módulo '{nome_modulo}' falhou.", text_color="#EF4444", font=self.fonte_titulo).pack(pady=100)

    def mascara_data_geral(self, event):
        entry = event.widget
        if event.keysym in ("BackSpace", "Delete"): return
        numeros = "".join(filter(str.isdigit, entry.get()))[:8]
        formatado = "".join([d + ("/" if i in (1, 3) else "") for i, d in enumerate(numeros)])
        entry.delete(0, "end"); entry.insert(0, formatado)

if __name__ == "__main__":
    app = GLVApp()
    app.mainloop()