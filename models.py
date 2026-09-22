from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Tarifa(Base):
    __tablename__ = "tarifas"
    id_tarifa = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(100))
    valor_diaria = Column(Float, nullable=False)
    carros = relationship("Carro", back_populates="tarifa")

class Carro(Base):
    __tablename__ = "carros"
    id_carro = Column(Integer, primary_key=True, autoincrement=True)
    numero_frota = Column(String(20), nullable=True)
    placa = Column(String(10), unique=True)
    modelo = Column(String(100))
    cor = Column(String(50), nullable=True)
    ano = Column(String(4), nullable=True)
    chassi = Column(String(50), nullable=True)
    numero_taximetro = Column(String(50), nullable=True)
    marca_taximetro = Column(String(50), nullable=True)
    data_afericao_taximetro = Column(String(20), nullable=True)
    observacoes = Column(String(255), nullable=True)
    
    status = Column(String(20), default='DISPONIVEL') 
    id_tarifa = Column(Integer, ForeignKey("tarifas.id_tarifa"))
    km_atual = Column(Integer, default=0)
    km_ultima_troca = Column(Integer, default=0)
    km_proxima_troca = Column(Integer, default=10000)
    foto = Column(String(255), nullable=True)

    tarifa = relationship("Tarifa", back_populates="carros")
    alvaras = relationship("Alvara", back_populates="carro", cascade="all, delete-orphan")
    contratos = relationship("Contrato", back_populates="carro")
    lancamentos = relationship("Financeiro", back_populates="carro")
    vendas = relationship("VendaVeiculo", back_populates="carro")
    multas = relationship("MultaAplicada", back_populates="carro")
    eventos = relationship("EventoCarro", back_populates="carro", cascade="all, delete-orphan")


class EventoCarro(Base):
    __tablename__ = "eventos_carro"
    id_evento = Column(Integer, primary_key=True, autoincrement=True)
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=False)
    data_hora = Column(DateTime, default=datetime.now)
    tipo = Column(String(50), default="MANUTENCAO")
    descricao = Column(String(500), nullable=False)
    carro = relationship("Carro", back_populates="eventos")

class Motorista(Base):
    __tablename__ = "motoristas"
    id_motorista = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(150), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    cnh = Column(String(20))
    telefone = Column(String(20))
    status = Column(String(20), default='ATIVO')
    data_cadastro = Column(DateTime, default=datetime.now)

    contratos = relationship("Contrato", back_populates="motorista")
    observacoes = relationship("ObservacaoMotorista", back_populates="motorista", cascade="all, delete-orphan")
    multas = relationship("MultaAplicada", back_populates="motorista")

class Contrato(Base):
    __tablename__ = "contratos"
    id_contrato = Column(Integer, primary_key=True, autoincrement=True)
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=False)
    id_motorista = Column(Integer, ForeignKey("motoristas.id_motorista"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=True)
    valor_acordado = Column(Float)

    carro = relationship("Carro", back_populates="contratos")
    motorista = relationship("Motorista", back_populates="contratos")

class Financeiro(Base):
    __tablename__ = "financeiro"
    id_lancamento = Column(Integer, primary_key=True, autoincrement=True)
    data_lancamento = Column(DateTime, default=datetime.now)
    tipo = Column(String(10), nullable=False) 
    categoria = Column(String(50), nullable=False) 
    valor = Column(Float, nullable=False)
    descricao = Column(String(255))
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=True)
    carro = relationship("Carro", back_populates="lancamentos")

class Alvara(Base):
    __tablename__ = "alvaras"
    id_alvara = Column(Integer, primary_key=True, autoincrement=True)
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=False)
    numero_doc = Column(String(50))
    data_vencimento = Column(Date)
    ativo = Column(Boolean, default=True)
    carro = relationship("Carro", back_populates="alvaras")

class TipoInfracao(Base):
    __tablename__ = "tipos_infracao"
    id_infracao = Column(Integer, primary_key=True, autoincrement=True)
    artigo = Column(String(50))
    descricao = Column(String(255))
    gravidade = Column(String(20))
    pontos = Column(Integer)
    valor_base = Column(Float)
    multas = relationship("MultaAplicada", back_populates="infracao")

class MultaAplicada(Base):
    __tablename__ = "multas_aplicadas"
    id_multa = Column(Integer, primary_key=True, autoincrement=True)
    id_motorista = Column(Integer, ForeignKey("motoristas.id_motorista"), nullable=False)
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=False)
    id_infracao = Column(Integer, ForeignKey("tipos_infracao.id_infracao"), nullable=False)
    data_infracao = Column(DateTime, nullable=False)
    valor_cobrado = Column(Float)
    status_pagamento = Column(String(20), default='PENDENTE')

    motorista = relationship("Motorista", back_populates="multas")
    carro = relationship("Carro", back_populates="multas")
    infracao = relationship("TipoInfracao", back_populates="multas")

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    id_log = Column(Integer, primary_key=True, autoincrement=True)
    tabela_afetada = Column(String(50))
    acao = Column(String(50))
    detalhes = Column(String(255))
    data_hora = Column(DateTime, default=datetime.now)

class ObservacaoMotorista(Base):
    __tablename__ = "observacoes_motorista"
    id_observacao = Column(Integer, primary_key=True, autoincrement=True)
    id_motorista = Column(Integer, ForeignKey("motoristas.id_motorista"), nullable=False)
    texto = Column(String(500), nullable=False)
    data_hora = Column(DateTime, default=datetime.now)
    motorista = relationship("Motorista", back_populates="observacoes")

class VendaVeiculo(Base):
    __tablename__ = "vendas_veiculos"
    id_venda = Column(Integer, primary_key=True, autoincrement=True)
    id_carro = Column(Integer, ForeignKey("carros.id_carro"), nullable=False)
    comprador = Column(String(150), nullable=False) 
    valor_venda = Column(Float, nullable=False)
    nota_promissoria = Column(Boolean, default=False)
    data_venda = Column(DateTime, default=datetime.now)
    carro = relationship("Carro", back_populates="vendas")