import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import re
from PIL import Image, ImageOps

def renderizar(frame_pai, controller, app):
    app.id_carro_editando = None
    app.caminho_foto_atual = None
    app.carros_em_memoria = {}

    # ==========================================
    # 1. VARIÁVEIS DE CONTROLE E ESCOPO DA TELA
    # ==========================================
    pagina_atual = 1
    ITENS_POR_PAGINA = 10
    modo_visao = ctk.StringVar(value="Cards")
    filtro_var = ctk.StringVar(value="Todos")

    COR_CARD = "#18181B"
    COR_BOX_INFO = "#27272A" 
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_CARD_TIT = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    FONT_TXT = ctk.CTkFont(family="Segoe UI", size=14)

    # ==========================================
    # 2. MOTORES DE FUNÇÃO E INTERAÇÃO COM O BANCO
    # ==========================================
    def executar_upload_foto():
        caminho = filedialog.askopenfilename(
            title="Selecione a foto do veículo", 
            filetypes=[("Arquivos de Imagem", "*.jpg *.png *.jpeg")]
        )
        if caminho:
            app.caminho_foto_atual = caminho
            lbl_nome_foto.configure(text=os.path.basename(caminho), text_color="#10B981")

    def registrar_oleo_ui(carro):
        if not carro:
            return messagebox.showwarning("Atenção", "Nenhum veículo selecionado.")
        km_nova = simpledialog.askstring("Troca de Óleo", f"Digite a quilometragem atual para o veículo {carro.modelo}:")
        if km_nova and km_nova.isdigit():
            if controller.registrar_troca_oleo(carro.id_carro, int(km_nova)):
                messagebox.showinfo("Sucesso", "Registro de troca de óleo computado com sucesso!")
                controller.adicionar_evento_carro(
                    carro.id_carro, 
                    "ÓLEO E FILTROS", 
                    f"Substituição de óleo e filtros realizada na quilometragem: {km_nova} km"
                )
                atualizar_exibicao_geral()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar a quilometragem no banco de dados.")

    def alternar_manutencao_ui(carro):
        if not carro:
            return
        s, msg = controller.alternar_manutencao(carro.id_carro)
        if s:
            atualizar_exibicao_geral()
        else:
            messagebox.showerror("Erro de Operação", msg)

    def abrir_linha_tempo(carro):
        if not carro:
            return
        d_lt = ctk.CTkToplevel(frame_pai)
        d_lt.title(f"Histórico de Ocorrências - Placa: {carro.placa}")
        d_lt.geometry("800x600")
        d_lt.attributes("-topmost", True)
        d_lt.configure(fg_color="#09090B")
        d_lt.focus()
        
        ctk.CTkLabel(d_lt, text=f"Diário de Bordo: {carro.modelo}", font=FONT_TITULO).pack(pady=(20, 10))
        grid = ctk.CTkFrame(d_lt, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=10)
        
        form_frame = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, width=300)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Nova Ocorrência", font=FONT_CARD_TIT, text_color="#3B82F6").pack(pady=15, padx=15, anchor="w")
        ctk.CTkLabel(form_frame, text="Categoria do Evento:", font=FONT_TXT).pack(anchor="w", padx=15, pady=(5, 0))
        cb_tipo = ctk.CTkComboBox(form_frame, values=["PNEUS", "BATERIA", "MECÂNICA GERAL", "ELÉTRICA", "ESTÉTICA", "DOCUMENTAÇÃO", "OUTROS"], width=250)
        cb_tipo.pack(padx=15, pady=5)
        
        ctk.CTkLabel(form_frame, text="Detalhamento Técnico:", font=FONT_TXT).pack(anchor="w", padx=15, pady=(5, 0))
        txt_desc = ctk.CTkTextbox(form_frame, width=250, height=150, fg_color="#27272A", corner_radius=8)
        txt_desc.pack(padx=15, pady=5)
        
        def registrar_evento():
            desc = txt_desc.get("1.0", "end").strip()
            if not desc:
                return messagebox.showwarning("Validação", "O campo de descrição técnica é obrigatório.")
            s, m = controller.adicionar_evento_carro(carro.id_carro, cb_tipo.get(), desc)
            if s:
                d_lt.destroy()
                abrir_linha_tempo(carro)
            else:
                messagebox.showerror("Erro", m)
            
        ctk.CTkButton(form_frame, text="Gravar no Diário", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=registrar_evento).pack(pady=20, padx=15)
        
        timeline_frame = ctk.CTkScrollableFrame(grid, fg_color="transparent")
        timeline_frame.pack(side="right", fill="both", expand=True)
        
        eventos = controller.listar_eventos_carro(carro.id_carro)
        if not eventos: 
            ctk.CTkLabel(timeline_frame, text="Nenhum histórico registrado para este ativo.", text_color=COR_TEXTO_SEC, font=FONT_TXT).pack(pady=50)
        for ev in eventos:
            card_ev = ctk.CTkFrame(timeline_frame, fg_color=COR_CARD, corner_radius=8)
            card_ev.pack(fill="x", pady=6)
            hf = ctk.CTkFrame(card_ev, fg_color="transparent")
            hf.pack(fill="x", padx=15, pady=(10,0))
            ctk.CTkLabel(hf, text=ev.data_hora.strftime("%d/%m/%Y às %H:%M"), font=ctk.CTkFont(size=12, weight="bold"), text_color=COR_TEXTO_SEC).pack(side="left")
            ctk.CTkButton(hf, text="🗑️", fg_color="transparent", text_color="#EF4444", width=30, height=30, command=lambda id_e=ev.id_evento: controller.excluir_evento_carro(id_e) and d_lt.destroy() or abrir_linha_tempo(carro)).pack(side="right")
            ctk.CTkLabel(hf, text=f"   • {ev.tipo}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA").pack(side="left")
            ctk.CTkLabel(card_ev, text=ev.descricao, font=FONT_TXT, justify="left", wraplength=400).pack(anchor="w", padx=15, pady=(5, 15))

    def mostrar_detalhes_ui(carro):
        if not carro:
            return
        d = ctk.CTkToplevel(frame_pai)
        d.title(f"Ficha Cadastral Completa - {carro.placa}")
        d.geometry("750x720")
        d.attributes("-topmost", True)
        d.configure(fg_color="#09090B")
        d.focus()
        
        content = ctk.CTkScrollableFrame(d, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        hdr = ctk.CTkFrame(content, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(hdr, text=f"Ficha Técnica: {carro.modelo}", font=FONT_TITULO).pack(side="left")
        ctk.CTkButton(hdr, text="📅 Linha do Tempo", fg_color="#8B5CF6", hover_color="#7C3AED", font=ctk.CTkFont(weight="bold"), command=lambda: abrir_linha_tempo(carro)).pack(side="right")
        
        if carro.foto and os.path.exists(carro.foto):
            try:
                img_fmt = ImageOps.pad(Image.open(carro.foto), (280, 180), color=COR_CARD)
                ctk.CTkLabel(content, image=ctk.CTkImage(light_image=img_fmt, dark_image=img_fmt, size=(280, 180)), text="").pack(pady=(0, 20))
            except:
                pass
                
        grid_frame = ctk.CTkFrame(content, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        def criar_caixa(r, col, t, v):
            bx = ctk.CTkFrame(grid_frame, fg_color=COR_BOX_INFO, corner_radius=8)
            bx.grid(row=r, column=col, sticky="nsew", padx=8, pady=8)
            ctk.CTkLabel(bx, text=t, font=ctk.CTkFont(weight="bold", size=14), text_color="#60A5FA").pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(bx, text=str(v), font=ctk.CTkFont(size=15)).pack(anchor="w", padx=15, pady=(0, 10))
            
        criar_caixa(0, 0, "Nº da Frota", carro.numero_frota or "N/A")
        criar_caixa(0, 1, "Status Operacional", carro.status)
        criar_caixa(1, 0, "Placa / Matrícula", carro.placa)
        criar_caixa(1, 1, "Valor de Contrato Diário", f"R$ {carro.tarifa.valor_diaria:.2f}" if carro.tarifa else "N/A")
        criar_caixa(2, 0, "Ano de Fabricação", carro.ano or "N/A")
        criar_caixa(2, 1, "Cor do Ativo", carro.cor or "N/A")
        criar_caixa(3, 0, "Quilometragem Atual", f"{carro.km_atual:,} km")
        criar_caixa(3, 1, "Próxima Troca de Óleo", f"{carro.km_proxima_troca:,} km")
        criar_caixa(4, 0, "Nº do Taxímetro", carro.numero_taximetro or "N/A")
        criar_caixa(4, 1, "Marca do Aparelho", carro.marca_taximetro or "N/A")
        criar_caixa(5, 0, "Data da Última Aferição", carro.data_afericao_taximetro or "N/A")
        criar_caixa(5, 1, "Numeração do Chassi", carro.chassi or "N/A")
        
        if carro.observacoes:
            bo = ctk.CTkFrame(grid_frame, fg_color="#3F3F46", corner_radius=8)
            bo.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            ctk.CTkLabel(bo, text="📌 Observações Gerais e Histórico de Importação", font=ctk.CTkFont(weight="bold", size=14), text_color="#FCA5A5").pack(anchor="w", padx=15, pady=(10, 5))
            ctk.CTkLabel(bo, text=carro.observacoes, font=ctk.CTkFont(size=15), justify="left", wraplength=600).pack(anchor="w", padx=15, pady=(0, 15))

    def preparar_edicao(carro):
        if not carro: 
            return
        app.id_carro_editando = carro.id_carro
        tabview.set("Cadastrar / Editar")
        entry_frota.delete(0, 'end'); entry_frota.insert(0, carro.numero_frota or "")
        entry_modelo.delete(0, 'end'); entry_modelo.insert(0, carro.modelo)
        entry_placa.delete(0, 'end'); entry_placa.insert(0, carro.placa)
        entry_cor.delete(0, 'end'); entry_cor.insert(0, carro.cor or "")
        entry_ano.delete(0, 'end'); entry_ano.insert(0, carro.ano or "")
        entry_chassi.delete(0, 'end'); entry_chassi.insert(0, carro.chassi or "")
        entry_num_taxi.delete(0, 'end'); entry_num_taxi.insert(0, carro.numero_taximetro or "")
        entry_marca_taxi.delete(0, 'end'); entry_marca_taxi.insert(0, carro.marca_taximetro or "")
        entry_data_afer.delete(0, 'end'); entry_data_afer.insert(0, carro.data_afericao_taximetro or "")
        entry_obs.delete(0, 'end'); entry_obs.insert(0, carro.observacoes or "")
        entry_km.delete(0, 'end'); entry_km.insert(0, str(carro.km_atual))
        entry_tarifa.delete(0, 'end')
        if carro.tarifa: 
            entry_tarifa.insert(0, str(carro.tarifa.valor_diaria))
        app.caminho_foto_atual = carro.foto
        if carro.foto: 
            lbl_nome_foto.configure(text=os.path.basename(carro.foto), text_color="#10B981")
        else: 
            lbl_nome_foto.configure(text="Nenhuma foto anexada", text_color=COR_TEXTO_SEC)
        if hasattr(app, 'btn_salvar_carro'): 
            app.btn_salvar_carro.configure(text="Atualizar Dados do Veículo", fg_color="#3B82F6")

    def vender_carro_ui(carro):
        if not carro: 
            return
        d = ctk.CTkToplevel(frame_pai)
        d.title("Processamento de Baixa por Venda")
        d.geometry("400x350")
        d.attributes("-topmost", True)
        d.configure(fg_color="#09090B")
        d.focus()
        
        ctk.CTkLabel(d, text=f"Alienação: {carro.modelo}", font=FONT_TITULO).pack(pady=(20, 15))
        ec = ctk.CTkEntry(d, width=300, placeholder_text="Nome do Comprador", height=40)
        ec.pack(pady=10)
        ev = ctk.CTkEntry(d, width=300, placeholder_text="Valor da Venda (R$)", height=40)
        ev.pack(pady=10)
        chk = ctk.CTkCheckBox(d, text="Exige Nota Promissória Vinculada")
        chk.pack(pady=15)
        chk.select() 
        
        def conf():
            if not ec.get() or not ev.get(): 
                return messagebox.showwarning("Erro", "Todos os campos de venda são obrigatórios.")
            s, msg = controller.processar_venda_veiculo(carro.id_carro, ec.get(), ev.get(), chk.get())
            if s: 
                d.destroy()
                resetar_e_atualizar()
            else:
                messagebox.showerror("Erro", msg)
        ctk.CTkButton(d, text="Confirmar e Baixar Ativo", fg_color="#8B5CF6", command=conf).pack(pady=10)

    def salvar_carro():
        val_tarifa = entry_tarifa.get().strip()
        num_frota = entry_frota.get().strip()
        if not val_tarifa: 
            return messagebox.showwarning("Atenção", "Preencha o valor da diária para o cálculo financeiro.")
        if app.id_carro_editando: 
            s, m = controller.atualizar_carro(app.id_carro_editando, num_frota, entry_placa.get(), entry_modelo.get(), val_tarifa, entry_km.get(), entry_cor.get(), entry_ano.get(), entry_chassi.get(), entry_num_taxi.get(), entry_marca_taxi.get(), entry_data_afer.get(), entry_obs.get(), app.caminho_foto_atual)
        else: 
            s, m = controller.adicionar_carro(num_frota, entry_placa.get(), entry_modelo.get(), val_tarifa, entry_km.get(), entry_cor.get(), entry_ano.get(), entry_chassi.get(), entry_num_taxi.get(), entry_marca_taxi.get(), entry_data_afer.get(), entry_obs.get(), app.caminho_foto_atual)
        if s: 
            messagebox.showinfo("Sucesso", m)
            app.carregar_tela("tela_frota")
        else: 
            messagebox.showerror("Erro de Salvamento", m)

    def mudar_pagina(direcao):
        nonlocal pagina_atual
        pagina_atual += direcao
        renderizar_cards()

    def resetar_e_atualizar():
        nonlocal pagina_atual
        pagina_atual = 1
        atualizar_exibicao_geral()

    def alternar_visualizacao(escolha):
        modo_visao.set(escolha)
        atualizar_exibicao_geral()

    def atualizar_exibicao_geral():
        if modo_visao.get() == "Cards":
            frame_tabela_wrapper.pack_forget()
            scroll_lista_cards.pack(fill="both", expand=True, pady=(0, 5))
            frame_paginacao.pack(fill="x", pady=5)
            renderizar_cards()
        else:
            scroll_lista_cards.pack_forget()
            frame_paginacao.pack_forget()
            frame_tabela_wrapper.pack(fill="both", expand=True, padx=10, pady=5)
            renderizar_tabela()

    def renderizar_cards():
        for w in scroll_lista_cards.winfo_children(): 
            w.destroy()
        status_filtro = filtro_var.get()
        
        carros_filtrados = [c for c in controller.listar_carros() if c.status != "VENDIDO" and (status_filtro == "Todos" or c.status == status_filtro.upper().replace("Í", "I"))]
        total_itens = len(carros_filtrados)
        total_paginas = max(1, (total_itens + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
        
        nonlocal pagina_atual
        if pagina_atual > total_paginas: 
            pagina_atual = total_paginas
        if pagina_atual < 1: 
            pagina_atual = 1
        
        sub_lista = carros_filtrados[(pagina_atual-1)*ITENS_POR_PAGINA : pagina_atual*ITENS_POR_PAGINA]
        
        for c in sub_lista:
            card = ctk.CTkFrame(scroll_lista_cards, fg_color=COR_CARD, corner_radius=12)
            card.pack(pady=8, padx=5, fill="x")
            
            ph = ctk.CTkFrame(card, width=150, height=110, fg_color="#27272A", corner_radius=8)
            ph.pack(side="left", padx=15, pady=15)
            ph.pack_propagate(False)
            if c.foto and os.path.exists(c.foto):
                try:
                    img_f = ImageOps.pad(Image.open(c.foto), (150, 110), color="#27272A")
                    ctk.CTkLabel(ph, image=ctk.CTkImage(light_image=img_f, dark_image=img_f, size=(150, 110)), text="").place(relx=0.5, rely=0.5, anchor="center")
                except: 
                    ctk.CTkLabel(ph, text="📷\nErro", font=FONT_TXT).place(relx=0.5, rely=0.5, anchor="center")
            else: 
                ctk.CTkLabel(ph, text="📷", font=ctk.CTkFont(size=24)).place(relx=0.5, rely=0.5, anchor="center")

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=10, pady=15)
            km_restante = c.km_proxima_troca - c.km_atual
            alerta_oleo = "  (⚠️ Óleo!)" if km_restante <= 1000 else ""
            
            header = ctk.CTkFrame(info, fg_color="transparent")
            header.pack(anchor="w")
            ctk.CTkLabel(header, text=f"[{c.numero_frota}] {c.modelo}" if c.numero_frota else c.modelo, font=FONT_CARD_TIT).pack(side="left")
            if alerta_oleo: 
                ctk.CTkLabel(header, text=alerta_oleo, font=ctk.CTkFont(size=14, weight="bold"), text_color="#EF4444").pack(side="left", padx=5)
            
            ctk.CTkLabel(info, text=f"Diária: R$ {c.tarifa.valor_diaria:.2f}   •   Placa: {c.placa}\nKM Atual: {c.km_atual:,} km   •   Próx. Óleo: {c.km_proxima_troca:,} km", font=FONT_TXT, text_color=COR_TEXTO_SEC, justify="left").pack(anchor="w", pady=(10,0))
            
            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=20, pady=15)
            btn_grid = ctk.CTkFrame(btn_box, fg_color="transparent")
            btn_grid.pack(side="top", pady=(0, 5))
            
            ctk.CTkButton(btn_grid, text="📄 Detalhes", width=85, height=32, corner_radius=6, fg_color="#3F3F46", command=lambda obj=c: mostrar_detalhes_ui(obj)).grid(row=0, column=0, padx=3, pady=3)
            ctk.CTkButton(btn_grid, text="✏️ Editar", width=85, height=32, corner_radius=6, fg_color="#2563EB", command=lambda obj=c: preparar_edicao(obj)).grid(row=0, column=1, padx=3, pady=3)
            ctk.CTkButton(btn_grid, text="🤝 Vender", width=85, height=32, corner_radius=6, fg_color="#8B5CF6", command=lambda obj=c: vender_carro_ui(obj)).grid(row=0, column=2, padx=3, pady=3)
            ctk.CTkButton(btn_grid, text="🛢️ Óleo", width=85, height=32, corner_radius=6, fg_color="#3F3F46", command=lambda obj=c: registrar_oleo_ui(obj)).grid(row=1, column=0, padx=3, pady=3)
            
            if c.status in ["DISPONIVEL", "MANUTENCAO"]:
                ctk.CTkButton(btn_grid, text="✅ Liberar" if c.status == "MANUTENCAO" else "🔧 Manutenção", width=176, height=32, corner_radius=6, fg_color="#10B981" if c.status == "MANUTENCAO" else "#F59E0B", command=lambda obj=c: alternar_manutencao_ui(obj)).grid(row=1, column=1, columnspan=2, padx=3, pady=3)

            cor_st = "#10B981" if c.status == "DISPONIVEL" else "#3B82F6" if c.status == "ALUGADO" else "#F59E0B" if c.status == "MANUTENCAO" else "#EF4444"
            ctk.CTkLabel(btn_box, text=f"• {c.status}", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=cor_st).pack(side="right", pady=(5,0))

        lbl_paginacao.configure(text=f"Página {pagina_atual} de {total_paginas}   •   ({total_itens} veículos encontrados)")
        btn_anterior.configure(state="normal" if pagina_atual > 1 else "disabled")
        btn_proximo.configure(state="normal" if pagina_atual < total_paginas else "disabled")

    def renderizar_tabela():
        for item in tv.get_children(): 
            tv.delete(item)
        app.carros_em_memoria.clear()
        status_filtro = filtro_var.get()
        
        cont = 0
        for c in controller.listar_carros():
            if c.status == "VENDIDO": 
                continue
            if status_filtro == "Disponível" and c.status != "DISPONIVEL": 
                continue
            if status_filtro == "Alugado" and c.status != "ALUGADO": 
                continue
            if status_filtro == "Manutenção" and c.status != "MANUTENCAO": 
                continue
            
            app.carros_em_memoria[c.id_carro] = c
            tag = 'par' if cont % 2 == 0 else 'impar'
            txt_oleo = f"{c.km_proxima_troca:,}"
            if (c.km_proxima_troca - c.km_atual) <= 1000: 
                txt_oleo = "⚠️ " + txt_oleo
            
            tv.insert("", "end", iid=c.id_carro, values=(c.numero_frota or "-", c.placa, c.modelo, f"{c.tarifa.valor_diaria:.2f}", f"{c.km_atual:,}", txt_oleo, c.status), tags=(tag,))
            cont += 1
        on_treeview_select(None)

    def obter_carro_tabela():
        sel = tv.selection()
        return app.carros_em_memoria.get(int(sel[0])) if sel else None

    def on_treeview_select(event):
        c = obter_carro_tabela()
        st = "normal" if c else "disabled"
        btn_t_detalhes.configure(state=st)
        btn_t_editar.configure(state=st)
        btn_t_vender.configure(state=st)
        btn_t_oleo.configure(state=st)
        if c and c.status in ["DISPONIVEL", "MANUTENCAO"]:
            btn_t_manut.configure(state="normal", text="✅ Liberar" if c.status == "MANUTENCAO" else "🔧 Manutenção", fg_color="#10B981" if c.status == "MANUTENCAO" else "#F59E0B")
        else:
            btn_t_manut.configure(state="disabled", text="🔧 Manutenção", fg_color="#3F3F46")


    # ==========================================
    # 3. CONSTRUÇÃO COMPLETA DA INTERFACE VISUAL
    # ==========================================
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=COR_CARD, foreground="#FFFFFF", rowheight=35, fieldbackground=COR_CARD, borderwidth=0, font=("Segoe UI", 12))
    style.map('Treeview', background=[('selected', '#2563EB')], foreground=[('selected', '#FFFFFF')])
    style.configure("Treeview.Heading", background="#09090B", foreground="#3B82F6", font=("Segoe UI", 13, "bold"), borderwidth=0)
    style.map("Treeview.Heading", background=[('active', '#27272A')])

    top = ctk.CTkFrame(frame_pai, fg_color="transparent"); top.pack(fill="x", padx=30, pady=(20, 10))
    btn_visao = ctk.CTkSegmentedButton(top, values=["Cards", "Tabela"], command=alternar_visualizacao, selected_color="#2563EB")
    btn_visao.set("Cards")
    btn_visao.pack(side="right", padx=10)
    ctk.CTkLabel(top, text="Visualização:", font=FONT_TXT).pack(side="right", padx=(10, 5))

    tabview = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8")
    tabview.pack(padx=30, pady=0, fill="both", expand=True)
    
    tab_list = tabview.add("Veículos Ativos")
    tab_new = tabview.add("Cadastrar / Editar")
    tab_vendidos = tabview.add("Histórico de Vendas")
    
    filtro_menu = ctk.CTkSegmentedButton(tab_list, values=["Todos", "Disponível", "Alugado", "Manutenção"], variable=filtro_var, selected_color="#2563EB", selected_hover_color="#1D4ED8", command=lambda _: resetar_e_atualizar())
    filtro_menu.pack(fill="x", padx=10, pady=10)

    # AREA DO MODO CARDS
    scroll_lista_cards = ctk.CTkScrollableFrame(tab_list, fg_color="transparent")
    frame_paginacao = ctk.CTkFrame(tab_list, fg_color="transparent")
    btn_anterior = ctk.CTkButton(frame_paginacao, text="◀ Anterior", width=100, height=32, fg_color="#3F3F46", hover_color="#52525B", command=lambda: mudar_pagina(-1))
    btn_anterior.pack(side="left", padx=20)
    lbl_paginacao = ctk.CTkLabel(frame_paginacao, text="Página 1 de 1", font=FONT_TXT)
    lbl_paginacao.pack(side="left", fill="x", expand=True)
    btn_proximo = ctk.CTkButton(frame_paginacao, text="Próximo ▶", width=100, height=32, fg_color="#3F3F46", hover_color="#52525B", command=lambda: mudar_pagina(1))
    btn_proximo.pack(side="right", padx=20)

    # AREA DO MODO TABELA
    frame_tabela_wrapper = ctk.CTkFrame(tab_list, fg_color="transparent")
    frame_tv_interna = ctk.CTkFrame(frame_tabela_wrapper, fg_color="transparent")
    frame_tv_interna.pack(fill="both", expand=True)

    scroll_y = ctk.CTkScrollbar(frame_tv_interna)
    scroll_y.pack(side="right", fill="y")

    colunas = ("frota", "placa", "modelo", "diaria", "km", "oleo", "status")
    tv = ttk.Treeview(frame_tv_interna, columns=colunas, show="headings", yscrollcommand=scroll_y.set)
    scroll_y.configure(command=tv.yview)

    tv.heading("frota", text="Frota")
    tv.heading("placa", text="Placa")
    tv.heading("modelo", text="Modelo")
    tv.heading("diaria", text="Diária (R$)")
    tv.heading("km", text="KM Atual")
    tv.heading("oleo", text="Próx. Óleo")
    tv.heading("status", text="Status")

    tv.column("frota", width=80, anchor="center")
    tv.column("placa", width=120, anchor="center")
    tv.column("modelo", width=250, anchor="w")
    tv.column("diaria", width=100, anchor="center")
    tv.column("km", width=100, anchor="center")
    tv.column("oleo", width=100, anchor="center")
    tv.column("status", width=150, anchor="center")
    tv.tag_configure('par', background="#18181B")
    tv.tag_configure('impar', background="#27272A")
    tv.pack(side="left", fill="both", expand=True)

    frame_acoes_tabela = ctk.CTkFrame(frame_tabela_wrapper, fg_color=COR_BOX_INFO, corner_radius=8, height=60)
    frame_acoes_tabela.pack(fill="x", pady=(10, 0))
    frame_acoes_tabela.pack_propagate(False)

    btn_t_detalhes = ctk.CTkButton(frame_acoes_tabela, text="📄 Ficha Técnica", state="disabled", fg_color="#3F3F46", command=lambda: mostrar_detalhes_ui(obter_carro_tabela()))
    btn_t_detalhes.pack(side="left", padx=10, pady=15)
    btn_t_editar = ctk.CTkButton(frame_acoes_tabela, text="✏️ Editar", state="disabled", fg_color="#2563EB", command=lambda: preparar_edicao(obter_carro_tabela()))
    btn_t_editar.pack(side="left", padx=5, pady=15)
    btn_t_vender = ctk.CTkButton(frame_acoes_tabela, text="🤝 Vender", state="disabled", fg_color="#8B5CF6", command=lambda: vender_carro_ui(obter_carro_tabela()))
    btn_t_vender.pack(side="left", padx=5, pady=15)
    btn_t_oleo = ctk.CTkButton(frame_acoes_tabela, text="🛢️ Lançar Óleo", state="disabled", fg_color="#3F3F46", command=lambda: registrar_oleo_ui(obter_carro_tabela()))
    btn_t_oleo.pack(side="right", padx=10, pady=15)
    btn_t_manut = ctk.CTkButton(frame_acoes_tabela, text="🔧 Manutenção", state="disabled", fg_color="#3F3F46", command=lambda: alternar_manutencao_ui(obter_carro_tabela()))
    btn_t_manut.pack(side="right", padx=5, pady=15)

    # RENDERS DO HISTÓRICO DE VENDAS
    sc_vendidos = ctk.CTkScrollableFrame(tab_vendidos, fg_color="transparent")
    sc_vendidos.pack(fill="both", expand=True, pady=10)
    for v in controller.listar_veiculos_vendidos():
        card_v = ctk.CTkFrame(sc_vendidos, fg_color=COR_CARD, corner_radius=12); card_v.pack(pady=8, padx=5, fill="x")
        info_v = ctk.CTkFrame(card_v, fg_color="transparent"); info_v.pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(info_v, text=f"[{v.carro.numero_frota}] {v.carro.modelo} ({v.carro.placa})" if v.carro.numero_frota else f"{v.carro.modelo} ({v.carro.placa})", font=FONT_CARD_TIT, text_color="#EF4444").pack(anchor="w")
        ctk.CTkLabel(info_v, text=f"Comprador: {v.comprador}   •   Data da Venda: {v.data_venda.strftime('%d/%m/%Y')}\nValor Fechado: R$ {v.valor_venda:.2f}   •   Nota Promissória: {'Sim' if v.nota_promissoria else 'Não'}", font=FONT_TXT, text_color=COR_TEXTO_SEC, justify="left").pack(anchor="w", pady=(5,0))

    # DESIGN DO FORMULÁRIO DE CADASTRO / EDIÇÃO
    form = ctk.CTkFrame(tab_new, fg_color=COR_CARD, corner_radius=12)
    form.pack(pady=20, padx=20, fill="both", expand=True)
    container_form = ctk.CTkFrame(form, fg_color="transparent")
    container_form.pack(pady=20)
    L_W = 220 
    
    ctk.CTkLabel(container_form, text="Nº da Frota:", font=FONT_TXT).grid(row=0, column=0, pady=8, padx=10, sticky="e")
    entry_frota = ctk.CTkEntry(container_form, width=L_W, height=35); entry_frota.grid(row=0, column=1, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Modelo:", font=FONT_TXT).grid(row=1, column=0, pady=8, padx=10, sticky="e")
    entry_modelo = ctk.CTkEntry(container_form, width=L_W, height=35); entry_modelo.grid(row=1, column=1, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Placa:", font=FONT_TXT).grid(row=2, column=0, pady=8, padx=10, sticky="e")
    entry_placa = ctk.CTkEntry(container_form, width=L_W, height=35); entry_placa.grid(row=2, column=1, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Cor:", font=FONT_TXT).grid(row=3, column=0, pady=8, padx=10, sticky="e")
    entry_cor = ctk.CTkEntry(container_form, width=L_W, height=35); entry_cor.grid(row=3, column=1, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Ano:", font=FONT_TXT).grid(row=4, column=0, pady=8, padx=10, sticky="e")
    entry_ano = ctk.CTkEntry(container_form, width=L_W, height=35); entry_ano.grid(row=4, column=1, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Chassi:", font=FONT_TXT).grid(row=5, column=0, pady=8, padx=10, sticky="e")
    entry_chassi = ctk.CTkEntry(container_form, width=L_W, height=35); entry_chassi.grid(row=5, column=1, pady=8, padx=10)
    
    ctk.CTkLabel(container_form, text="Odômetro (KM):", font=FONT_TXT).grid(row=0, column=2, pady=8, padx=10, sticky="e")
    entry_km = ctk.CTkEntry(container_form, width=L_W, height=35); entry_km.grid(row=0, column=3, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Valor da Diária (R$):", font=FONT_TXT).grid(row=1, column=2, pady=8, padx=10, sticky="e")
    entry_tarifa = ctk.CTkEntry(container_form, width=L_W, height=35); entry_tarifa.grid(row=1, column=3, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Nº Taxímetro:", font=FONT_TXT).grid(row=2, column=2, pady=8, padx=10, sticky="e")
    entry_num_taxi = ctk.CTkEntry(container_form, width=L_W, height=35); entry_num_taxi.grid(row=2, column=3, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Marca Taxímetro:", font=FONT_TXT).grid(row=3, column=2, pady=8, padx=10, sticky="e")
    entry_marca_taxi = ctk.CTkEntry(container_form, width=L_W, height=35); entry_marca_taxi.grid(row=3, column=3, pady=8, padx=10)
    ctk.CTkLabel(container_form, text="Data Aferição:", font=FONT_TXT).grid(row=4, column=2, pady=8, padx=10, sticky="e")
    entry_data_afer = ctk.CTkEntry(container_form, width=L_W, height=35, placeholder_text="DD/MM/AAAA"); entry_data_afer.grid(row=4, column=3, pady=8, padx=10); entry_data_afer.bind("<KeyRelease>", app.mascara_data_geral)
    ctk.CTkLabel(container_form, text="Obs / Manutenção:", font=FONT_TXT).grid(row=5, column=2, pady=8, padx=10, sticky="e")
    entry_obs = ctk.CTkEntry(container_form, width=L_W, height=35, placeholder_text="Ex: Trocar correia..."); entry_obs.grid(row=5, column=3, pady=8, padx=10)
    
    box_foto = ctk.CTkFrame(container_form, fg_color="transparent")
    box_foto.grid(row=6, column=0, columnspan=4, pady=(20, 0))
    ctk.CTkLabel(box_foto, text="Fotografia:", font=FONT_TXT).pack(side="left", padx=10)
    ctk.CTkButton(box_foto, text="Carregar", fg_color="#3F3F46", height=30, width=80, command=executar_upload_foto).pack(side="left")
    lbl_nome_foto = ctk.CTkLabel(box_foto, text="Nenhum anexo", text_color=COR_TEXTO_SEC, font=FONT_TXT)
    lbl_nome_foto.pack(side="left", padx=15)
    
    app.btn_salvar_carro = ctk.CTkButton(container_form, text="Salvar Ativo na Frota", fg_color="#10B981", hover_color="#059669", height=45, corner_radius=8, font=FONT_CARD_TIT, command=salvar_carro)
    app.btn_salvar_carro.grid(row=7, column=0, columnspan=4, pady=25)

    atualizar_exibicao_geral()