import customtkinter as ctk
from tkinter import messagebox
import re

def renderizar(frame_pai, controller, app):
    COR_CARD = "#18181B"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)

    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(20, 10))
    ctk.CTkLabel(top, text="Controlo de Alvarás Oficiais", font=FONT_TITULO).pack(side="left")

    tv = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8")
    tv.pack(padx=30, fill="both", expand=True)
    ta = tv.add("Status da Frota")
    tn = tv.add("Renovar / Registar Alvará")

    carros = controller.listar_carros()
    lista_carros_cb = []
    for c in carros:
        if c.status != "VENDIDO":
            nome = f"[{c.numero_frota}] {c.modelo} - {c.placa}" if c.numero_frota else f"{c.modelo} - {c.placa}"
            lista_carros_cb.append(nome)


    form = ctk.CTkFrame(tn, fg_color=COR_CARD, corner_radius=12)
    form.pack(pady=20, padx=20, fill="both", expand=True)
    container = ctk.CTkFrame(form, fg_color="transparent")
    container.pack(pady=30)

    ctk.CTkLabel(container, text="Selecione o Veículo:", font=FONT_TXT).grid(row=0, column=0, pady=10, padx=15, sticky="e")
    cb_c = ctk.CTkComboBox(container, values=lista_carros_cb, width=350, height=40, font=FONT_TXT, corner_radius=6)
    if lista_carros_cb: cb_c.set(lista_carros_cb[0])
    else: cb_c.set("Nenhum veículo disponível")
    cb_c.grid(row=0, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Número do Alvará/Documento:", font=FONT_TXT).grid(row=1, column=0, pady=10, padx=15, sticky="e")
    e_doc = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6)
    e_doc.grid(row=1, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Data de Vencimento:", font=FONT_TXT).grid(row=2, column=0, pady=10, padx=15, sticky="e")
    e_dat = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6, placeholder_text="DD/MM/AAAA")
    e_dat.grid(row=2, column=1, pady=10)
    e_dat.bind("<KeyRelease>", app.mascara_data_geral)
    
    def save_a():
        if not cb_c.get() or "Nenhum" in cb_c.get() or not e_doc.get() or not e_dat.get():
            return messagebox.showwarning("Erro", "Preencha todas as informações do documento.")
        
        placa_str = cb_c.get().split("-")[-1].strip()
        id_c = next((c.id_carro for c in carros if c.placa == placa_str), None)
        
        s, m = controller.registrar_alvara(id_c, e_doc.get(), e_dat.get())
        if s: messagebox.showinfo("Sucesso", m); app.carregar_tela("tela_alvaras")
        else: messagebox.showerror("Erro", m)
        
    ctk.CTkButton(container, text="Registar Documento Oficial", fg_color="#3B82F6", hover_color="#1D4ED8", height=45, corner_radius=8, font=FONT_CARD_TIT, command=save_a).grid(row=3, column=0, columnspan=2, pady=35)

    def preparar_renovacao(nome_carro, doc_antigo, data_antiga):
        tv.set("Renovar / Registar Alvará")
        cb_c.set(nome_carro)
        e_doc.delete(0, 'end')
        if doc_antigo != "N/A": e_doc.insert(0, doc_antigo)
        e_dat.delete(0, 'end')
        if data_antiga != "N/A": e_dat.insert(0, data_antiga)
        e_doc.focus()

    filtro_ordem = ctk.StringVar(value="Data de Vencimento")
    menu_ordem = ctk.CTkSegmentedButton(ta, values=["Data de Vencimento", "Ordem de Frota"], variable=filtro_ordem, selected_color="#2563EB", selected_hover_color="#1D4ED8", command=lambda _: atualizar_lista_alvaras())
    menu_ordem.pack(fill="x", padx=5, pady=10)

    sc = ctk.CTkScrollableFrame(ta, fg_color="transparent")
    sc.pack(fill="both", expand=True, pady=5)
    
    def atualizar_lista_alvaras():
        for w in sc.winfo_children(): w.destroy()
        docs = controller.listar_documentacao_frota()

        if filtro_ordem.get() == "Ordem de Frota":
            def extrair_num(nome_carro):
                match = re.search(r'\[(\d+)\]', nome_carro)
                return int(match.group(1)) if match else 999999
            docs.sort(key=lambda d: extrair_num(d['carro']))
        else:
            docs.sort(key=lambda d: d['dias_restantes'])

        for d in docs:
            card = ctk.CTkFrame(sc, fg_color=COR_CARD, corner_radius=12)
            card.pack(pady=8, padx=5, fill="x")
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=20, pady=15)
            
            ctk.CTkLabel(info, text=d['carro'], font=FONT_CARD_TIT).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Documento Nº: {d['numero_doc']}   •   Vencimento: {d['vencimento']}", text_color=COR_TEXTO_SEC, font=FONT_TXT).pack(anchor="w", pady=(5,0))

            box = ctk.CTkFrame(card, fg_color="transparent")
            box.pack(side="right", padx=20, pady=15)
            
            ctk.CTkButton(box, text="📝 Renovar", fg_color="#3B82F6", hover_color="#1D4ED8", width=100, height=32, corner_radius=6, command=lambda n=d['carro'], doc=d['numero_doc'], dt=d['vencimento']: preparar_renovacao(n, doc, dt)).pack(side="right", padx=(15, 0))

            st = d['status']
            cor_st = "#10B981" if st == "REGULAR" else "#F59E0B" if st == "VENCE EM BREVE" else "#EF4444"
            ctk.CTkLabel(box, text=f"• {st}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=cor_st).pack(side="right", padx=10)

    atualizar_lista_alvaras()