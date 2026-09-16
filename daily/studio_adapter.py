"""Adapta a seleção diária ao motor original enviado pelo proprietário."""
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'studio'
CTA='Obrigada, Pablo Guru. Vou seguir o canal pra receber mais histórias assim.'
DISCOVERIES={
 'a-lanterna':'Então posso testar, parar e mudar de direção. Começar não me obriga a continuar no caminho errado.',
 'o-vaso':'Então esperar não é abandonar o vaso. Posso observar a água e a luz sem arrancar a planta todos os dias.',
 'o-mapa':'Eu estava usando a vida dos outros como calendário. Posso aprender com eles sem escolher o mesmo destino.',
 'a-xicara':'Eu não preciso transformar todo pedido em promessa. Posso combinar o que consigo oferecer.',
 'o-caderno':'Meu rascunho não precisa ser a versão definitiva. A primeira página pode me ensinar a escrever a próxima.',
 'a-chave':'Mudar minha estratégia não apaga o esforço. Talvez seja justamente o que falta para ele fazer sentido.',
 'a-mochila':'A pedra não conserta o caminho. O que mostra meu aprendizado é o que eu faço diferente agora.',
 'a-luz-do-outro':'A alegria que vejo pode ser real. Mas uma janela acesa não mostra a casa inteira.',
 'as-raizes':'Eu posso usar uma referência sem copiar tudo. Preciso observar de que cuidado meu jardim precisa.',
 'a-rota':'Meu destino não desapareceu. A estrada mudou, e eu posso atualizar o caminho.',
 'a-pausa':'Uma pausa não apaga meu cuidado. Eu não preciso provar meu valor pelo cansaço.',
 'a-pagina-seguinte':'Essa página faz parte da minha história. Mas reconhecer, reparar e aprender também podem fazer.',
 'a-porta-aberta':'Eu estava esperando que adivinhassem. Posso pedir ajuda e ouvir a resposta, sem exigir um sim.',
 'a-bagagem':'Posso ajudar sem carregar todas as malas. Primeiro preciso conversar sobre o que cabe a cada um.',
}

def roteiro(ep):
    lines=[s['text'] for s in ep['segments']]
    discovery=DISCOVERIES.get(ep['id'],lines[4])
    # As cinco respostas editoriais precedem a montagem das cenas.
    editorial={'nicho':'Desenvolvimento pessoal, emocional e espiritual por histórias e metáforas.',
               'nao_seguidor':f"Pessoa que se reconhece nesta pergunta: {lines[0]}",
               'emocao':'INQUIETAÇÃO','pensamento_final':discovery,
               'formato':'Reel vertical 9:16, alvo de 40 a 60 segundos.',
               'teste_estranho':'História autônoma, sem depender de episódios anteriores.',
               'teste_envio':f"Quem recebe está tentando lidar com a questão: {lines[0]}"}
    prop={'lamp':'ponte','seed':'ponte','map':'estacao','cup':'xicara','book':'espelho','key':'porta','bag':'mochila'}[ep['prop']]
    text_scenes=[lines[0],lines[1],lines[2],lines[3],lines[4],lines[6],discovery,CTA]
    speakers=['perguntadora','pablo','pablo','pablo','perguntadora','pablo','perguntadora','perguntadora']
    expressions=['duvida','calmo','calmo','calmo','surpresa','calmo','compreensao','compreensao']
    gestures=['levantar_mao','abrir_maos','apontar','abrir_maos','baixar_cabeca','apontar','abrir_maos','acenar']
    effects=[None,'push',None,'push','revelar',None,'revelar',None]
    scenes=[{'falante':speaker,'texto':text,'cenario':prop if i in (1,2) else 'ponte' if i==3 else 'split',
             'expressao':expressions[i],'gesto':gestures[i],'efeito':effects[i]} for i,(speaker,text) in enumerate(zip(speakers,text_scenes))]
    n=12+max(0,(date.fromisoformat(ep['date'])-date(2026,9,13)).days)
    return {'numero':n,'titulo':ep['title'],'titulo_b':lines[0].replace('Pablo Guru, ','').capitalize(),
            'hook_first': True, 'tema':ep['title'],'pergunta':lines[6],'formato':'vertical','cartela':ep['title'],
            'cartela_sub':lines[0].replace('Pablo Guru, ',''),'cta_final':'Siga o canal para receber mais',
            'estilo_vox':'guru','cta':['SIGA O CANAL','para receber mais','@pabloguru'],
            'editorial':editorial,'cenas':scenes}

def main():
    out=ROOT/'output';ep=json.loads((out/'episode.json').read_text())
    script=roteiro(ep);path=out/'roteiro_studio.json'
    path.write_text(json.dumps(script,ensure_ascii=False,indent=2),encoding='utf-8')
    sys.path.insert(0,str(STUDIO))
    import pablo_audio as pa
    # Estilo Vox colagem é o padrão desde 16/09/2026.
    # PABLO_ESTILO=classico volta para o pablo_episodio.py original.
    if os.environ.get('PABLO_ESTILO','vox')=='classico':
        import pablo_episodio as pe
    else:
        import pablo_episodio_vox as pe
    # Não permitir mudança silenciosa para voz robótica em produção.
    original=pa.narrar
    def neural_only(*args,**kwargs):
        result=original(*args,**kwargs)
        if result.motor!='kokoro':raise RuntimeError('Voz Kokoro indisponível. Render interrompido para preservar a identidade vocal.')
        return result
    pa.narrar=neural_only
    result=pe.produzir(str(path),str(out/'studio'),'h')
    shutil.copy2(result['episodio'],out/'Pablo_Guru_Diario.mp4')
    shutil.copy2(result['capa'],out/'capa.png')
    meta=json.loads(Path(result['metadados']).read_text())
    # Metadados históricos não são evidência de alcance nem de testes realizados.
    meta.pop('performance_esperada',None)
    meta['canal']='Pablo Guru (@opabloguru)'
    meta['motor_tts']=result['motor_tts']
    meta['checklist_pre_publicacao']={'teste_automatizado':'pendente','revisao_visual':'pendente','teste_em_tres_dispositivos':'não realizado'}
    (out/'metadados.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
