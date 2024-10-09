import os
from flask import Flask, render_template, request, redirect, url_for
from trello import TrelloClient
from Trello import Trello
from Document import Document

API_KEY = 'f02469d093a13aca46ed2b5fbb7d8655'
API_SECRET = 'e19c613581328584049ad446beb3616c7467c71e21b3294f41786e9d4212a0e0'
TOKEN = 'ATTAda46d707198647510441a1b2be6f8f6ed1c9e07aee1adaf9dc160d3e67578b6c8EA544A0'
board_id = 'fYUZJCTz'
non_conformity_list = '67032c674496e526dacc3e1b'
geral_feedback_list = '670333b72501085cb440b2d3'
higher_review_list = '670333abd36976bb56fd6830'
resolved_list = '670333c493cfc1437ff2b630'
file_path = '../checklist.csv'
# Caminho absoluto para checklist.csv
checklist_path = "C:/Users/melov/OneDrive/Área de Trabalho/Qualidade de Software/Sistema-no-Trello-de-N-o-Conformidade/Sistema no Trello de Não Conformidade/checklist.csv"

# Verificando se o arquivo existe
if not os.path.isfile(checklist_path):
    print(f"Arquivo não encontrado: {checklist_path}")
else:
    checkList = Document(checklist_path)


