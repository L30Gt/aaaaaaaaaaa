import customtkinter as ctk
from tkinter import ttk, messagebox

def renderizar(frame_pai, controller, app):
    app.id_motorista_editando = None
    app.modo_exclusao_mot = getattr(app, "modo_exclusao_mot", False)
    app.motoristas_em_memoria = {}

    pagina_atual = 1
    ITENS_POR_PAGINA = 10
    modo_visao = ctk.StringVar(value="Cards")

    COR_CARD = "#18181B"
    COR_BOX_INFO = "#27272A"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=COR_CARD, foreground="#FFFFFF", rowheight=35, fieldbackground=COR_CARD, borderwidth=0, font=("Segoe UI", 12))
    style.map('Treeview', background=[('selected', '#2563EB')], foreground=[('selected', '#FFFFFF')])
    style.configure("Treeview.Heading", background="#09090B", foreground="#3B82F6", font=("Segoe UI", 13, "bold"), borderwidth=0)
    style.map("Treeview.Heading", background=[('active', '#27272A')])

    # --- BARRA SUPERIOR ---
    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(20, 10))
    ctk.CTkLabel(top, text="Base de Motoristas", font=FONT_TITULO).pack(side="left")
    
    entry_pesquisa = ctk.CTkEntry(top, placeholder_text="Procurar por nome ou CPF...", width=250, height=40, font=FONT_TXT, corner_radius=8)
    entry_pesquisa.pack(side="right")

    def alternar_visualizacao(escolha):
        modo_visao.set(escolha)
        atualizar_exibicao_geral()

    btn_visao = ctk.CTkSegmentedButton(top, values=["Cards", "Tabela"], command=alternar_visualizacao, selected_color="#2563EB")
    btn_visao.set("Cards")
    btn_visao.pack(side="right", padx=10)
    ctk.CTkLabel(top, text="Visualização:", font=FONT_TXT).pack(side="right", padx=(10, 5))

    def toggle_exclusao():
        app.modo_exclusao_mot = not app.modo_exclusao_mot
        btn_toggle_exclusao.configure(
            fg_color="#EF4444" if app.modo_exclusao_mot else "transparent",
            text_color="#FFFFFF" if app.modo_exclusao_mot else "#EF4444"
        )
        atualizar_exibicao_geral()

    btn_toggle_exclusao = ctk.CTkButton(top, text="⚠️ Habilitar Exclusão", width=140, height=40, corner_radius=8, fg_color="#EF4444" if app.modo_exclusao_mot else "transparent", text_color="#FFFFFF" if app.modo_exclusao_mot else "#EF4444", border_width=1, border_color="#EF4444", font=ctk.CTkFont(weight="bold"), command=toggle_exclusao)
    btn_toggle_exclusao.pack(side="right", padx=(0, 15))

    tabview_mot = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB")
    tabview_mot.pack(padx=30, fill="both", expand=True)
    tab_list = tabview_mot.add("Fichas Cadastrais")
    tab_new = tabview_mot.add("Cadastrar / Editar")

    # --- CONTÊINER CARDS ---
    scroll_lista_cards = ctk.CTkScrollableFrame(tab_list, fg_color="transparent")
    
    frame_paginacao = ctk.CTkFrame(tab_list, fg_color="transparent")
    def mudar_pagina(direcao):
        nonlocal pagina_atual
        pagina_atual += direcao
        renderizar_cards()

    btn_anterior = ctk.CTkButton(frame_paginacao, text="◀ Anterior", width=100, height=32, fg_color="#3F3F46", command=lambda: mudar_pagina(-1))
    btn_anterior.pack(side="left", padx=20)
    lbl_paginacao = ctk.CTkLabel(frame_paginacao, text="Página 1 de 1", font=FONT_TXT)
    lbl_paginacao.pack(side="left", fill="x", expand=True)
    btn_proximo = ctk.CTkButton(frame_paginacao, text="Próximo ▶", width=100, height=32, fg_color="#3F3F46", command=lambda: mudar_pagina(1))
    btn_proximo.pack(side="right", padx=20)

    # --- CONTÊINER TABELA ---
    frame_tabela_wrapper = ctk.CTkFrame(tab_list, fg_color="transparent")
    frame_tv_interna = ctk.CTkFrame(frame_tabela_wrapper, fg_color="transparent"); frame_tv_interna.pack(fill="both", expand=True)
    scroll_y = ctk.CTkScrollbar(frame_tv_interna); scroll_y.pack(side="right", fill="y")
    
    colunas = ("id", "nome", "cpf", "cnh", "telefone", "status")
    tv = ttk.Treeview(frame_tv_interna, columns=colunas, show="headings", yscrollcommand=scroll_y.set)
    scroll_y.configure(command=tv.yview)
    tv.heading("id", text="Nº"); tv.heading("nome", text="Nome Completo"); tv.heading("cpf", text="CPF"); tv.heading("cnh", text="CNH"); tv.heading("telefone", text="Telefone"); tv.heading("status", text="Status")
    tv.column("id", width=60, anchor="center"); tv.column("nome", width=250, anchor="w"); tv.column("cpf", width=140, anchor="center"); tv.column("cnh", width=120, anchor="center"); tv.column("telefone", width=140, anchor="center"); tv.column("status", width=100, anchor="center")
    tv.tag_configure('par', background="#18181B"); tv.tag_configure('impar', background="#27272A"); tv.pack(side="left", fill="both", expand=True)

    frame_acoes_tabela = ctk.CTkFrame(frame_tabela_wrapper, fg_color=COR_BOX_INFO, corner_radius=8, height=60)
    frame_acoes_tabela.pack(fill="x", pady=(10, 0)); frame_acoes_tabela.pack_propagate(False)

    def obter_motorista_tabela():
        sel = tv.selection()
        return app.motoristas_em_memoria.get(int(sel[0])) if sel else None

    def on_treeview_select(event):
        m = obter_motorista_tabela()
        st = "normal" if m else "disabled"
        btn_t_perfil.configure(state=st)
        btn_t_editar.configure(state=st)
        btn_t_excluir.configure(state=st)

    tv.bind("<<TreeviewSelect>>", on_treeview_select)

    btn_t_perfil = ctk.CTkButton(frame_acoes_tabela, text="👁️ Perfil & Histórico", state="disabled", fg_color="#2563EB", command=lambda: mostrar_perfil(obter_motorista_tabela().id_motorista))
    btn_t_perfil.pack(side="left", padx=10, pady=15)
    btn_t_editar = ctk.CTkButton(frame_acoes_tabela, text="✏️ Editar Motorista", state="disabled", fg_color="#3F3F46", command=lambda: preparar_edicao(obter_motorista_tabela()))
    btn_t_editar.pack(side="left", padx=5, pady=15)
    btn_t_excluir = ctk.CTkButton(frame_acoes_tabela, text="🗑️ Excluir", state="disabled", fg_color="#EF4444", hover_color="#7F1D1D", command=lambda: confirmar_exclusao(obter_motorista_tabela()))

    def atualizar_exibicao_geral(event=None):
        if event: nonlocal pagina_atual; pagina_atual = 1
        
        if modo_visao.get() == "Cards":
            frame_tabela_wrapper.pack_forget()
            scroll_lista_cards.pack(fill="both", expand=True, pady=(0, 5))
            frame_paginacao.pack(fill="x", pady=5)
            renderizar_cards()
        else:
            scroll_lista_cards.pack_forget()
            frame_paginacao.pack_forget()
            frame_tabela_wrapper.pack(fill="both", expand=True, padx=10, pady=5)
            if app.modo_exclusao_mot: btn_t_excluir.pack(side="right", padx=10, pady=15)
            else: btn_t_excluir.pack_forget()
            renderizar_tabela()

    def renderizar_cards():
        for w in scroll_lista_cards.winfo_children(): w.destroy()
        termo = entry_pesquisa.get().lower()
        
        m_filtrados = [m for m in controller.listar_motoristas() if not termo or termo in m.nome_completo.lower() or termo in m.cpf]
        total_itens = len(m_filtrados)
        total_paginas = max(1, (total_itens + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
        
        nonlocal pagina_atual
        if pagina_atual > total_paginas: pagina_atual = total_paginas
        sub_lista = m_filtrados[(pagina_atual-1)*ITENS_POR_PAGINA : pagina_atual*ITENS_POR_PAGINA]

        for m in sub_lista:
            card = ctk.CTkFrame(scroll_lista_cards, fg_color=COR_CARD, corner_radius=12); card.pack(pady=8, padx=5, fill="x")
            info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(info, text=f"[Nº {m.id_motorista}] {m.nome_completo}", font=FONT_CARD_TIT).pack(anchor="w")
            ctk.CTkLabel(info, text=f"CPF: {m.cpf}   •   CNH: {m.cnh or 'N/A'}", text_color=COR_TEXTO_SEC, font=FONT_TXT).pack(anchor="w", pady=(5,0))
            
            btn_box = ctk.CTkFrame(card, fg_color="transparent"); btn_box.pack(side="right", padx=20, pady=15)
            cor_st = "#10B981" if m.status == "ATIVO" else "#EF4444"
            ctk.CTkLabel(btn_box, text=f"• {m.status}", font=ctk.CTkFont(weight="bold", size=13), text_color=cor_st).pack(side="right", padx=(15, 0))
            
            if app.modo_exclusao_mot:
                ctk.CTkButton(btn_box, text="🗑️ Excluir", width=90, height=32, fg_color="#EF4444", hover_color="#7F1D1D", command=lambda obj=m: confirmar_exclusao(obj)).pack(side="right", padx=5)
            ctk.CTkButton(btn_box, text="✏️ Editar", width=90, height=32, fg_color="#3F3F46", command=lambda obj=m: preparar_edicao(obj)).pack(side="right", padx=5)
            ctk.CTkButton(btn_box, text="👁️ Perfil & Feed", width=120, height=32, fg_color="#2563EB", command=lambda obj=m: mostrar_perfil(obj.id_motorista)).pack(side="right", padx=5)

        lbl_paginacao.configure(text=f"Página {pagina_atual} de {total_paginas}   •   ({total_itens} registros)")
        btn_anterior.configure(state="normal" if pagina_atual > 1 else "disabled")
        btn_proximo.configure(state="normal" if pagina_atual < total_paginas else "disabled")

    def renderizar_tabela():
        for item in tv.get_children(): tv.delete(item)
        app.motoristas_em_memoria.clear()
        termo = entry_pesquisa.get().lower()
        
        cont = 0
        for m in controller.listar_motoristas():
            if termo and termo not in m.nome_completo.lower() and termo not in m.cpf: continue
            app.motoristas_em_memoria[m.id_motorista] = m
            tag = 'par' if cont % 2 == 0 else 'impar'
            tv.insert("", "end", iid=m.id_motorista, values=(m.id_motorista, m.nome_completo, m.cpf, m.cnh or "N/A", m.telefone or "N/A", m.status), tags=(tag,))
            cont += 1
        on_treeview_select(None)

    entry_pesquisa.bind("<KeyRelease>", atualizar_exibicao_geral)
    atualizar_exibicao_geral()

    def mascara_cpf(event):
        entry = event.widget; numeros = "".join(filter(str.isdigit, entry.get()))[:11]
        if event.keysym not in ("BackSpace", "Delete"): entry.delete(0, "end"); entry.insert(0, "".join([d + ("." if i in (2, 5) else "-" if i == 8 else "") for i, d in enumerate(numeros)]))
    def mascara_telefone(event):
        entry = event.widget; numeros = "".join(filter(str.isdigit, entry.get()))[:11]; formatado = ""
        for i, d in enumerate(numeros):
            if i == 0: formatado += "("
            if i == 2: formatado += ") "
            if len(numeros) == 11 and i == 7: formatado += "-"
            elif len(numeros) < 11 and i == 6: formatado += "-"
            formatado += d
        if event.keysym not in ("BackSpace", "Delete"): entry.delete(0, "end"); entry.insert(0, formatado)
    def mascara_cnh(event):
        entry = event.widget; numeros = "".join(filter(str.isdigit, entry.get()))[:11]
        if event.keysym not in ("BackSpace", "Delete"): entry.delete(0, "end"); entry.insert(0, numeros)

    def preparar_edicao(motorista):
        app.id_motorista_editando = motorista.id_motorista; tabview_mot.set("Cadastrar / Editar")
        ent_m_nome.delete(0, 'end'); ent_m_nome.insert(0, motorista.nome_completo)
        ent_m_cpf.delete(0, 'end'); ent_m_cpf.insert(0, motorista.cpf)
        ent_m_cnh.delete(0, 'end'); ent_m_cnh.insert(0, motorista.cnh or "")
        ent_m_tel.delete(0, 'end'); ent_m_tel.insert(0, motorista.telefone or "")
        combo_status.set(motorista.status); btn_salvar_mot.configure(text="Atualizar Motorista", fg_color="#3B82F6")

    def confirmar_exclusao(motorista):
        if messagebox.askyesno("Crítico", f"Excluir o Motorista Nº {motorista.id_motorista} ({motorista.nome_completo})?"):
            s, m = controller.excluir_motorista(motorista.id_motorista)
            if s: messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_motoristas")
            else: messagebox.showwarning("Bloqueado", m)

    def mostrar_perfil(id_motorista):
        dados = controller.obter_resumo_motorista(id_motorista)
        for widget in frame_pai.winfo_children(): widget.destroy()
        tb = ctk.CTkFrame(frame_pai, fg_color="transparent"); tb.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkButton(tb, text="⬅ Voltar", width=80, height=35, fg_color="#3F3F46", command=lambda: app.carregar_tela("tela_motoristas")).pack(side="left", padx=(0,20))
        ctk.CTkLabel(tb, text=f"Perfil: {dados['nome']}", font=FONT_TITULO).pack(side="left")
        grid = ctk.CTkFrame(frame_pai, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=30, pady=10)
        esq = ctk.CTkFrame(grid, fg_color="transparent"); esq.pack(side="left", fill="both", expand=True, padx=(0,10))
        dir = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, width=380); dir.pack(side="right", fill="both", expand=True, padx=(10,0))
        ctk.CTkLabel(esq, text=f"Faturamento Gerado: R$ {dados['total_gasto']:.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#10B981").pack(anchor="w", pady=5)
        ctk.CTkLabel(esq, text="Histórico de Locações", font=FONT_CARD_TIT).pack(anchor="w", pady=(15, 5))
        sc_h = ctk.CTkScrollableFrame(esq, fg_color="transparent"); sc_h.pack(fill="both", expand=True)
        for h in dados['historico']:
            item = ctk.CTkFrame(sc_h, fg_color=COR_CARD, corner_radius=8); item.pack(fill="x", pady=4)
            ctk.CTkLabel(item, text=f"📅 {h['data_inicio']}   •   {h['carro']}").pack(padx=15, pady=12, anchor="w")
        ctk.CTkLabel(dir, text="💬 Feed de Ocorrências", font=FONT_CARD_TIT).pack(pady=(20, 10))
        txt_box = ctk.CTkTextbox(dir, height=80, fg_color="#27272A", corner_radius=8); txt_box.pack(fill="x", padx=20, pady=5)
        def post():
            if txt_box.get("1.0", "end").strip(): controller.adicionar_observacao(id_motorista, txt_box.get("1.0", "end").strip()); mostrar_perfil(id_motorista)
        ctk.CTkButton(dir, text="Postar Nota", fg_color="#2563EB", command=post).pack(padx=20, pady=10, anchor="e")
        sc_f = ctk.CTkScrollableFrame(dir, fg_color="transparent"); sc_f.pack(fill="both", expand=True, padx=10, pady=10)
        for o in dados['observacoes']:
            p = ctk.CTkFrame(sc_f, fg_color="#27272A", corner_radius=8); p.pack(fill="x", pady=5, padx=5)
            hdr = ctk.CTkFrame(p, fg_color="transparent"); hdr.pack(fill="x", padx=15, pady=(10,0))
            ctk.CTkLabel(hdr, text=o['data'], text_color=COR_TEXTO_SEC).pack(side="left")
            ctk.CTkButton(hdr, text="🗑️", width=25, height=25, fg_color="transparent", hover_color="#EF4444", command=lambda id_o=o['id']: controller.remover_observacao(id_o) or mostrar_perfil(id_motorista)).pack(side="right")
            ctk.CTkLabel(p, text=o['texto'], wraplength=300, justify="left", font=FONT_TXT).pack(anchor="w", padx=15, pady=(5,15))

    # --- FORMULÁRIO ---
    form = ctk.CTkFrame(tab_new, fg_color=COR_CARD, corner_radius=12); form.pack(pady=20, padx=20, fill="both", expand=True)
    container = ctk.CTkFrame(form, fg_color="transparent"); container.pack(pady=30)
    ctk.CTkLabel(container, text="Nome Completo:", font=FONT_TXT).grid(row=0, column=0, pady=10, padx=15, sticky="e")
    ent_m_nome = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6); ent_m_nome.grid(row=0, column=1, pady=10)
    ctk.CTkLabel(container, text="CPF:", font=FONT_TXT).grid(row=1, column=0, pady=10, padx=15, sticky="e")
    ent_m_cpf = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6); ent_m_cpf.grid(row=1, column=1, pady=10); ent_m_cpf.bind("<KeyRelease>", mascara_cpf)
    ctk.CTkLabel(container, text="CNH:", font=FONT_TXT).grid(row=2, column=0, pady=10, padx=15, sticky="e")
    ent_m_cnh = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6); ent_m_cnh.grid(row=2, column=1, pady=10); ent_m_cnh.bind("<KeyRelease>", mascara_cnh)
    ctk.CTkLabel(container, text="Telefone:", font=FONT_TXT).grid(row=3, column=0, pady=10, padx=15, sticky="e")
    ent_m_tel = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6); ent_m_tel.grid(row=3, column=1, pady=10); ent_m_tel.bind("<KeyRelease>", mascara_telefone)
    ctk.CTkLabel(container, text="Status Contratual:", font=FONT_TXT).grid(row=4, column=0, pady=10, padx=15, sticky="e")
    combo_status = ctk.CTkComboBox(container, values=["ATIVO", "INATIVO"], width=350, height=40, font=FONT_TXT, corner_radius=6); combo_status.grid(row=4, column=1, pady=10)
    def salvar_m():
        if app.id_motorista_editando: s, m = controller.atualizar_motorista(app.id_motorista_editando, ent_m_nome.get(), ent_m_cpf.get(), ent_m_cnh.get(), ent_m_tel.get(), combo_status.get())
        else: s, m = controller.adicionar_motorista(ent_m_nome.get(), ent_m_cpf.get(), ent_m_cnh.get(), ent_m_tel.get(), combo_status.get())
        if s: messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_motoristas")
        else: messagebox.showerror("Erro", m)
    btn_salvar_mot = ctk.CTkButton(container, text="Salvar Motorista", fg_color="#10B981", hover_color="#059669", height=45, corner_radius=8, font=FONT_CARD_TIT, command=salvar_m)
    btn_salvar_mot.grid(row=5, column=0, columnspan=2, pady=35)