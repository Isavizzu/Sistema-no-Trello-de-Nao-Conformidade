import os
from flask import Flask, render_template, request, redirect, url_for
from trello import TrelloClient
from Trello import Trello
from Document import Document
from Email import Email

API_KEY = 'f02469d093a13aca46ed2b5fbb7d8655'
API_SECRET = 'e19c613581328584049ad446beb3616c7467c71e21b3294f41786e9d4212a0e0'
TOKEN = 'ATTAda46d707198647510441a1b2be6f8f6ed1c9e07aee1adaf9dc160d3e67578b6c8EA544A0'
board_id = 'fYUZJCTz'
non_conformity_list = '67032c674496e526dacc3e1b'
geral_feedback_list = '670333b72501085cb440b2d3'
higher_review_list = '670333abd36976bb56fd6830'
resolved_list = '670333c493cfc1437ff2b630'
file_path = os.path.join(os.getcwd(), 'checklist.csv')
email = "email.ptestes04@gmail.com"
password = 'iegv vxot dmgn juqg'


trello = Trello(API_KEY, API_SECRET, TOKEN, board_id)
email = Email(email, password)
checklist = Document(file_path)


for non_conformity in checklist.non_conformities:
    trello.create_card(non_conformity_list, non_conformity[0], non_conformity[4],
                       non_conformity[2], non_conformity[3], non_conformity[5], non_conformity[7], non_conformity[6], email, checklist)

trello.checking_deadline()
trello.feedback_update(geral_feedback_list, checklist.get_number_of_rows(), checklist.non_conformities, checklist)
trello.organize_cards(non_conformity_list)
