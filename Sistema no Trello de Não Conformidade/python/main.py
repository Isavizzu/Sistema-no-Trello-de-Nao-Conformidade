import os
from flask import Flask, render_template
from flask import Flask, render_template, request, redirect, url_for
from trello import TrelloClient

# Configuração do cliente Trello
API_KEY = 'f02469d093a13aca46ed2b5fbb7d8655'
API_SECRET = 'e19c613581328584049ad446beb3616c7467c71e21b3294f41786e9d4212a0e0'
TOKEN = 'ATTAda46d707198647510441a1b2be6f8f6ed1c9e07aee1adaf9dc160d3e67578b6c8EA544A0'
board_id = 'fYUZJCTz'
id_da_lista_identificadas = '67032c674496e526dacc3e1b' 
# Especifique o diretório onde o template está localizado
app = Flask(__name__, template_folder='../templates')

# Rota para processar o envio do formulário
@app.route('/submit', methods=['POST'])
def submit():


    # Obter o quadro e a lista
    board = client.get_board('fYUZJCTz')
    lista_identificadas = board.get_list(id_da_lista_identificadas)

    # Criar um novo cartão
    card = lista_identificadas.add_card(
        name=name,
        due=due_date,
        desc=f'Responsável: {responsible}\nClassificação: {classification}'
    )

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
