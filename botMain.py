#!/usr/bin/env python
import logging #logs
import os
import pathlib
import asyncio #for async computing
from telebot.async_telebot import AsyncTeleBot #telegram bot api
import time
from functionsFFMPEG import functionFFMPEG

#variables
token=str(os.environ.get("token_AnythingToSticker"))
bot=AsyncTeleBot(token)
path = pathlib.Path(__file__).parent.resolve()

# Start
@bot.message_handler(commands=['start'])
async def start_message(message):
    await bot.send_message(message.chat.id, "Send me any media file and i'll convert it to file supported by @Stickers")

#file convert
@bot.message_handler(content_types=['animation','video','photo'])
async def media_process(message):
    result_message = await bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML', disable_web_page_preview=True,reply_to_message_id=message.id)
    file_id = (message.photo[-1].file_id if (message.content_type=='photo') else (message.animation.file_id if (message.content_type=='animation') else message.video.file_id))
    file_path = await bot.get_file(file_id)
    name = f"{path}/tmp/{file_id}{'.png' if (message.content_type=='photo') else '.webm'}"
    url = f'https://api.telegram.org/file/bot{token}/{file_path.file_path}'
    await functionFFMPEG(url,name) if (message.content_type=='photo') else await functionFFMPEG(url,name, {'vf':'scale=:w=512:h=512:force_original_aspect_ratio=decrease', 'c:v':'vp9', 't':'2.9', 'b:v':'85K','an':None})
    await bot.delete_message(chat_id=message.chat.id, message_id=result_message.id, timeout=180)
    with open(name, 'rb') as doc:
        await bot.send_document(message.chat.id,doc ,reply_to_message_id=message.id,caption='<b>Done!</b>', timeout=180,parse_mode='HTML')
    os.remove(converted_name)

#boot
def main():
    logging.basicConfig(filename=f'{path}/bot.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logging.info(f'file path = {path}')
    if token == 'None':
        logging.critical('token is None')
        exit('Token is not selected')
    tmpPath = pathlib.Path(f"{path}/tmp").mkdir(parents=True, exist_ok=True)
    while True:
        try:
            asyncio.run(bot.polling(none_stop=True, timeout=180, interval=1))
        except Exception as e:
            logging.error(e)
            time.sleep(10)
if __name__ == '__main__':
    main()
