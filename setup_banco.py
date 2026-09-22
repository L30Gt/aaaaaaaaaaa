from database import engine, Base, SessionLocal
from models import Tarifa, TipoInfracao

import models 

def iniciar_banco():
    print("Criando o arquivo do banco de dados e as tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

    db = SessionLocal()
    
   
    if db.query(Tarifa).count() == 0:
        print("Inserindo Tarifas base...")
        tarifas = [
            Tarifa(descricao="PRISMA", valor_diaria=150.00),
            Tarifa(descricao="ONIX", valor_diaria=160.00),
            Tarifa(descricao="SPIN", valor_diaria=160.00),
            Tarifa(descricao="FIAT CRONOS AUTOMATICO", valor_diaria=180.00),
            Tarifa(descricao="SPIN GAS", valor_diaria=220.00)
        ]
        db.add_all(tarifas)
        db.commit()

    if db.query(TipoInfracao).count() == 0:
        print("Inserindo Infrações base...")
        infracoes = [
            TipoInfracao(artigo="Art. 162, I", descricao="Dirigir sem possuir CNH", gravidade="Gravíssima", pontos=7, valor_base=880.41),
            TipoInfracao(artigo="Art. 165", descricao="Dirigir sob influência de álcool", gravidade="Gravíssima", pontos=7, valor_base=2934.70),
            TipoInfracao(artigo="Art. 167", descricao="Deixar de usar cinto de segurança", gravidade="Grave", pontos=5, valor_base=195.23)
        ]
        db.add_all(infracoes)
        db.commit()

    db.close()
    print("Configuração inicial concluída! O banco glvf.db está pronto para uso.")

if __name__ == "__main__":
    iniciar_banco()