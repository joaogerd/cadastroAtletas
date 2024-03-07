import pyautogui as pg
import time
import re
from re import fullmatch
import os
import webbrowser as web
import pyperclip

def sendwhatmsg_instantly(phone_no: str, message: str, wait_time: int = 15, tab_close: bool = False, close_time: int = 1) -> None:
    """Send WhatsApp Message Instantly using pyautogui."""
    # Validar o número de telefone
    phone_no = phone_no.replace(" ", "")
    if not re.fullmatch(r"^\+?[0-9]{10,15}$", phone_no):
        raise ValueError("Invalid Phone Number. Ensure it includes the country code and is without spaces or special characters.")

    # Abrir o WhatsApp Web
    web.open(f"https://web.whatsapp.com/send?phone={phone_no}")
    time.sleep(wait_time)  # Esperar pela carga da página e pelo login

    # Digitar e enviar a mensagem
    for msg in message:
       pyperclip.copy(msg)
       pg.hotkey("ctrl", "v")
       pg.hotkey("enter")
#       pg.typewrite(f'{msg}\n')
       
    input("Pressione Enter para continuar...")
    time.sleep(0.1)

    # Opcional: fechar a aba após enviar a mensagem
    if tab_close:
        time.sleep(close_time)  # Esperar um momento antes de fechar
        pg.hotkey('ctrl', 'w')  # Fecha a aba do navegador

def sendMessage(phone_number, name):
    # Exemplo de uso
#    phone_number = '+5512991484812'  # Replace with the ac# Importing the required module
    message1=f'{name}, agora preciso dos seguintes documentos:'
    message2 = "*RG* autenticado e *COLORIDO* (*não pode ser preto e branca*) ou RG oferecido pelo sistema do Governo Federal (Gov.br)"
    message3 = "*ATESTADO MÉDICO* datado de 2024, contento *Está apto a pratica esportiva no ano de 2024*"
    message4 = "*AUTORIZAÇÃO DO MENOR*, *deve ser assinada pelo responsável legal*, que deverá via cartório *reconhecer firma*;"
    message5 = "Assim que tiver todos os documentos autenticados envia cópia digital *DE BOA QUALIDADE*  aqui no meu whatsapp.;"
    message=(message1,message2, message3, message4, message5)
    sendwhatmsg_instantly(phone_number, message, wait_time=8, tab_close=True)

