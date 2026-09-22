import customtkinter as ctk
from tkinter import messagebox

def renderizar(frame_pai, controller, app):
    COR_CARD = "#18181B"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)

    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(20, 10))
    ctk.CTkLabel(top, text="Gestão de Multas e Infrações", font=FONT_TITULO).pack(side="left")

    tv = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8")
    tv.pack(padx=30, fill="both", expand=True)
    
    tl = tv.add("Multas Aplicadas")
    tm = tv.add("Lançar Nova Multa")
    tc = tv.add("Catálogo (CTB)") 

    # --- ABA 1: MULTAS APLICADAS ---
    sc = ctk.CTkScrollableFrame(tl, fg_color="transparent")
    sc.pack(fill="both", expand=True, pady=10)

    for m in controller.listar_multas_aplicadas():
        card = ctk.CTkFrame(sc, fg_color=COR_CARD, corner_radius=12)
        card.pack(pady=8, fill="x", padx=5)
        
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(info, text=f"Condutor: {m.motorista.nome_completo}   •   Viatura: {m.carro.placa}", font=FONT_CARD_TIT).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Data: {m.data_infracao.strftime('%d/%m/%Y')}   •   Motivo: {m.infracao.descricao}", text_color=COR_TEXTO_SEC, font=FONT_TXT).pack(anchor="w", pady=(5,0))
        
        st_fr = ctk.CTkFrame(card, fg_color="transparent")
        st_fr.pack(side="right", padx=20, pady=15)
        
        ctk.CTkButton(st_fr, text="🗑️ Excluir", fg_color="#3F3F46", hover_color="#EF4444", width=80, height=32, corner_radius=6, command=lambda id_m=m.id_multa: controller.excluir_multa(id_m) and app.carregar_tela("tela_multas")).pack(side="right", padx=(10, 0))
        
        if m.status_pagamento == "PENDENTE":
            ctk.CTkLabel(st_fr, text=f"Débito: - R$ {m.valor_cobrado:.2f}", font=ctk.CTkFont(weight="bold", size=16), text_color="#EF4444").pack(side="right", padx=20)
            ctk.CTkButton(st_fr, text="💸 Quitar/Reembolso", fg_color="#10B981", hover_color="#059669", height=32, corner_radius=6, command=lambda id_m=m.id_multa: controller.quitar_multa(id_m) and app.carregar_tela("tela_multas")).pack(side="right")
        else:
            ctk.CTkLabel(st_fr, text=f"✅ Reembolsado: + R$ {m.valor_cobrado:.2f}", font=ctk.CTkFont(weight="bold", size=16), text_color="#10B981").pack(side="right", padx=20)

    # --- ABA 2: LANÇAR NOVA MULTA ---
    form = ctk.CTkFrame(tm, fg_color=COR_CARD, corner_radius=12)
    form.pack(pady=20, padx=20, fill="both", expand=True)
    container = ctk.CTkFrame(form, fg_color="transparent")
    container.pack(pady=30)

    cars = controller.listar_carros()
    mots = controller.listar_motoristas()
    infs = controller.listar_tipos_infracao()

    ctk.CTkLabel(container, text="Motorista Infrator:", font=FONT_TXT).grid(row=0, column=0, pady=10, padx=15, sticky="e")
    cb_m = ctk.CTkComboBox(container, values=[f"{m.nome_completo}" for m in mots], width=350, height=40, font=FONT_TXT, corner_radius=6)
    if mots: cb_m.set(mots[0].nome_completo)
    else: cb_m.set("Sem motoristas")
    cb_m.grid(row=0, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Veículo Utilizado:", font=FONT_TXT).grid(row=1, column=0, pady=10, padx=15, sticky="e")
    cb_c = ctk.CTkComboBox(container, values=[f"{c.modelo} - {c.placa}" for c in cars], width=350, height=40, font=FONT_TXT, corner_radius=6)
    if cars: cb_c.set(f"{cars[0].modelo} - {cars[0].placa}")
    else: cb_c.set("Sem carros")
    cb_c.grid(row=1, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Infração / Motivo:", font=FONT_TXT).grid(row=2, column=0, pady=10, padx=15, sticky="e")
    
    if not infs:
        cb_i = ctk.CTkComboBox(container, values=["Nenhuma infração cadastrada no catálogo"], width=350, height=40, font=FONT_TXT, corner_radius=6)
        cb_i.set("Vá ao Catálogo (CTB) primeiro")
    else:
        cb_i = ctk.CTkComboBox(container, values=[f"{i.artigo} - {i.descricao}" for i in infs], width=350, height=40, font=FONT_TXT, corner_radius=6)
        cb_i.set(f"{infs[0].artigo} - {infs[0].descricao}")
    cb_i.grid(row=2, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Data da Ocorrência:", font=FONT_TXT).grid(row=3, column=0, pady=10, padx=15, sticky="e")
    e_dt = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6, placeholder_text="DD/MM/AAAA"); e_dt.grid(row=3, column=1, pady=10)
    e_dt.bind("<KeyRelease>", app.mascara_data_geral)

    def save_m():
        if not infs: return messagebox.showwarning("Atenção", "Cadastre primeiro os tipos de infração no Catálogo.")
        id_m = next((m.id_motorista for m in mots if m.nome_completo == cb_m.get()), None)
        id_c = next((c.id_carro for c in cars if f"{c.modelo} - {c.placa}" == cb_c.get()), None)
        id_i = next((i.id_infracao for i in infs if f"{i.artigo} - {i.descricao}" == cb_i.get()), None)
        if not id_m or not id_c or not id_i: return messagebox.showwarning("Atenção", "Selecione opções válidas nas listas.")
        
        s, msg = controller.registrar_multa(id_m, id_c, id_i, e_dt.get())
        if s: messagebox.showinfo("Sucesso", msg); app.carregar_tela("tela_multas")
        else: messagebox.showerror("Erro", msg)
        
    ctk.CTkButton(container, text="Registar Débito", fg_color="#EF4444", hover_color="#DC2626", height=45, corner_radius=8, font=FONT_CARD_TIT, command=save_m).grid(row=4, column=0, columnspan=2, pady=35)

    # --- ABA 3: CATÁLOGO DE INFRAÇÕES (CTB) ---
    frame_top_cat = ctk.CTkFrame(tc, fg_color=COR_CARD, corner_radius=12)
    frame_top_cat.pack(fill="x", padx=10, pady=(10, 20))
    
    ctk.CTkLabel(frame_top_cat, text="Adicionar Nova Infração ao Catálogo", font=FONT_CARD_TIT, text_color="#3B82F6").grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")
    
    ctk.CTkLabel(frame_top_cat, text="Artigo (Ex: 218 I):", font=FONT_TXT).grid(row=1, column=0, padx=15, pady=8, sticky="e")
    ent_artigo = ctk.CTkEntry(frame_top_cat, width=150, height=35, placeholder_text="Código")
    ent_artigo.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    
    ctk.CTkLabel(frame_top_cat, text="Descrição / Motivo:", font=FONT_TXT).grid(row=1, column=2, padx=15, pady=8, sticky="e")
    ent_desc = ctk.CTkEntry(frame_top_cat, width=300, height=35, placeholder_text="Ex: Excesso de Velocidade")
    ent_desc.grid(row=1, column=3, padx=5, pady=8, sticky="w")
    
    ctk.CTkLabel(frame_top_cat, text="Gravidade:", font=FONT_TXT).grid(row=2, column=0, padx=15, pady=8, sticky="e")
    cb_grav = ctk.CTkComboBox(frame_top_cat, values=["Leve", "Média", "Grave", "Gravíssima"], width=150, height=35)
    cb_grav.grid(row=2, column=1, padx=5, pady=8, sticky="w")
    
    ctk.CTkLabel(frame_top_cat, text="Pontos na CNH:", font=FONT_TXT).grid(row=2, column=2, padx=15, pady=8, sticky="e")
    ent_pts = ctk.CTkEntry(frame_top_cat, width=100, height=35, placeholder_text="Ex: 7")
    ent_pts.grid(row=2, column=3, padx=5, pady=8, sticky="w")
    
    ctk.CTkLabel(frame_top_cat, text="Valor da Multa (R$):", font=FONT_TXT).grid(row=3, column=0, padx=15, pady=8, sticky="e")
    ent_val = ctk.CTkEntry(frame_top_cat, width=150, height=35, placeholder_text="Ex: 293.47")
    ent_val.grid(row=3, column=1, padx=5, pady=8, sticky="w")
    
    def add_infracao():
        if not ent_artigo.get() or not ent_desc.get() or not ent_pts.get() or not ent_val.get():
            return messagebox.showwarning("Aviso", "Preencha todos os campos do catálogo.")
        s, m = controller.adicionar_tipo_infracao(ent_artigo.get(), ent_desc.get(), cb_grav.get(), ent_pts.get(), ent_val.get())
        if s: app.carregar_tela("tela_multas")
        else: messagebox.showerror("Erro", m)

    ctk.CTkButton(frame_top_cat, text="Guardar no Catálogo", fg_color="#10B981", hover_color="#059669", height=35, command=add_infracao).grid(row=3, column=3, padx=5, pady=8, sticky="w")

    # Lista das Infrações do Catálogo
    sc_cat = ctk.CTkScrollableFrame(tc, fg_color="transparent")
    sc_cat.pack(fill="both", expand=True, padx=10, pady=5)
    
    for i in infs:
        crd = ctk.CTkFrame(sc_cat, fg_color=COR_CARD, corner_radius=8)
        crd.pack(pady=4, fill="x")
        ctk.CTkLabel(crd, text=f"Art. {i.artigo}", font=ctk.CTkFont(weight="bold", size=15), text_color="#60A5FA", width=100).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(crd, text=f"{i.descricao}\nGravidade: {i.gravidade}  |  Pontos: {i.pontos}", font=FONT_TXT, justify="left").pack(side="left", padx=15)
        ctk.CTkLabel(crd, text=f"R$ {i.valor_base:.2f}", font=ctk.CTkFont(weight="bold", size=16)).pack(side="right", padx=20)
        ctk.CTkButton(crd, text="🗑️", fg_color="transparent", text_color="#EF4444", hover_color="#7F1D1D", width=40, height=40, command=lambda id_i=i.id_infracao: controller.excluir_tipo_infracao(id_i) and app.carregar_tela("tela_multas")).pack(side="right")