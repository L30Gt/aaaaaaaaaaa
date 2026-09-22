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
    ctk.CTkLabel(top, text="Livro Caixa Oficial", font=FONT_TITULO).pack(side="left")
    

    ctk.CTkButton(top, text="🖨️ Exportar Extrato PDF", fg_color="#10B981", hover_color="#059669", height=40, corner_radius=8, font=ctk.CTkFont(weight="bold", size=14), command=controller.exportar_relatorio_caixa_pdf).pack(side="right")

    tv = ctk.CTkTabview(frame_pai, fg_color="transparent", segmented_button_selected_color="#2563EB")
    tv.pack(padx=30, fill="both", expand=True)
    te = tv.add("Histórico de Transações")
    tn = tv.add("Lançamento Manual")


    hdr = ctk.CTkFrame(te, fg_color=COR_CARD, corner_radius=8)
    hdr.pack(fill="x", pady=(10, 5), padx=5)
    ctk.CTkLabel(hdr, text="Data / Fluxo", width=120, font=FONT_TXT, text_color=COR_TEXTO_SEC).pack(side="left", padx=20, pady=10)
    ctk.CTkLabel(hdr, text="Detalhes do Registo", font=FONT_TXT, text_color=COR_TEXTO_SEC).pack(side="left", padx=15)

    sc = ctk.CTkScrollableFrame(te, fg_color="transparent")
    sc.pack(fill="both", expand=True)

    for l in controller.listar_extrato():
        item = ctk.CTkFrame(sc, fg_color=COR_CARD, corner_radius=8)
        item.pack(fill="x", pady=4, padx=5)
        
        ic = "🟢 Entrada" if l.tipo == "ENTRADA" else "🔴 Saída"
        ctk.CTkLabel(item, text=f"{ic}\n{l.data_lancamento.strftime('%d/%m/%Y')}", justify="left", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=25, pady=15)
        
        ctk.CTkLabel(item, text=f"Cat: {l.categoria}\nRef: {l.descricao}", justify="left", font=FONT_TXT).pack(side="left", padx=10)
        
        ctk.CTkButton(item, text="🗑️", width=35, height=35, corner_radius=6, fg_color="#3F3F46", text_color="#EF4444", hover_color="#7F1D1D", command=lambda id_l=l.id_lancamento: controller.excluir_lancamento(id_l) and app.carregar_tela("tela_caixa")).pack(side="right", padx=20)
        
        cor = "#10B981" if l.tipo == "ENTRADA" else "#EF4444"
        sinal = "+" if l.tipo == "ENTRADA" else "-"
        ctk.CTkLabel(item, text=f"{sinal} R$ {l.valor:.2f}", text_color=cor, font=ctk.CTkFont(size=18, weight="bold")).pack(side="right", padx=15)


    form = ctk.CTkFrame(tn, fg_color=COR_CARD, corner_radius=12)
    form.pack(pady=20, padx=20, fill="both", expand=True)
    container = ctk.CTkFrame(form, fg_color="transparent")
    container.pack(pady=40)

    ctk.CTkLabel(container, text="Fluxo:", font=FONT_TXT).grid(row=0, column=0, pady=10, padx=15, sticky="e")
    c_t = ctk.CTkComboBox(container, values=["ENTRADA", "SAIDA"], width=350, height=40, font=FONT_TXT, corner_radius=6); c_t.grid(row=0, column=1, pady=10); c_t.set("SAIDA")
    
    ctk.CTkLabel(container, text="Categoria Operacional:", font=FONT_TXT).grid(row=1, column=0, pady=10, padx=15, sticky="e")
    c_c = ctk.CTkComboBox(container, values=["MANUTENCAO", "MULTA", "LAVAGEM", "OUTROS"], width=350, height=40, font=FONT_TXT, corner_radius=6); c_c.grid(row=1, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Valor do Lançamento (R$):", font=FONT_TXT).grid(row=2, column=0, pady=10, padx=15, sticky="e")
    e_v = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6, placeholder_text="Ex: 50.00"); e_v.grid(row=2, column=1, pady=10)
    
    ctk.CTkLabel(container, text="Descrição / Justificativa:", font=FONT_TXT).grid(row=3, column=0, pady=10, padx=15, sticky="e")
    e_d = ctk.CTkEntry(container, width=350, height=40, font=FONT_TXT, corner_radius=6); e_d.grid(row=3, column=1, pady=10)
    
    def save_cx():
        if not e_v.get() or not e_d.get(): return messagebox.showwarning("Atenção", "Preencha o valor e a descrição.")
        s, m = controller.registrar_lancamento(c_t.get(), c_c.get(), e_v.get(), e_d.get())
        if s: app.carregar_tela("tela_caixa")
        else: messagebox.showerror("Erro", m)
        
    ctk.CTkButton(container, text="Efetuar Registo Financeiro", fg_color="#2563EB", hover_color="#1D4ED8", height=45, corner_radius=8, font=FONT_CARD_TIT, command=save_cx).grid(row=4, column=0, columnspan=2, pady=35)