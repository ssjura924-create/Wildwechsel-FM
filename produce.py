#!/usr/bin/env python3
"""Prepare a narrated short from approved footage, a script and optional Ralle overlay."""
import argparse
import os
import subprocess as sp
import sys
import tempfile
import textwrap
import wave
from pathlib import Path

def execute(*args, **kwargs):
    sp.run([str(x) for x in args], check=True, **kwargs)

def duration(path):
    return float(sp.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]))

def stamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script', required=True, type=Path)
    p.add_argument('--model', required=True, type=Path)
    p.add_argument('--gameplay', type=Path)
    p.add_argument('--ralle', type=Path)
    p.add_argument('--preview', action='store_true')
    p.add_argument('--output', default='output/wildwechsel.mp4', type=Path)
    a = p.parse_args()
    lines = [x.strip() for x in a.script.read_text(encoding='utf-8').splitlines() if x.strip()]
    if not lines or sum(map(len,lines)) > 1300 or any(len(x)>180 for x in lines):
        p.error('Write short caption-length lines, max 1300 characters total.')
    if not a.preview and (not a.gameplay or not a.gameplay.is_file()):
        p.error('Real episode requires approved gameplay footage.')
    if not a.preview and (not a.ralle or not a.ralle.is_file()):
        p.error('Real episode requires Ralle PNG or alpha video.')
    a.output = a.output.resolve()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='wildwechsel-') as temp:
        d = Path(temp)
        voice = d/'voice.wav'
        captions = d/'captions.srt'
        cues = []
        offset = 0
        with wave.open(str(voice),'wb') as out:
            for i,line in enumerate(lines):
                wav = d/f'{i}.wav'
                execute(sys.executable,'-m','piper','-m',a.model,'-f',wav,'--',line)
                with wave.open(str(wav),'rb') as part:
                    fmt = (part.getnchannels(),part.getsampwidth(),part.getframerate())
                    if i == 0:
                        out.setnchannels(fmt[0]); out.setsampwidth(fmt[1]); out.setframerate(fmt[2])
                    elif fmt != (out.getnchannels(),out.getsampwidth(),out.getframerate()):
                        raise ValueError('Voice segments have different formats.')
                    length = part.getnframes()/fmt[2]
                    out.writeframes(part.readframes(part.getnframes()))
                    gap = round(fmt[2]*.18)
                    out.writeframes(b'\0'*(gap*fmt[0]*fmt[1]))
                cues.append(f'{i+1}\n{stamp(offset)} --> {stamp(offset+length)}\n'+ '\n'.join(textwrap.wrap(line,width=35))+'\n')
                offset += length + gap/fmt[2]
        captions.write_text('\n'.join(cues),encoding='utf-8')
        total = offset + .45
        if total > 60:
            p.error('Narration exceeds 60 seconds; shorten the script.')
        gameplay = a.gameplay
        if a.preview:
            gameplay = d/'preview.mp4'
            execute('ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=0x182536:s=1280x720:r=30',
              '-vf',"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='WILDWECHSEL FM':fontsize=65:fontcolor=white:x=(w-tw)/2:y=(h-th)/2-50,drawtext=text='STIMMEN- UND UNTERTITELTEST':fontsize=30:fontcolor=white:x=(w-tw)/2:y=(h-th)/2+50",
              '-t',str(total+.2),'-c:v','libx264','-pix_fmt','yuv420p',gameplay)
        if duration(gameplay) + .05 < total:
            p.error(f'Gameplay is too short: need {total:.1f} seconds. Provide a longer clip.')
        args = [sys.executable, str(Path(__file__).with_name('render.py')), '--gameplay',str(gameplay),'--voice',str(voice),'--subtitles',str(captions),'--seconds',str(total),'--output',str(a.output)]
        if a.ralle:
            args += ['--ralle',str(a.ralle)]
        execute(*args)
        (a.output.parent/'captions.srt').write_text(captions.read_text(encoding='utf-8'),encoding='utf-8')
        import shutil
        shutil.copyfile(voice,a.output.parent/'voice.wav')

if __name__ == '__main__':
    main()
