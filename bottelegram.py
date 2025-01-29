import openai
import os
from telegram import Bot
from telegram.ext import Application, CommandHandler
import schedule
import time
from threading import Thread
import asyncio

# Configurações do bot - Usando variáveis de ambiente para segurança
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Variável de ambiente para o token do Telegram
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Variável de ambiente para a chave OpenAI
CHAT_ID = os.getenv("CHAT_ID")  # Variável de ambiente para o chat ID

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# Função para consultar o ChatGPT
async def consultar_chatgpt(pergunta):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pergunta}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Erro ao acessar o ChatGPT: {e}"

# Função para enviar mensagens
async def enviar_mensagem(chat_id, mensagem):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=mensagem)

# Função para mensagens agendadas
async def enviar_mensagem_agendada():
    pergunta = "Crie uma mensagem de bom dia motivacional para a comunidade Godin Bets na qual é um grupo de apostas esportivas no telegram. A mensagem deve começar com saudações calorosas no estilo da comunidade, destacando o mascote do grupo que é o Tio Patinhas como símbolo de riqueza e estratégia. Inclua referências ao universo das apostas esportivas, como gestão de banca, odds, greens e disciplina. O texto deve ser envolvente, criativo e único, nunca repetindo formatos anteriores. Sempre busque superar o impacto e a originalidade das mensagens anteriores, motivando o grupo a começar o dia com entusiasmo e foco. Responda somente com a mensagem final e nada mais.Exemplo: ☀️ BOM DIAAA, TIME GODIN BETS! ☀️🌟 Novo dia, nova chance de fazer o cofre brilhar!O Tio Patinhas já abriu o mapa do tesouro, e hoje vamos atrás dos nossos greens com estratégia e disciplina!⚽ Jogos quentes no radar e odds perfeitas para encher os bolsos.🚀 Foco, gestão de banca e boas decisões são o caminho para o sucesso.🤑 Quem aqui vai encher o cofre junto com o Tio Patinhas hoje? Reage aí e vamos com tudo!🍀 Dica do Tio Patinhas:O segredo do sucesso é estratégia, disciplina e... estar com a gente no grupo VIP!"
    resposta = await consultar_chatgpt(pergunta)
    await enviar_mensagem(CHAT_ID, resposta)

# Configurar agendamentos
def configurar_agendamento(loop):
    schedule.every().day.at("09:00").do(lambda: asyncio.run_coroutine_threadsafe(enviar_mensagem_agendada(), loop))

# Thread para executar o agendamento
def executar_agendamentos():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Comando /start
async def start(update, context):
    await update.message.reply_text("Bot ativado! Mensagens programadas serão enviadas ao grupo.")

# Função principal
def main():
    # Configura o bot do Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comando /start
    application.add_handler(CommandHandler("start", start))

    # Inicia os agendamentos em uma thread separada
    loop = asyncio.get_event_loop()
    configurar_agendamento(loop)
    thread = Thread(target=executar_agendamentos)
    thread.start()

    # Inicia o bot sem encerrar o loop
    loop.run_until_complete(application.run_polling())

# Inicializador
if __name__ == "__main__":
    # Garante que o loop principal está sendo usado
    try:
        main()
    except RuntimeError as e:
        print(f"Erro: {e}")