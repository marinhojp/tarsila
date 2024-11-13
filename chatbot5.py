import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import random

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Tarsila")
        master.geometry("600x500")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Tarsila, sua assistente cultural. Como posso te ajudar hoje?\n")
        self.text_area.configure(state="disabled")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite o nome ou a informação que deseja sobre o museu...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="green", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n\n")  # Adiciona linha em branco após a pergunta
        self.text_area.configure(state="disabled")

        # Processar a entrada do usuário
        response = self.get_response(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Tarsila: " + response + "\n\n")  # Adiciona linha em branco após a resposta
        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

    def normalize_string(self, s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()

    def get_response(self, user_input):
        user_input_normalized = self.normalize_string(user_input)

        # Definir sinônimos para cada tipo de coluna
        endereco_sinonimos = ["endereco", "logradouro", "localizacao", "local", "rua"]
        telefone_sinonimos = ["telefone", "contato", "numero","celular"]
        site_sinonimos = ["site", "website", "pagina","link"]
        descricao_sinonimos = ["descricao", "informacao", "sobre","história"]

        try:
            response = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vQE0Ri65HJxWyZdjjcgzzAz7N6ZxcejCLhPNweL5q5tBBB9-qsams2yLdeNMMu4ETeNIKhDNeTnd4ye/pubhtml")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')

                for row in rows[1:]:
                    cells = row.find_all('td')
                    nome_museu = cells[0].get_text().strip()
                    nome_museu_normalized = self.normalize_string(nome_museu)
                    
                    if re.search(r'\b' + re.escape(nome_museu_normalized) + r'\b', user_input_normalized):
                        descricao = cells[1].get_text().strip()
                        bairro = cells[2].get_text().strip()
                        logradouro = cells[3].get_text().strip()
                        telefone = cells[4].get_text().strip()
                        site = cells[5].get_text().strip()

                        # Frases randomizadas para cada tipo de informação
                        endereco_respostas = [
                            f"O endereço do {nome_museu} é {logradouro}, no bairro {bairro}.",
                            f"Você pode encontrar o {nome_museu} em {logradouro}, {bairro}.",
                            f"O {nome_museu} está localizado em {logradouro}, no bairro {bairro}."
                        ]
                        telefone_respostas = [
                            f"O telefone do {nome_museu} é {telefone}.",
                            f"Para falar com o {nome_museu}, ligue para {telefone}.",
                            f"Você pode contatar o {nome_museu} pelo número {telefone}."
                            f"Ligue: {telefone} para contatar o {nome_museu}"
                        ]
                        site_respostas = [
                            f"O site do {nome_museu} é {site}.",
                            f"Acesse o site do {nome_museu} em {site}.",
                            f"Para mais informações, visite o site: {site}."
                            f"Opa, aqui está o site do {nome_museu}: {site}"
                            f"É pra já! O site do {nome_museu} é {site}"
                        ]
                        descricao_respostas = [
                            f"Aqui vai uma descrição do {nome_museu}: {descricao}",
                            f"Sobre o {nome_museu}: {descricao}",
                            f"Descrição do {nome_museu}: {descricao}"
                            f"Essa é uma breve descrição do {nome_museu}: {descricao}"
                            f"Aqui está um pouco sobre o {nome_museu}: {descricao}"
                        ]

                        if any(sin in user_input_normalized for sin in endereco_sinonimos):
                            return random.choice(endereco_respostas)
                        elif any(sin in user_input_normalized for sin in telefone_sinonimos):
                            return random.choice(telefone_respostas)
                        elif any(sin in user_input_normalized for sin in site_sinonimos):
                            return random.choice(site_respostas)
                        elif any(sin in user_input_normalized for sin in descricao_sinonimos):
                            return random.choice(descricao_respostas)
                        else:
                            return (f"Museu: {nome_museu}\n"
                                    f"Descrição: {descricao}\n"
                                    f"Bairro: {bairro}\n"
                                    f"Logradouro: {logradouro}\n"
                                    f"Telefone: {telefone}\n"
                                    f"Site: {site}")
                return "Museu não encontrado. Por favor, verifique o nome e tente novamente."
            else:
                return "Desculpe, não consegui acessar a tabela no momento."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
