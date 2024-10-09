from trello import TrelloClient
from datetime import datetime, timedelta  

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
        self.classification_labels = self.create_label()
        self.cards = []        
        
        
    def create_label(self):
        labels = []
        labels.append(red_label = self.board.add_label("Alta", color="red"))
        labels.append(yellow_label = self.board.add_label("Méida", color="yellow"))
        labels.append(green_label = self.board.add_label("Baixa", color="green"))
        return labels

    
    def create_card(self, list_id, non_conformity, deadline, responsible, classification, names, emails, email):
        list = self.board.get_list(list_id)
    
        superiors_emails = [email.strip() for email in emails.split(',')]
        superiors = [name.strip() for name in names.split(',')]
        
        card = self.Card(non_conformity,deadline,responsible,classification,superiors, email, superiors_emails, 0)
        self.cards.append(card)

        list.add_card(
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
    
