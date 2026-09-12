import json
import subprocess
from pathlib import Path

def main():
    out=Path('output'); video=out/'Pablo_Guru_Diario.mp4'
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    v=next(s for s in data['streams'] if s['codec_type']=='video')
    a=next(s for s in data['streams'] if s['codec_type']=='audio')
    duration=float(data['format']['duration'])
    assert (v['width'],v['height'])==(1080,1920), 'Resolução incorreta'
    assert v['codec_name']=='h264' and a['codec_name']=='aac', 'Codecs incorretos'
    assert 35 <= duration <= 90, f'Duração fora do limite de segurança: {duration}'
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    for i,second in enumerate([1,duration*.35,duration*.70,duration-2]):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(second),'-i',str(video),'-frames:v','1',str(out/f'preview_{i}.jpg')],check=True)
    result={'duration_seconds':duration,'width':v['width'],'height':v['height'],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'target_40_60_seconds':40<=duration<=60}
    (out/'validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__':main()
