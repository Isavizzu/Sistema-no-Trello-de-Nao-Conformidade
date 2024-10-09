from trello import TrelloClient
from datetime import datetime, timedelta  
from Document import Document

class Trello:
    
    def __init__(self, API_KEY, API_SECRET, TOKEN, board):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.TOKEN = TOKEN
        self.client = TrelloClient(
            api_key= self.API_KEY,
            api_secret= self.API_SECRET,
            token= self.TOKEN,
        )
        self.board = self.client.get_board(board)
        self.classification_labels = self.create_classification_labels()
        self.cards = []
        self.feedback_card = None  
        
        
    def create_classification_labels(self):
        labels = []
        labels.append(labels.append(self.board.add_label("Alta", color="red")))
        labels.append(self.board.add_label("Média", color="yellow"))
        labels.append(self.board.add_label("Baixa", color="green"))
        return labels

    
    def create_card(self, list_id, non_conformity, deadline, responsible, classification, names, emails, email):
        trello_list = self.board.get_list(list_id)
    
        superiors_emails = [email.strip() for email in emails.split('-')]
        superiors = [name.strip() for name in names.split('-')]
        
        card = self.Card(non_conformity,deadline,responsible,classification,superiors, email, superiors_emails, 0)
        self.cards.append(card)

        new_card = trello_list.add_card(
            name=card.non_conformity, 
            start=datetime.now().isoformat(),
            due=(datetime.now() + timedelta(days=card.deadline)).isoformat(), 
            desc=f'Não Conformidade: {card.non_conformity}\n'
                f'Responsável: {card.responsible}\n'
                f'Classificação: {card.classification}\n'
                f'Prazo (dias): {card.deadline}\n'
                f'Nº de Escalonamento: 0\n'
                f'Superiores: {" -> ".join(card.superiors)}' 
        )
        
        if card.classification == 'Alta':
            label = self.classification_labels[0]
            
        elif card.classification == 'Média':
            label = self.classification_labels[1]

        else:
            label = self.classification_labels[2]
        
        new_card.add_label(label)
    
    
    def feedback_update(self,list_id, number_of_lines, non_conformities):
        trello_list = self.board.get_list(list_id)
        
        adherence_percentage = ((len(non_conformities) / number_of_lines) * 100 if number_of_lines != 0 else 0)
        if self.feedback_card == None:
            self.feedback_card = trello_list.add_card(
                name="Feedback Geral", 
                desc=f'Atualizado em: {datetime.now().isoformat(),}\n'
                    f'Total de Itens: {number_of_lines}\n'
                    f'Itens não-conformes: {len(non_conformities)}\n'
                    f'Aderência: {adherence_percentage}%\n'
            )
        else:
            self.feedback_card.set_description(  
            f'Atualizado em: {datetime.now().isoformat()}\n'
            f'Total de Itens: {number_of_lines}\n'
            f'Itens não-conformes: {len(non_conformities)}\n'
            f'Aderência: {adherence_percentage}%\n'
        )
        
    
    class Card:
        
        def __init__(self, non_conformity, deadline, responsible, classification, superiors, responsible_email, superiors_emails, escalation_number):
            self.non_conformity = non_conformity
            self.deadline = deadline
            self.responsible = responsible
            self.classification = classification
            self.superiors = superiors
            self.responsible_email = responsible_email
            self.superiors_emails = superiors_emails
            self.escalation_number = escalation_number
    
