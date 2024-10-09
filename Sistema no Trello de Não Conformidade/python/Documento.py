import csv

class Documento:

    def __init__(self, nome_do_arq):
        self.nome_do_arq = nome_do_arq
        self.nao_conformidades = self.abrir_arq()
        
    
    def abrir_arq(self):
        nao_conformidades = []
        with open(self.nome_do_arq, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            next(leitor)
            nao_conformidades = [linha for linha in leitor if linha[1] == "Não Conforme"]
            return nao_conformidades
        
   

        
