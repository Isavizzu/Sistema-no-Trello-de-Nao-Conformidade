from trello import TrelloClient
from datetime import datetime, timedelta  
from Email import Email
import time
import pickle
import os


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
        self.cards_escalonados = []
        self.feedback_card = None  
        self.check = None

        
        
    def create_classification_labels(self):
        labels = []
        labels.append(self.board.add_label("Alta", color="red"))
        labels.append(self.board.add_label("Média", color="yellow"))
        labels.append(self.board.add_label("Baixa", color="green"))
        labels.append(self.board.add_label("1", color="yellow"))
        labels.append(self.board.add_label("2", color="red"))
        return labels

    
    def create_card(self, conditional, trello_list, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist):
        superiors_emails = [email.strip() for email in emails.split('-')]
        superiors = [name.strip() for name in names.split('-')] 

        self.check = checklist
        
        if (conditional is None):
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
            
            self.send_email(obj_email, email, "Solicitação de Resolução de Não Conformidade", superiors[0], classification,
                        non_conformity, checklist.auditor_name, 0, checklist, responsible, datetime.now().strftime("%d/%m/%Y"),
                        (datetime.now() + timedelta(days=int(deadline))).strftime("%d/%m/%Y"), deadline, card)
        
        card = self.Card(conditional,non_conformity,deadline,responsible,classification,superiors, email, superiors_emails, 0)
        self.cards.append(card)


    def verify_card(self, list_id, list_review_id, list_resolved_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist):
        trello_list = self.board.get_list(list_id)
        existing_cards = trello_list.list_cards()

        trello_list_review = self.board.get_list(list_review_id)
        existing_cards2 = trello_list_review.list_cards()

        trello_list_resolved = self.board.get_list(list_resolved_id)
        existing_cards3 = trello_list_resolved.list_cards()

        for card in existing_cards:
            if card.name == non_conformity:
                print(f"Cartão '{non_conformity}' já existe. Não será duplicado.")
                self.create_card(card, trello_list, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist)
                return
            
        for card in existing_cards2:
            if card.name == non_conformity:
                print(f"Cartão '{non_conformity}' já existe. Não será duplicado.")
                self.create_card(card, trello_list, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist)
                return
            
        for card in existing_cards3:
            if card.name == non_conformity:
                print(f"Cartão '{non_conformity}' já existe. Não será duplicado.")
                self.create_card(card, trello_list, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist)
                return
        
        self.create_card(None, trello_list, list_id, non_conformity, deadline, responsible, classification, names, emails, email, obj_email, checklist)

        
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
                self.comment(card.card, f"Lembrete: O prazo de entrega é hoje, verifique se obteve resposta no seu e-mail.")
            
            elif card.card.due_date.date() == today + timedelta(days=1):
                self.comment(card.card, f"Lembrete: O prazo de entrega é amanhã, verifique se obteve resposta no seu e-mail.")
            
            elif card.card.due_date.date() < today:
                self.comment(card.card, f"Lembrete: O prazo de entrega foi estourado.")
    
        
    def send_email(self,email, receiver_email, subject, immediate_superior, classification, non_conformity, auditor, escalation_number, checklist, responsible, date, resolution_date, deadline,card):
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

        if(email.send_email(receiver_email, subject, body)):
            self.comment(card, f"Aviso: E-mail de notificação sobre não conformidade enviado ao(à) responsável: {responsible}.")


    def comment(self, card, comment_text):
        card.comment(comment_text)
    

    def verify_feedback_card(self, cards_list):
        
        for card in cards_list:
            if card.name == "Feedback Geral":
                self.feedback_card = card
                print("Cartão de feedback carregado com sucesso.")
                return(True)

        print("Cartão de feedback não encontrado")
        return(False)


    def feedback_update(self, list_id, number_of_lines, non_conformities, checklist):
        
        trello_list = self.board.get_list(list_id)
        existing_cards = trello_list.list_cards()
        
        adherence_percentage = ((len(non_conformities) / number_of_lines) * 100 if number_of_lines != 0 else 0)

        if (self.verify_feedback_card(existing_cards)):
            self.feedback_card.set_description(
                f'Nome do Projeto: {checklist.project_name}\n'
                f'Nome do Artefato: {checklist.artefact_name}\n'
                f'Auditor: {checklist.auditor_name}\n'
                f'Atualizado em: {datetime.now().strftime("%d/%m/%Y")}\n'
                f'Total de Itens: {number_of_lines}\n'
                f'Itens não-conformes: {len(non_conformities)}\n'
                f'Aderência: {adherence_percentage:.2f}%\n'
            )
            self.comment(self.feedback_card, f'Aviso: Cartão Feedback atualizado às {datetime.now().strftime("%H:%M de %d/%m/%Y")}')
        
        else:
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
            self.comment(self.feedback_card, f'Aviso: Cartão Feedback criado às {datetime.now().strftime("%H:%M de %d/%m/%Y")}')
        
        self.comment(self.feedback_card, f'Aviso: Aderência atualizada para: {adherence_percentage:.2f}%')

    def search_card(self, card):
        cards_non_confority = self.cards
        for cd in cards_non_confority:
            if card.name == cd.non_conformity:
                return cd
        return None


    def move_card_to_list(self, card, list_id):
        # Mova o cartão para a lista de acordo com o list_id (superior responsável)
        destination_list = self.board.get_list(list_id)
        card.change_list(destination_list.id)
        card.comment(f"Cartão movido para a lista do superior responsável em {datetime.now().strftime('%d/%m/%Y')}.")
    
    def get_first_label_name(self, card):
        labels = card.labels  
        if labels:
            return labels[0].name 
        return None 
    
    def check_and_move_expired_cards(self, non_conformity_list, higher_review_list):
        trello_list = self.board.get_list(non_conformity_list)
        cards = trello_list.list_cards()

        today = datetime.now().replace(tzinfo=None)

        for card in cards:
            due_date = card.due_date.replace(tzinfo=None) 

            if due_date and due_date < today:
                print(f"Cartão {card.name} venceu. Movendo para a lista do superior responsável.")
                self.cards_escalonados.append(card)
                label = self.get_first_label_name(card)

                if label == 'Alta':
                    label = 1
                elif label == 'Média':
                    label = 2
                else:
                    label = 3

                new_due_date =datetime.now() + timedelta(days=int(label))
                card.set_due(new_due_date)
            
                label = self.classification_labels[3]
                card.add_label(label)
                self.move_card_to_list(card, higher_review_list)
                cd = self.search_card(card) 
                if cd is None:
                    print("Erro ao procurar o cartão!")
                    return
                email = "email.ptestes04@gmail.com"
                #self.send_email_review(email, cd.responsible_email, "Solicitação de Resolução de Não Conformidade", cd.superiors[1],
                #                      cd.classification, cd.non_conformity, self.check.auditor_name, 1, self.check, cd.responsible, datetime.now().strftime("%d/%m/%Y"),
                #                       (datetime.now() + timedelta(days=int(cd.deadline))).strftime("%d/%m/%Y"), cd.deadline, card) 
               


    def run_deadline_checker(self, non_conformity_list, higher_review_list, interval=3600):
        print("oii")
        while True:
            self.check_and_move_expired_cards(non_conformity_list, higher_review_list)
            time.sleep(interval) 

    def run_deadline_review(self, higher_review_list, resolved_list, interval=3600):
        while True:
            self.check_and_move_cards_review(higher_review_list, resolved_list)
            time.sleep(interval)

    def check_and_move_cards_review(self, higher_review_list, resolved_list):
        trello_list = self.board.get_list(higher_review_list)
        cards = trello_list.list_cards()

        today = datetime.now().replace(tzinfo=None)

        for card in cards:
            due_date = card.due_date.replace(tzinfo=None) 

            if due_date and due_date < today:
                print(f"Cartão {card.name} venceu. Escalonando para o superior responsável.")
                card.comment(f"Cartão escalonado para o superior responsável em {datetime.now().strftime('%d/%m/%Y')}.")
            
                
                
   
    def send_email_review(self,email, receiver_email, subject, immediate_superior, classification, non_conformity, auditor, escalation_number, checklist, responsible, date, resolution_date, deadline,card):
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

Informo que a não conformidade não foi resolvida no prazo estabelecido. Aguardo a resolução do problema 
dentro do novo prazo estipulado. Caso tenha alguma dúvida ou necessite de mais informações, 
favor entrar em contato. Se desejar apresentar uma contestação, gentileza fazê-lo no prazo de 24 horas úteis.


Atenciosamente,

{auditor},
Auditor(a) Interno(a)
        """

        if(email.send_email_review(receiver_email, subject, body)):
            self.comment(card, f"Aviso: E-mail de notificação sobre não conformidade enviado ao(à) responsável: {responsible}.")

    
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
    
