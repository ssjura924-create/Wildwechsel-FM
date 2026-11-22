#!/usr/bin/env python3
"""Render a vertical short from licensed gameplay and optional narration/overlay."""
import argparse
import json
import subprocess
import tempfile
import shutil
from pathlib import Path


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))


def run():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gameplay', required=True)
    p.add_argument('--voice')
    p.add_argument('--ralle', help='PNG or video with transparency')
    p.add_argument('--subtitles', help='UTF-8 SRT')
    p.add_argument('--seconds', type=float, default=30)
    p.add_argument('--output', default='output/wildwechsel.mp4')
    a = p.parse_args()
    if not 0 < a.seconds <= 60:
        p.error('Duration must be between 0 and 60 seconds')
    meta = probe(a.gameplay)
    has_audio = any(s['codec_type']=='audio' for s in meta['streams'])
    duration = min(a.seconds, float(meta['format'].get('duration',a.seconds)))
    if duration <= 0:
        p.error('Invalid gameplay duration')
    cmd = ['ffmpeg','-hide_banner','-loglevel','warning','-y','-filter_complex_threads','1','-i',a.gameplay]
    idx = 1
    voice = avatar = None
    if a.voice:
        voice = idx; idx += 1
        cmd += ['-i',a.voice]
    if a.ralle:
        avatar = idx; idx += 1
        cmd += ['-i',a.ralle]
    if not has_audio and voice is None:
        silent = idx
        cmd += ['-f','lavfi','-i','anullsrc=r=48000:cl=stereo']
    f = ['[0:v]fps=30,split=2[bg][game]', '[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2,setsar=1[b]', '[game]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[g]', '[b][g]overlay=(W-w)/2:(H-h)/2[base]']
    v = 'base'
    if avatar is not None:
        f += [f'[{avatar}:v]scale=380:-2,format=rgba[r]', '[base][r]overlay=x=60+8*sin(t*2):y=H-h-300+5*sin(t*3):eof_action=repeat[withralle]']
        v = 'withralle'
    with tempfile.TemporaryDirectory(prefix='wildwechsel-') as tmp:
        if a.subtitles:
            sub = Path(tmp) / 'captions.srt'
            shutil.copyfile(a.subtitles,sub)
            f.append(f"[{v}]subtitles={sub}:force_style='FontName=DejaVu Sans,FontSize=16,Outline=2,Alignment=2,MarginV=45'[captioned]")
            v = 'captioned'
        if voice is not None and has_audio:
            f += ['[0:a]volume=0.18,aresample=48000[gameaudio]',f'[{voice}:a]aresample=48000,apad[voiceaudio]','[gameaudio][voiceaudio]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,apad[audio]']
        elif voice is not None:
            f += [f'[{voice}:a]aresample=48000,apad[audio]']
        elif has_audio:
            f += ['[0:a]aresample=48000,apad[audio]']
        else:
            f += [f'[{silent}:a]anull[audio]']
        out = Path(a.output)
        out.parent.mkdir(parents=True,exist_ok=True)
        cmd += ['-filter_complex',';'.join(f),'-map',f'[{v}]','-map','[audio]','-t',str(duration),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
        subprocess.run(cmd,check=True)
    print(f'Exported: {out}')

if __name__=='__main__':
    run()
