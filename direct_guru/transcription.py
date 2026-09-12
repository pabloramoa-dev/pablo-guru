"""Audio input adapter; gated until an authenticated Instagram audio test passes."""
import ipaddress
import json
import socket
import subprocess
import tempfile
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from direct_guru.providers import ProviderError

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ProviderError('audio_redirect_refused')

def allowed_url(url):
    p=urllib.parse.urlsplit(url)
    host=(p.hostname or '').lower()
    if p.scheme!='https' or p.username or p.password or p.port not in (None,443):return False
    return any(host.endswith('.'+d) for d in ['fbcdn.net','cdninstagram.com','fbsbx.com'])

def transcribe(url,key,model='gpt-4o-mini-transcribe'):
    if not allowed_url(url):raise ProviderError('audio_host_refused')
    host=urllib.parse.urlsplit(url).hostname
    for info in socket.getaddrinfo(host,443):
        if not ipaddress.ip_address(info[4][0]).is_global:raise ProviderError('audio_ip_refused')
    try:
        with urllib.request.build_opener(NoRedirect()).open(url,timeout=15) as response:
            audio=response.read(5*1024*1024+1)
        if not audio or len(audio)>5*1024*1024:raise ValueError()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'input.audio';p.write_bytes(audio)
            meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-show_format','-show_streams','-of','json',str(p)],timeout=10,stderr=subprocess.DEVNULL))
            duration=float(meta['format']['duration'])
            if not 0.3<=duration<=60 or not any(s['codec_type']=='audio' for s in meta['streams']):raise ValueError()
            wav=Path(td)/'audio.wav'
            subprocess.run(['ffmpeg','-y','-v','error','-protocol_whitelist','file,pipe','-i',str(p),'-t','60','-ar','16000','-ac','1',str(wav)],check=True,timeout=20,stderr=subprocess.DEVNULL)
            audio=wav.read_bytes()
        boundary='pablo'+uuid.uuid4().hex
        data=(f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\n{model}\r\n'
              f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\npt\r\n'
              f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+audio+f'\r\n--{boundary}--\r\n'.encode()
        request=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=data,headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
        with urllib.request.urlopen(request,timeout=45) as r:text=json.load(r)['text'].strip()
        if not text or len(text)>1800:raise ValueError()
        return text
    except Exception:raise ProviderError('transcription_failed') from None
