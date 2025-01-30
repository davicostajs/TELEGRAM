import openai
import os
import asyncio
import schedule
import time
from threading import Thread
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configurações do bot - Usando variáveis de ambiente para segurança
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token do Telegram
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Chave OpenAI
CHAT_ID = os.getenv("CHAT_ID")  # ID do chat no Telegram

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

# Função para enviar mensagens ao Telegram
async def enviar_mensagem(chat_id, mensagem):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=mensagem)

# Função para mensagens agendadas
async def enviar_mensagem_agendada():
    pergunta = (
        "Crie uma mensagem de bom dia motivacional para a comunidade Godin Bets na qual é um grupo de apostas esportivas no Telegram. "
        "A mensagem deve começar com saudações calorosas no estilo da comunidade, destacando o mascote do grupo, Tio Patinhas, como símbolo de riqueza e estratégia. "
        "Inclua referências ao universo das apostas esportivas, como gestão de banca, odds, greens e disciplina. "
        "O texto deve ser envolvente, criativo e único, nunca repetindo formatos anteriores. "
        "Sempre busque superar o impacto e a originalidade das mensagens anteriores, motivando o grupo a começar o dia com entusiasmo e foco. "
        "Responda somente com a mensagem final e nada mais."
    )

    resposta = await consultar_chatgpt(pergunta)
    await enviar_mensagem(CHAT_ID, resposta)

# Configurar agendamentos
def configurar_agendamento():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    schedule.every().day.at("09:00").do(lambda: asyncio.run(enviar_mensagem_agendada()))

    while True:
        schedule.run_pending()
        time.sleep(1)

# Comando /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot ativado! Mensagens programadas serão enviadas ao grupo.")

# Função principal
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adicionar comandos
    application.add_handler(CommandHandler("start", start))

    # Inicia a thread de agendamentos
    thread = Thread(target=configurar_agendamento, daemon=True)
    thread.start()

    # Inicia o bot de forma correta
    application.run_polling()

# Inicializador
if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Erro: {e}")
