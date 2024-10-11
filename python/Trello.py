from trello import TrelloClient
from datetime import datetime, timedelta  
from Email import Email


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
        labels.append(self.board.add_label("Alta", color="red"))
        labels.append(self.board.add_label("Média", color="yellow"))
        labels.append(self.board.add_label("Baixa", color="green"))
        return labels

    
    def create_card(self, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist):
        
        trello_list = self.board.get_list(list_id)
    
        superiors_emails = [email.strip() for email in emails.split('-')]
        superiors = [name.strip() for name in names.split('-')]

        card = trello_list.add_card(
            name=non_conformity, 
            due=(datetime.now() + timedelta(days=int(deadline))).isoformat(),
            desc=f'Não Conformidade: {non_conformity}\n'
                f'Responsável: {responsible}\n'
                f'Prioridade: {classification}\n'
                f'Prazo (dias): {deadline}\n'
                f'Data de Início: {datetime.now().strftime("%d/%m/%Y")}\n'
                f'Nº de Escalonamento: 0\n'
                f'Superiores: {" -> ".join(superiors)}' 
        )
                
        if classification == 'Alta':
            label = self.classification_labels[0]
            
        elif classification == 'Média':
            label = self.classification_labels[1]

        else:
            label = self.classification_labels[2]
        
        card.add_label(label)
        card = self.Card(card,non_conformity,deadline,responsible,classification,superiors, email, superiors_emails, 0)
        self.cards.append(card)
        
        self.send_email(obj_email, email, "Solicitação de Resolução de Não Conformidade", superiors[0], classification,
                        non_conformity, checklist.auditor_name, 0, checklist, responsible, datetime.now().strftime("%d/%m/%Y"),
                        (datetime.now() + timedelta(days=int(deadline))).strftime("%d/%m/%Y"), deadline)


    def get_label_priority(self, card):
        priority_map = {
            'red': 0,    
            'yellow': 1, 
            'green': 2   
        }
        for label in card.labels:
            if label.color in priority_map:
                return priority_map[label.color]
        return float('inf') 

    def organize_cards(self, list_id):
        cards = self.board.get_list(list_id).list_cards()
        sorted_cards = sorted(cards, key=self.get_label_priority)

        for index, card in enumerate(sorted_cards):
            card.set_pos(index + 1)

    
    def checking_deadline(self):
        today = datetime.now().date()
        
        for card in self.cards:
            if card.card.due_date.date() == today:
                card.card.comment(f"Lembrete: O prazo de entrega é hoje, verifique se obteve resposta no seu e-mail.")
            
            elif card.card.due_date.date() == today + timedelta(days=1):
                card.card.comment(f"Lembrete: O prazo de entrega é amanhã, verifique se obteve resposta no seu e-mail.")
            
            elif card.card.due_date.date() < today:
                card.card.comment(f"Lembrete: O prazo de entrega foi estourado.")
    
    
    def feedback_update(self,list_id, number_of_lines, non_conformities, checklist):
        trello_list = self.board.get_list(list_id)
        
        adherence_percentage = ((len(non_conformities) / number_of_lines) * 100 if number_of_lines != 0 else 0)
        if self.feedback_card == None:
            self.feedback_card = trello_list.add_card(
                name="Feedback Geral", 
                desc=f'Nome do Projeto: {checklist.project_name}\n'
                    f'Nome do Artefato: {checklist.artefact_name}\n'
                    f'Auditor: {checklist.auditor_name}\n'
                    f'Atualizado em: {datetime.now().strftime("%d/%m/%Y")}\n'
                    f'Total de Itens: {number_of_lines}\n'
                    f'Itens não-conformes: {len(non_conformities)}\n'
                    f'Aderência: {adherence_percentage:.2f}%\n'
            )
        else:
            self.feedback_card.set_description(  
                f'Nome do Projeto: {checklist.project_name}\n'
                f'Nome do Artefato: {checklist.artefact_name}\n'
                f'Auditor: {checklist.auditor_name}\n'
                f'Atualizado em: {datetime.now().strftime("%d/%m/%Y")}\n'
                f'Total de Itens: {number_of_lines}\n'
                f'Itens não-conformes: {len(non_conformities)}\n'
                f'Aderência: {adherence_percentage:.2f}%\n'
            )
        
    
    def send_email(self,email, receiver_email, subject, immediate_superior, classification, non_conformity, auditor, escalation_number, checklist, responsible, date, resolution_date, deadline):
        body = f"""
Prezado(a) {responsible},

Segue abaixo as informações da solicitação de resolução de não conformidade no projeto '{checklist.project_name}':

Detalhes da Solicitação:
- Responsável: {responsible}
- Data da Solicitação: {date}
- Prazo de Resolução: {deadline} dia(s)
- Data da Solução: {resolution_date}
- Número de Escalonamentos: {escalation_number}
- Artefato: {checklist.artefact_name}
- RQA Responsável: {auditor}

Descrição da Não Conformidade: {non_conformity}

Prioridade: {classification}
Superior Imediato: {immediate_superior}

Aguardo a resolução conforme o prazo estabelecido. Caso tenha alguma dúvida ou necessite de mais informações, favor entrar em contato.
Caso deseje apresentar uma contestação, favor fazê-lo no prazo de 24 horas úteis.

Atenciosamente,

{auditor},
Auditor(a) Interno(a)
        """

        email.send_email(receiver_email, subject, body)

    

    
    class Card:
        
        def __init__(self, card, non_conformity, deadline, responsible, classification, superiors, responsible_email, superiors_emails, escalation_number):
            self.non_conformity = non_conformity
            self.deadline = deadline
            self.responsible = responsible
            self.classification = classification
            self.superiors = superiors
            self.responsible_email = responsible_email
            self.superiors_emails = superiors_emails
            self.escalation_number = escalation_number
            self.card = card
    
