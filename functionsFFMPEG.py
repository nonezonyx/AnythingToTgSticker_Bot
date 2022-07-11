from ffmpeg import FFmpeg
import asyncio

async def functionFFMPEG(namein='input.jpg', nameout='output.png', args={'vf':'scale=:w=512:h=512:force_original_aspect_ratio=decrease'}):
    ffmpeg = FFmpeg().option('y').input(namein,).output(nameout,args)
    await ffmpeg.execute()
    return(nameout)
