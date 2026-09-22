from database import get_db
from models import Carro, Tarifa, Motorista, Contrato, Financeiro, Alvara, LogAuditoria, ObservacaoMotorista, VendaVeiculo, TipoInfracao, MultaAplicada, EventoCarro
from sqlalchemy.orm import joinedload
from datetime import datetime, date
import os
import webbrowser
from fpdf import FPDF

class CarroController:
    # ==========================================
    # SISTEMA DE ALERTAS
    # ==========================================
    def obter_alertas(self):
        db = next(get_db())
        alertas = []
        carros = db.query(Carro).filter(Carro.status != "VENDIDO").all()
        hoje = date.today()
        
        for c in carros:
            restante = c.km_proxima_troca - c.km_atual
            if restante <= 1000:
                alertas.append(f"🛢️ {c.modelo} ({c.placa}): Faltam {restante} km para a troca de óleo!")
                
            alvara_ativo = next((a for a in c.alvaras if a.ativo), None)
            if alvara_ativo and alvara_ativo.data_vencimento:
                dias = (alvara_ativo.data_vencimento - hoje).days
                if dias < 0:
                    alertas.append(f"🛑 {c.modelo} ({c.placa}): Alvará VENCIDO há {abs(dias)} dias!")
                elif dias <= 30:
                    alertas.append(f"⚠️ {c.modelo} ({c.placa}): Alvará vence em {dias} dias!")
            elif not alvara_ativo:
                alertas.append(f"📄 {c.modelo} ({c.placa}): Sem alvará registrado!")
                
        return alertas

    # ==========================================
    # MÓDULO CARROS E VENDAS
    # ==========================================
    def listar_carros(self):
        db = next(get_db())
        return db.query(Carro).options(joinedload(Carro.tarifa)).all()

    def listar_carros_disponiveis(self):
        db = next(get_db())
        return db.query(Carro).options(joinedload(Carro.tarifa)).filter(Carro.status == "DISPONIVEL").all()

    def listar_tarifas(self):
        db = next(get_db())
        return db.query(Tarifa).all()

    def listar_veiculos_vendidos(self):
        db = next(get_db())
        return db.query(VendaVeiculo).options(joinedload(VendaVeiculo.carro)).order_by(VendaVeiculo.data_venda.desc()).all()

    def adicionar_carro(self, numero_frota, placa, modelo, valor_diaria, km_atual, cor, ano, chassi, num_taxi, marca_taxi, data_afer, obs, foto_caminho=None):
        db = next(get_db())
        try: 
            km_int = int(km_atual)
            valor_float = float(str(valor_diaria).replace(",", "."))
        except: 
            return False, "A KM e o Valor da Diária devem ser numéricos."
            
        tarifa = db.query(Tarifa).filter(Tarifa.valor_diaria == valor_float).first()
        if not tarifa:
            tarifa = Tarifa(descricao="Diária Padrão", valor_diaria=valor_float)
            db.add(tarifa)
            db.commit()
            db.refresh(tarifa)

        novo_carro = Carro(
            numero_frota=numero_frota, placa=placa.upper(), modelo=modelo.upper(),
            cor=cor.upper(), ano=ano, chassi=chassi.upper(), numero_taximetro=num_taxi, 
            marca_taximetro=marca_taxi.upper(), data_afericao_taximetro=data_afer, 
            observacoes=obs, id_tarifa=tarifa.id_tarifa, km_atual=km_int, 
            km_ultima_troca=km_int, km_proxima_troca=km_int+10000, status="DISPONIVEL", foto=foto_caminho
        )
        try: 
            db.add(novo_carro)
            db.commit()
            return True, "Veículo registrado com sucesso!"
        except: 
            db.rollback()
            return False, "Erro ao registrar. Placa já existe?"

    def atualizar_carro(self, id_carro, numero_frota, placa, modelo, valor_diaria, km_atual, cor, ano, chassi, num_taxi, marca_taxi, data_afer, obs, foto_caminho=None):
        db = next(get_db())
        try: 
            km_int = int(km_atual)
            valor_float = float(str(valor_diaria).replace(",", "."))
        except: 
            return False, "KM ou Valor inválidos."
            
        carro = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        if not carro: return False, "Veículo não encontrado."
            
        tarifa = db.query(Tarifa).filter(Tarifa.valor_diaria == valor_float).first()
        if not tarifa:
            tarifa = Tarifa(descricao="Diária Padrão", valor_diaria=valor_float)
            db.add(tarifa)
            db.commit()
            db.refresh(tarifa)

        try:
            carro.numero_frota = numero_frota
            carro.placa = placa.upper()
            carro.modelo = modelo.upper()
            carro.cor = cor.upper()
            carro.ano = ano
            carro.chassi = chassi.upper()
            carro.numero_taximetro = num_taxi
            carro.marca_taximetro = marca_taxi.upper()
            carro.data_afericao_taximetro = data_afer
            carro.observacoes = obs
            carro.id_tarifa = tarifa.id_tarifa
            carro.km_atual = km_int
            if foto_caminho: carro.foto = foto_caminho
            db.commit()
            return True, "Veículo atualizado com sucesso!"
        except Exception as e: 
            db.rollback()
            return False, str(e)

    def registrar_troca_oleo(self, id_carro, km_atual):
        db = next(get_db())
        carro = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        if carro: 
            carro.km_atual = km_atual 
            carro.km_ultima_troca = km_atual
            carro.km_proxima_troca = km_atual + 10000
            db.commit()
            return True
        return False

    def alternar_manutencao(self, id_carro):
        db = next(get_db())
        carro = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        if not carro: return False, "Veículo não encontrado."
            
        if carro.status == "DISPONIVEL":
            carro.status = "MANUTENCAO"
            msg = "Veículo enviado para a oficina."
        elif carro.status == "MANUTENCAO":
            carro.status = "DISPONIVEL"
            msg = "Veículo liberado para locação."
        else:
            return False, "Um carro alugado não pode ir para manutenção sem ser devolvido primeiro."
        db.commit()
        return True, msg

    def processar_venda_veiculo(self, id_carro, comprador, valor_venda, usa_promissoria):
        db = next(get_db())
        try: valor_float = float(valor_venda)
        except: return False, "Preço inválido."
            
        carro = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        carro.status = "VENDIDO"
        
        db.add(VendaVeiculo(id_carro=id_carro, comprador=comprador.upper(), valor_venda=valor_float, nota_promissoria=usa_promissoria))
        tipo_n = "Promissória" if usa_promissoria else "À Vista"
        db.add(Financeiro(tipo="ENTRADA", categoria="VENDA_CARRO", valor=valor_float, descricao=f"Venda {carro.placa} ({tipo_n})", id_carro=id_carro))
        
        db.commit()
        return True, "Veículo vendido e baixado da frota!"

    # ==========================================
    # MÓDULO: LINHA DO TEMPO DO CARRO (EVENTOS)
    # ==========================================
    def adicionar_evento_carro(self, id_carro, tipo, descricao):
        db = next(get_db())
        try:
            novo_evento = EventoCarro(id_carro=id_carro, tipo=tipo.upper(), descricao=descricao)
            db.add(novo_evento)
            db.commit()
            return True, "Evento registrado no diário do veículo!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao registrar: {str(e)}"

    def listar_eventos_carro(self, id_carro):
        db = next(get_db())
        return db.query(EventoCarro).filter(EventoCarro.id_carro == id_carro).order_by(EventoCarro.data_hora.desc()).all()

    def excluir_evento_carro(self, id_evento):
        db = next(get_db())
        ev = db.query(EventoCarro).filter(EventoCarro.id_evento == id_evento).first()
        if ev:
            db.delete(ev)
            db.commit()
            return True
        return False

    # ==========================================
    # MÓDULO MOTORISTAS
    # ==========================================
    def listar_motoristas(self):
        db = next(get_db())
        return db.query(Motorista).all()

    def adicionar_motorista(self, nome, cpf, cnh, telefone, status="ATIVO"):
        db = next(get_db())
        novo = Motorista(nome_completo=nome.upper(), cpf=cpf, cnh=cnh, telefone=telefone, status=status.upper())
        try: 
            db.add(novo)
            db.commit()
            return True, "Motorista registrado!"
        except: 
            db.rollback()
            return False, "Erro. CPF duplicado?"

    def atualizar_motorista(self, id_motorista, nome, cpf, cnh, telefone, status):
        db = next(get_db())
        motorista = db.query(Motorista).filter(Motorista.id_motorista == id_motorista).first()
        if not motorista: return False, "Motorista não encontrado."
            
        try:
            motorista.nome_completo = nome.upper()
            motorista.cpf = cpf
            motorista.cnh = cnh
            motorista.telefone = telefone
            motorista.status = status.upper()
            db.commit()
            return True, "Atualizado com sucesso!"
        except: 
            db.rollback()
            return False, "Erro ao atualizar."

    def excluir_motorista(self, id_motorista):
        db = next(get_db())
        motorista = db.query(Motorista).filter(Motorista.id_motorista == id_motorista).first()
        if not motorista: return False, "Motorista não encontrado."
        
        tem_contratos = db.query(Contrato).filter(Contrato.id_motorista == id_motorista).first()
        tem_multas = db.query(MultaAplicada).filter(MultaAplicada.id_motorista == id_motorista).first()
        
        if tem_contratos or tem_multas:
            return False, f"O motorista {motorista.nome_completo} possui histórico de locações ou multas.\nPara manter o histórico financeiro intacto e evitar falhas na auditoria, você NÃO PODE excluí-lo.\n\nSugestão: Edite a ficha dele e mude o Status Contratual para INATIVO."
            
        try:
            db.delete(motorista)
            db.commit()
            return True, "O registro do motorista foi excluído permanentemente do sistema."
        except Exception as e:
            db.rollback()
            return False, f"Erro ao excluir: {str(e)}"

    def obter_resumo_motorista(self, id_motorista):
        db = next(get_db())
        motorista = db.query(Motorista).filter(Motorista.id_motorista == id_motorista).first()
        if not motorista: return None
            
        contratos = db.query(Contrato).filter(Contrato.id_motorista == id_motorista).order_by(Contrato.data_inicio.desc()).all()
        observacoes = db.query(ObservacaoMotorista).filter(ObservacaoMotorista.id_motorista == id_motorista).order_by(ObservacaoMotorista.data_hora.desc()).all()
        
        total_gasto = sum((c.valor_acordado or 0) for c in contratos)
        hist = [{"carro": f"{c.carro.modelo} ({c.carro.placa})", "data_inicio": c.data_inicio.strftime("%d/%m/%Y"), "status": "Concluído" if c.data_fim else "Ativo"} for c in contratos]
        obs = [{"id": o.id_observacao, "texto": o.texto, "data": o.data_hora.strftime("%d/%m/%Y às %H:%M")} for o in observacoes]
        
        return {
            "nome": motorista.nome_completo, 
            "cpf": motorista.cpf, 
            "telefone": motorista.telefone, 
            "status": motorista.status, 
            "total_locacoes": len(hist), 
            "total_gasto": total_gasto, 
            "historico": hist, 
            "observacoes": obs
        }

    def adicionar_observacao(self, id_motorista, texto):
        db = next(get_db())
        db.add(ObservacaoMotorista(id_motorista=id_motorista, texto=texto))
        db.commit()
        return True

    def remover_observacao(self, id_observacao):
        db = next(get_db())
        obs = db.query(ObservacaoMotorista).filter(ObservacaoMotorista.id_observacao == id_observacao).first()
        if obs: 
            db.delete(obs)
            db.commit()
            return True
        return False

    # ==========================================
    # MÓDULO LOCAÇÕES
    # ==========================================
    def listar_locacoes_ativas(self):
        db = next(get_db())
        return db.query(Contrato).options(joinedload(Contrato.carro), joinedload(Contrato.motorista)).filter(Contrato.data_fim == None).all()

    def alugar_carro(self, id_carro, id_motorista, valor_acordado):
        db = next(get_db())
        carro = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        if not carro or carro.status != "DISPONIVEL": return False, "Veículo indisponível ou em manutenção."
            
        try: valor_float = float(valor_acordado)
        except: return False, "Valor financeiro inválido."
            
        db.add(Contrato(id_carro=id_carro, id_motorista=id_motorista, valor_acordado=valor_float, data_inicio=datetime.now()))
        carro.status = "ALUGADO"
        db.add(Financeiro(tipo="ENTRADA", categoria="ALUGUEL", valor=valor_float, descricao=f"Locação {carro.placa}", id_carro=id_carro))
        
        db.commit()
        return True, "Locação registrada!"

    def devolver_carro(self, id_contrato, km_devolucao):
        db = next(get_db())
        try: km_int = int(km_devolucao)
        except: return False, "Quilometragem inválida."
            
        contrato = db.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
        if not contrato: return False, "Contrato não encontrado."
            
        carro = db.query(Carro).filter(Carro.id_carro == contrato.id_carro).first()
        contrato.data_fim = datetime.now()
        
        if carro: 
            carro.status = "DISPONIVEL"
            carro.km_atual = km_int
            
        db.commit()
        return True, "Veículo devolvido!"

    def processar_troca_veiculo(self, id_contrato_atual, id_novo_carro, km_carro_antigo):
        db = next(get_db())
        try: km_int = int(km_carro_antigo)
        except: return False, "KM inválida."
            
        contrato_atual = db.query(Contrato).filter(Contrato.id_contrato == id_contrato_atual).first()
        carro_antigo = db.query(Carro).filter(Carro.id_carro == contrato_atual.id_carro).first()
        carro_novo = db.query(Carro).filter(Carro.id_carro == id_novo_carro).first()
        
        if not carro_novo or carro_novo.status != "DISPONIVEL": return False, "Novo veículo indisponível."
            
        contrato_atual.data_fim = datetime.now()
        carro_antigo.status = "DISPONIVEL"
        carro_antigo.km_atual = km_int
        
        db.add(Contrato(id_carro=id_novo_carro, id_motorista=contrato_atual.id_motorista, valor_acordado=0.0, data_inicio=datetime.now()))
        carro_novo.status = "ALUGADO"
        
        db.commit()
        return True, "Substituição realizada!"

    # ==========================================
    # MÓDULO ALVARÁS
    # ==========================================
    def listar_documentacao_frota(self):
        db = next(get_db())
        carros = db.query(Carro).options(joinedload(Carro.alvaras)).filter(Carro.status != "VENDIDO").all()
        frota_docs = []
        hoje = date.today()
        
        for c in carros:
            alvara_ativo = next((a for a in c.alvaras if a.ativo), None)
            
            if not alvara_ativo: 
                status = "SEM REGISTRO"
                dias_restantes = 9999
                vencimento_str = "N/A"
            else:
                vencimento = alvara_ativo.data_vencimento
                if vencimento:
                    diferenca = (vencimento - hoje).days
                    dias_restantes = diferenca
                    vencimento_str = vencimento.strftime("%d/%m/%Y")
                    if diferenca < 0: status = "VENCIDO"
                    elif diferenca <= 30: status = "VENCE EM BREVE"
                    else: status = "REGULAR"
                else: 
                    status = "SEM DATA"
                    dias_restantes = 8888
                    vencimento_str = "N/A"
                    
            nome_exibicao = f"[{c.numero_frota}] {c.modelo} - {c.placa}" if c.numero_frota else f"{c.modelo} - {c.placa}"
            
            frota_docs.append({
                "id_carro": c.id_carro, 
                "carro": nome_exibicao, 
                "numero_doc": alvara_ativo.numero_doc if alvara_ativo else "N/A", 
                "vencimento": vencimento_str, 
                "status": status, 
                "dias_restantes": dias_restantes
            })
            
        return frota_docs

    def registrar_alvara(self, id_carro, numero_doc, data_vencimento_str):
        db = next(get_db())
        try: vencimento_date = datetime.strptime(data_vencimento_str, "%d/%m/%Y").date()
        except: return False, "Data inválida."
            
        db.query(Alvara).filter(Alvara.id_carro == id_carro).update({"ativo": False})
        db.add(Alvara(id_carro=id_carro, numero_doc=numero_doc, data_vencimento=vencimento_date, ativo=True))
        db.commit()
        return True, "Alvará salvo!"

    # ==========================================
    # MÓDULO FINANCEIRO E PDF
    # ==========================================
    def obter_resumo_financeiro(self):
        db = next(get_db())
        lancamentos = db.query(Financeiro).all()
        entradas = sum(l.valor for l in lancamentos if l.tipo == "ENTRADA")
        saidas = sum(l.valor for l in lancamentos if l.tipo == "SAIDA")
        return {"entradas": entradas, "saidas": saidas, "saldo": entradas - saidas}

    def listar_extrato(self):
        db = next(get_db())
        return db.query(Financeiro).options(joinedload(Financeiro.carro)).order_by(Financeiro.data_lancamento.desc()).all()

    def registrar_lancamento(self, tipo, categoria, valor, descricao, id_carro=None):
        db = next(get_db())
        try: valor_float = float(valor)
        except: return False, "Preço inválido."
            
        db.add(Financeiro(tipo=tipo, categoria=categoria, valor=valor_float, descricao=descricao, id_carro=id_carro))
        db.commit()
        return True, "Lançamento efetuado!"

    def excluir_lancamento(self, id_lancamento):
        db = next(get_db())
        lancamento = db.query(Financeiro).filter(Financeiro.id_lancamento == id_lancamento).first()
        if not lancamento: return False, "Não encontrado."
            
        db.add(LogAuditoria(tabela_afetada="financeiro", acao="EXCLUSAO", detalhes=f"Excluiu {lancamento.tipo}: R$ {lancamento.valor:.2f} ({lancamento.descricao})"))
        db.delete(lancamento)
        db.commit()
        return True, "Excluído."

    def obter_dados_cronologicos_faturamento(self):
        db = next(get_db())
        lancamentos = db.query(Financeiro).all()
        fluxo = {"Jan": 0, "Fev": 0, "Mar": 0, "Abr": 0, "Mai": 0, "Jun": 0, "Jul": 0, "Ago": 0, "Set": 0, "Out": 0, "Nov": 0, "Dez": 0}
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        
        for l in lancamentos:
            nome_mes = meses[l.data_lancamento.month - 1]
            if l.tipo == "ENTRADA": 
                fluxo[nome_mes] += l.valor
            else: 
                fluxo[nome_mes] -= l.valor
                
        return list(fluxo.keys()), list(fluxo.values())

    def exportar_relatorio_caixa_pdf(self):
        db = next(get_db())
        lancamentos = db.query(Financeiro).order_by(Financeiro.data_lancamento.desc()).all()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="Extrato Oficial de Caixa - GLV", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 10, "Data", border=1, align='C')
        pdf.cell(25, 10, "Tipo", border=1, align='C')
        pdf.cell(35, 10, "Categoria", border=1, align='C')
        pdf.cell(80, 10, "Descricao", border=1, align='C')
        pdf.cell(25, 10, "Valor (R$)", border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", '', 9)
        for l in lancamentos:
            pdf.cell(25, 8, l.data_lancamento.strftime('%d/%m/%Y'), border=1, align='C')
            
            if l.tipo == "ENTRADA": pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(200, 0, 0)
                
            pdf.cell(25, 8, l.tipo, border=1, align='C')
            pdf.set_text_color(0, 0, 0) 
            
            pdf.cell(35, 8, l.categoria, border=1)
            desc = (l.descricao[:40] + '..') if len(l.descricao) > 40 else l.descricao
            pdf.cell(80, 8, desc, border=1)
            pdf.cell(25, 8, f"{l.valor:.2f}", border=1, align='R')
            pdf.ln()
            
        caminho = os.path.abspath("Extrato_Caixa_GLV.pdf")
        pdf.output(caminho)
        webbrowser.open(f"file://{caminho}")
        return True

    # ==========================================
    # MÓDULO MULTAS
    # ==========================================
    def listar_tipos_infracao(self):
        db = next(get_db())
        return db.query(TipoInfracao).all()

    def listar_multas_aplicadas(self):
        db = next(get_db())
        return db.query(MultaAplicada).options(joinedload(MultaAplicada.motorista), joinedload(MultaAplicada.carro), joinedload(MultaAplicada.infracao)).all()

    def registrar_multa(self, id_motorista, id_carro, id_infracao, data_str):
        db = next(get_db())
        try: d_inf = datetime.strptime(data_str, "%d/%m/%Y")
        except: return False, "Data inválida."
            
        inf = db.query(TipoInfracao).filter(TipoInfracao.id_infracao == id_infracao).first()
        mot = db.query(Motorista).filter(Motorista.id_motorista == id_motorista).first()
        car = db.query(Carro).filter(Carro.id_carro == id_carro).first()
        
        db.add(MultaAplicada(id_motorista=id_motorista, id_carro=id_carro, id_infracao=id_infracao, data_infracao=d_inf, valor_cobrado=inf.valor_base))
        db.add(Financeiro(tipo="SAIDA", categoria="MULTA", valor=inf.valor_base, descricao=f"Pagamento Multa ({car.placa}) - {mot.nome_completo}", id_carro=id_carro))
        
        db.commit()
        return True, "Multa registrada! Valor debitado do caixa."

    def quitar_multa(self, id_multa):
        db = next(get_db())
        m = db.query(MultaAplicada).options(joinedload(MultaAplicada.motorista), joinedload(MultaAplicada.carro)).filter(MultaAplicada.id_multa == id_multa).first()
        if m: 
            m.status_pagamento = "PAGO"
            db.add(Financeiro(tipo="ENTRADA", categoria="MULTA", valor=m.valor_cobrado, descricao=f"Reembolso Multa - {m.motorista.nome_completo} ({m.carro.placa})", id_carro=m.id_carro))
            db.commit()
            return True, "Multa Quitada! Valor reembolsado no caixa."
        return False, "Multa não encontrada."

    def excluir_multa(self, id_multa):
        db = next(get_db())
        m = db.query(MultaAplicada).filter(MultaAplicada.id_multa == id_multa).first()
        if m: 
            db.delete(m)
            db.commit()
            return True, "Registro arquivado."
        return False, "Multa não localizada."

    def adicionar_tipo_infracao(self, artigo, descricao, gravidade, pontos, valor_base):
        db = next(get_db())
        try:
            pt = int(pontos)
            vl = float(str(valor_base).replace(",", "."))
            novo = TipoInfracao(artigo=artigo.upper(), descricao=descricao.upper(), gravidade=gravidade.upper(), pontos=pt, valor_base=vl)
            db.add(novo)
            db.commit()
            return True, "Infração registrada no catálogo!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao registrar: {str(e)}"

    def excluir_tipo_infracao(self, id_infracao):
        db = next(get_db())
        inf = db.query(TipoInfracao).filter(TipoInfracao.id_infracao == id_infracao).first()
        if inf:
            uso = db.query(MultaAplicada).filter(MultaAplicada.id_infracao == id_infracao).first()
            if uso: 
                return False, "Não é possível apagar: existem multas associadas a este tipo no sistema."
            db.delete(inf)
            db.commit()
            return True, "Tipo de infração removido do catálogo."
        return False, "Infração não encontrada."