import customtkinter as ctk
from tkinter import messagebox, simpledialog

def renderizar(frame_pai, controller, app):
    COR_CARD = "#18181B"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)

    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(20, 10))
    ctk.CTkLabel(top, text="Controlo Operacional de Locações", font=FONT_TITULO).pack(side="left")

    tv = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8")
    tv.pack(padx=30, fill="both", expand=True)
    ta = tv.add("Locações Ativas")
    tn = tv.add("Nova Locação")

    def devolver_ui(id_contrato):
        km = simpledialog.askstring("Devolução de Veículo", "Insira a quilometragem atual do veículo para devolução:")
        if km and km.isdigit():
            s, m = controller.devolver_carro(id_contrato, km)
            if s: messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_locacoes")
            else: messagebox.showerror("Erro", m)

    def trocar_frota_ui(contrato):
        win = ctk.CTkToplevel(frame_pai)
        win.title("Troca de Frota")
        win.geometry("400x350")
        win.attributes("-topmost", True)
        win.configure(fg_color="#09090B")
        win.focus()
        
        ctk.CTkLabel(win, text=f"Motorista: {contrato.motorista.nome_completo}", font=FONT_CARD_TIT).pack(pady=(20, 10))
        ctk.CTkLabel(win, text="KM final do veículo atual:", font=FONT_TXT, text_color=COR_TEXTO_SEC).pack(pady=(5,0), anchor="w", padx=40)
        ekm = ctk.CTkEntry(win, width=320, height=40, font=FONT_TXT, corner_radius=6); ekm.pack(pady=5)
        
        disp = controller.listar_carros_disponiveis()
        ctk.CTkLabel(win, text="Novo veículo:", font=FONT_TXT, text_color=COR_TEXTO_SEC).pack(pady=(15,0), anchor="w", padx=40)
        cb = ctk.CTkComboBox(win, values=[f"{c.modelo} - {c.placa}" for c in disp], width=320, height=40, font=FONT_TXT, corner_radius=6)
        cb.set("Selecione o novo veículo...")
        cb.pack(pady=5)
        
        def conf_t():
            if not ekm.get(): return messagebox.showwarning("Erro", "Preencha a KM.")
            if "Selecione" in cb.get(): return messagebox.showwarning("Erro", "Selecione um veículo válido.")
            id_n = next((c.id_carro for c in disp if f"{c.modelo} - {c.placa}" == cb.get()), None)
            s, m = controller.processar_troca_veiculo(contrato.id_contrato, id_n, ekm.get())
            if s: win.destroy(); messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_locacoes")
            else: messagebox.showerror("Erro", m)
        ctk.CTkButton(win, text="Executar Substituição", fg_color="#3B82F6", hover_color="#1D4ED8", height=45, corner_radius=8, font=FONT_TXT, command=conf_t).pack(pady=25)

    # --- ABA ATIVAS ---
    sc = ctk.CTkScrollableFrame(ta, fg_color="transparent")
    sc.pack(fill="both", expand=True, pady=10)
    
    for loc in controller.listar_locacoes_ativas():
        card = ctk.CTkFrame(sc, fg_color=COR_CARD, corner_radius=12)
        card.pack(pady=8, padx=5, fill="x")
        
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=20, pady=15)
        
        nome_carro = f"[{loc.carro.numero_frota}] {loc.carro.modelo}" if loc.carro.numero_frota else loc.carro.modelo
        ctk.CTkLabel(info, text=f"{nome_carro} ({loc.carro.placa})   ➜   {loc.motorista.nome_completo}", font=FONT_CARD_TIT).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}   •   Valor Acordado: R$ {loc.valor_acordado:.2f}", text_color=COR_TEXTO_SEC, font=FONT_TXT).pack(anchor="w", pady=(5,0))

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(side="right", padx=20, pady=15)
        
        ctk.CTkButton(box, text="🔙 Devolver Veículo", fg_color="#F59E0B", hover_color="#D97706", height=32, corner_radius=6, command=lambda id_c=loc.id_contrato: devolver_ui(id_c)).pack(side="left", padx=5)
        ctk.CTkButton(box, text="🔄 Substituir Frota", fg_color="#3B82F6", hover_color="#1D4ED8", height=32, corner_radius=6, command=lambda l=loc: trocar_frota_ui(l)).pack(side="left", padx=5)

    # --- ABA NOVA LOCAÇÃO ---
    form = ctk.CTkFrame(tn, fg_color=COR_CARD, corner_radius=12)
    form.pack(pady=20, padx=20, fill="both", expand=True)
    container = ctk.CTkFrame(form, fg_color="transparent")
    container.pack(pady=30)

    c_cars = controller.listar_carros_disponiveis()
    c_mots = controller.listar_motoristas()
    
    nomes_carros = [f"[{c.numero_frota}] {c.modelo} - {c.placa} (R$ {c.tarifa.valor_diaria:.2f})" if c.numero_frota else f"{c.modelo} - {c.placa} (R$ {c.tarifa.valor_diaria:.2f})" for c in c_cars if c.tarifa]
    nomes_mots = [m.nome_completo for m in c_mots if m.status == "ATIVO"]

    ctk.CTkLabel(container, text="Selecione o Veículo:", font=FONT_TXT).grid(row=0, column=0, pady=10, padx=15, sticky="e")
    cb_c = ctk.CTkComboBox(container, values=nomes_carros, width=350, height=40, font=FONT_TXT, corner_radius=6)
    cb_c.set("Selecione um veículo...") 
    cb_c.grid(row=0, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Pesquisar Motorista:", font=FONT_TXT).grid(row=1, column=0, pady=10, padx=15, sticky="e")
    entry_pesquisa_mot = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6, placeholder_text="Digite o nome para filtrar...")
    entry_pesquisa_mot.grid(row=1, column=1, pady=10)

    ctk.CTkLabel(container, text="Motorista Responsável:", font=FONT_TXT).grid(row=2, column=0, pady=10, padx=15, sticky="e")
    cb_m = ctk.CTkComboBox(container, values=nomes_mots, width=350, height=40, font=FONT_TXT, corner_radius=6)
    cb_m.set("Selecione um motorista...")
    cb_m.grid(row=2, column=1, pady=10)
    
    def filtrar_motoristas(event):
        digitado = entry_pesquisa_mot.get().lower()
        if digitado.strip() == "":
            cb_m.configure(values=nomes_mots)
            cb_m.set("Selecione um motorista...")
            return
            
        filtrados = [n for n in nomes_mots if digitado in n.lower()]
        if filtrados:
            cb_m.configure(values=filtrados)
            cb_m.set(filtrados[0]) 
        else:
            cb_m.configure(values=[""])
            cb_m.set("Nenhum motorista encontrado")

    entry_pesquisa_mot.bind("<KeyRelease>", filtrar_motoristas)
    
    ctk.CTkLabel(container, text="Quantidade de Diárias:", font=FONT_TXT).grid(row=3, column=0, pady=10, padx=15, sticky="e")
    entry_dias_loc = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6, placeholder_text="Ex: 7")
    entry_dias_loc.grid(row=3, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Valor Final (R$):", font=FONT_TXT).grid(row=4, column=0, pady=10, padx=15, sticky="e")
    entry_valor_loc = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6)
    entry_valor_loc.grid(row=4, column=1, pady=10)

    def calcular_valor_automatico(event=None):
        txt_carro, txt_dias = cb_c.get(), entry_dias_loc.get().strip()
        if not txt_carro or "Selecione" in txt_carro or not txt_dias.isdigit(): return
        
        try:
            placa_str = txt_carro.split("(")[0].split("-")[-1].strip()
            carro_selecionado = next((c for c in c_cars if c.placa == placa_str), None)
            if carro_selecionado and carro_selecionado.tarifa:
                total = int(txt_dias) * carro_selecionado.tarifa.valor_diaria
                entry_valor_loc.delete(0, 'end')
                entry_valor_loc.insert(0, f"{total:.2f}")
        except: pass

    entry_dias_loc.bind("<KeyRelease>", calcular_valor_automatico)
    cb_c.configure(command=calcular_valor_automatico)
    
    def alu():
        if not cb_c.get() or "Selecione" in cb_c.get() or "Selecione" in cb_m.get() or not entry_valor_loc.get():
            return messagebox.showwarning("Aviso de Segurança", "Selecione um veículo, um motorista válido e preencha as diárias.")
        
        try:
            placa_str = cb_c.get().split("(")[0].split("-")[-1].strip()
            id_car = next((c.id_carro for c in c_cars if c.placa == placa_str), None)
        except: id_car = None
            
        id_mot = next((m.id_motorista for m in c_mots if m.nome_completo == cb_m.get()), None)
        
        if not id_car or not id_mot:
            return messagebox.showwarning("Erro", "Veículo ou Motorista inválido.")

        s, m = controller.alugar_carro(id_car, id_mot, entry_valor_loc.get())
        if s: messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_locacoes")
        else: messagebox.showerror("Erro", m)
        
    ctk.CTkButton(container, text="Confirmar Abertura de Locação", fg_color="#10B981", hover_color="#059669", height=45, corner_radius=8, font=FONT_CARD_TIT, command=alu).grid(row=5, column=0, columnspan=2, pady=35)