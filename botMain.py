#!/usr/bin/env python
import logging #logs
import os
import pathlib
import asyncio #for async computing
from telebot.async_telebot import AsyncTeleBot #telegram bot api
import time
from functionsFFMPEG import functionFFMPEG
from moviepy.editor import VideoFileClip
import requests as rq

#variables
path = pathlib.Path(__file__).parent.resolve()
token=str(os.environ.get("token_AnythingToSticker"))
bot=AsyncTeleBot(token)
cwd = pathlib.Path(__file__).parent.resolve()

#functions
def download_file(url,name): #file download from url
    with rq.get(url, stream=True, timeout=3600) as r:
        r.raise_for_status()
        with open(name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    return name

# Start
@bot.message_handler(commands=['start'])
async def start_message(message):
    await bot.send_message(message.chat.id, 'Hello!')
    
#file convert
@bot.message_handler(content_types=['animation','video','photo'])
async def media_process(message):
    result_message = await bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML', disable_web_page_preview=True,reply_to_message_id=message.id)
    file_id = (message.photo[-1].file_id if (message.content_type=='photo') else (message.animation.file_id if (message.content_type=='animation') else message.video.file_id))
    file_path = await bot.get_file(file_id)
    name =f"{cwd}/tmp/{file_id}{'.jpg' if (message.content_type=='photo') else '.mp4'}"
    converted_name=name.replace('.'+name.split('.')[-1],'.png' if (message.content_type=='photo') else '.webm')
    download_file(f'https://api.telegram.org/file/bot{token}/{file_path.file_path}',name)
    if message.content_type!='photo':
        videoclip = VideoFileClip(name)
        new_clip = videoclip.without_audio()
        new_clip.write_videofile(name)
        videoclip.close()
        new_clip.close()
    await functionFFMPEG(name,converted_name) if (message.content_type=='photo') else await functionFFMPEG(name,converted_name, {'vf':'scale=:w=512:h=512:force_original_aspect_ratio=decrease', 'c:v':'vp9', 't':'2.9', 'b:v':'85K'})
    os.remove(name)
    doc = open(converted_name, 'rb')
    await bot.delete_message(chat_id=message.chat.id, message_id=result_message.id, timeout=180)
    await bot.send_document(message.chat.id,doc ,reply_to_message_id=message.id,caption='<b>Done!</b>', timeout=180,parse_mode='HTML')
    os.remove(converted_name)


#boot
def main():
    logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logging.info(f'file path = {cwd}')
    if token == 'None':
        logging.critical('token is None')
        exit('Token is not selected')
    tmpPath = pathlib.Path(f"{cwd}/tmp").mkdir(parents=True, exist_ok=True)
    while True:
        try:
            asyncio.run(bot.polling(none_stop=True, timeout=180, interval=1))
        except Exception as e:
            logging.error(e)
            time.sleep(10)

if __name__ == '__main__':
    main()
