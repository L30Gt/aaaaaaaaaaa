import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def renderizar(frame_pai, controller, app):
    COR_CARD = "#18181B"
    COR_TEXTO_SEC = "#A1A1AA"
    FONT_TITULO = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    FONT_VALOR = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
    
    top = ctk.CTkFrame(frame_pai, fg_color="transparent")
    top.pack(fill="x", padx=30, pady=(20, 10))
    ctk.CTkLabel(top, text="Indicadores Financeiros", font=FONT_TITULO).pack(side="left")

    resumo = controller.obter_resumo_financeiro()
    
    # Painel de Cards
    dash = ctk.CTkFrame(frame_pai, fg_color="transparent")
    dash.pack(fill="x", padx=25, pady=10)
    
    dados_cards = [
        ("Faturamento Total (Entradas)", f"R$ {resumo['entradas']:.2f}", "#10B981"), 
        ("Despesas/Multas (Saídas)", f"R$ {resumo['saidas']:.2f}", "#EF4444"), 
        ("Saldo Líquido", f"R$ {resumo['saldo']:.2f}", "#3B82F6")
    ]
    
    for titulo, valor, cor in dados_cards:
        card = ctk.CTkFrame(dash, fg_color=COR_CARD, corner_radius=12)
        card.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=14), text_color=COR_TEXTO_SEC).pack(pady=(15, 2))
        ctk.CTkLabel(card, text=valor, font=FONT_VALOR, text_color=cor).pack(pady=(0, 15))

    # Gráfico
    gf = ctk.CTkFrame(frame_pai, fg_color=COR_CARD, corner_radius=12)
    gf.pack(fill="both", expand=True, padx=30, pady=15)
    ctk.CTkLabel(gf, text="Lucro Líquido Mensal", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

    meses, valores = controller.obter_dados_cronologicos_faturamento()
    
    fig = Figure(figsize=(7, 2.5), dpi=100)
    fig.patch.set_facecolor(COR_CARD)
    ax = fig.add_subplot(111)
    ax.set_facecolor(COR_CARD)
    ax.bar(meses, valores, color='#3B82F6', width=0.6, edgecolor='#2563EB', linewidth=1)
    ax.tick_params(colors='white')
    
    # Limpar bordas do gráfico para um visual muito mais moderno
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#4B5563')
    
    canvas = FigureCanvasTkAgg(fig, master=gf)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))