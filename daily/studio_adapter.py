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

# Prop do roteiro diário -> desenho em studio/pablo_cenarios.py (PROPS).
# Até 22/09 'lamp' e 'seed' viravam PONTE, 'book' virava ESPELHO e 'map' virava
# ESTAÇÃO: a narração falava de uma coisa e a tela mostrava outra.
PROP_DESENHO={'lamp':'lanterna','seed':'vaso','map':'mapa','book':'caderno','key':'chave',
              'cup':'xicara','bag':'mochila','door':'porta','mirror':'espelho',
              'hourglass':'ampulheta','bridge':'ponte','station':'estacao','chain':'corrente',
              'window':'janela','magnifier':'lupa'}

# Paleta da capa e da etiqueta: gira por episódio para a grade não virar um bloco só.
PALETAS_CAPA=['noite','vinho','petroleo','musgo','terracota']

def _destaque(ep,lines):
    if ep.get('destaque'):return ep['destaque'].strip().upper()[:18]
    return None

def _frase(ep,lines):
    """Frase que a Marina anota no caderninho dourado (e que o espectador salva)."""
    if ep.get('frase'):return ep['frase'].strip()
    return DISCOVERIES.get(ep['id'])

def paleta_capa(ep):
    import hashlib
    h=int(hashlib.sha1(ep['id'].encode()).hexdigest(),16)
    return PALETAS_CAPA[h%len(PALETAS_CAPA)]

# Coreografia por episódio: cada fala tem um PAPEL e cada papel tem opções de
# expressão/gesto/câmera. A escolha gira pelo id do episódio, e o formato e a
# emoção puxam a virada. Antes, todo episódio repetia a mesma sequência.
# (papel, opções de expressão, opções de gesto, opções de efeito, reação de quem escuta)
PAPEIS=[
    ('gancho',    ['duvida','preocupado','surpresa'],   ['levantar_mao','cruzar_bracos',None], [None,'revelar'], ['sabio','provocando']),
    ('historia',  ['sabio','sereno','provocando'],      ['abrir_maos','apontar',None],         ['push',None],    ['calmo','duvida']),
    ('imagem',    ['sereno','surpresa','sabio'],        ['apontar','abrir_maos',None],         [None,'push'],    ['surpresa','calmo']),
    ('provoca',   ['provocando','grave','sabio'],       ['apontar','cruzar_bracos','abrir_maos'], ['push','revelar'], ['preocupado','duvida']),
    ('descoberta',['compreensao','surpresa','sorriso'], ['assentir','abrir_maos',None],        ['revelar',None], ['sereno','sorriso']),
    ('virada',    ['sereno','grave','sorriso'],         ['abrir_maos','assentir'],             ['revelar','push'], ['compreensao','surpresa']),
    ('final',     ['sorriso','provocando','sereno'],    ['apontar','abrir_maos',None],         [None,'push'],    ['compreensao','sorriso']),
    ('cta',       ['sorriso','compreensao'],            ['acenar'],                            [None],           ['sorriso','sereno']),
]

def coreografia(ep):
    import hashlib
    semente=int(hashlib.sha1(ep['id'].encode()).hexdigest(),16)
    saida=[]
    for i,(_papel,exprs,gestos,efeitos,reacoes) in enumerate(PAPEIS):
        r=(semente>>(i*5))
        saida.append([exprs[r%len(exprs)],gestos[(r>>1)%len(gestos)],efeitos[(r>>2)%len(efeitos)],reacoes[(r>>3)%len(reacoes)]])
    formato=ep.get('formato','parabola');emocao=ep.get('emocao','INQUIETAÇÃO')
    # a virada acompanha a emoção do roteiro
    saida[5][0]={'INDIGNAÇÃO':'grave','ESPANTO':'surpresa'}.get(emocao,saida[5][0])
    if formato=='humor':
        saida[1][0]='sorriso';saida[2][0]='provocando';saida[4][0]='sorriso'
    elif formato=='marina_discorda':
        saida[4]=['duvida','cruzar_bracos',None,'sabio'];saida[5][0]='sereno'
    elif formato=='erro_do_pablo':
        saida[1][0]='sereno';saida[1][1]=None;saida[1][3]='surpresa'
    elif formato=='sem_pergunta':
        saida[6][0]='sereno';saida[6][1]=None
    # pelo menos dois movimentos de câmera no episódio
    if sum(1 for x in saida if x[2])<2:saida[1][2]='push';saida[5][2]='revelar'
    return saida

def roteiro(ep):
    lines=[s['text'] for s in ep['segments']]
    frase=_frase(ep,lines)
    # As cinco respostas editoriais precedem a montagem das cenas.
    editorial={'nicho':'Desenvolvimento pessoal, emocional e espiritual por histórias e metáforas.',
               'nao_seguidor':f"Pessoa que se reconhece nesta pergunta: {lines[0]}",
               'emocao':ep.get('emocao','INQUIETAÇÃO'),'pensamento_final':frase or lines[5],
               'formato':'Reel vertical 9:16, alvo de 40 a 60 segundos.',
               'teste_estranho':'História autônoma, sem depender de episódios anteriores.',
               'teste_envio':f"Quem recebe está tentando lidar com a questão: {lines[0]}"}
    prop=PROP_DESENHO.get(ep['prop'],'ponte')
    # Cenas: a VIRADA do Pablo (fala 6) volta para o vídeo — antes era descartada e a
    # Marina repetia uma descoberta pré-escrita. A frase anotada aparece no caderninho
    # durante a pergunta final, sem narração extra.
    text_scenes=[lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6],CTA]
    speakers=['perguntadora','pablo','pablo','pablo','perguntadora','pablo','pablo','perguntadora']
    coreo=coreografia(ep)
    scenes=[]
    for i,(speaker,text) in enumerate(zip(speakers,text_scenes)):
        expr,gesto,efeito,reacao=coreo[i]
        scene={'falante':speaker,'texto':text,'cenario':prop if i in (1,2,3,5) else 'split',
               'expressao':expr,'gesto':gesto,'efeito':efeito,'reacao':reacao}
        if i==5:
            scene['desfecho']=True          # o objeto muda de estado na virada
            scene['pingente']=True          # o pingente do Pablo acende
            if _destaque(ep,lines):scene['destaque']=_destaque(ep,lines)
        if i==6 and frase:scene['anotacao']=frase
        scenes.append(scene)
    n=12+max(0,(date.fromisoformat(ep['date'])-date(2026,9,13)).days)
    capa=ep.get('capa') or ep['title']
    return {'numero':n,'titulo':ep['title'],'titulo_b':lines[0].replace('Pablo Guru, ','').capitalize(),
            'hook_first': True, 'tema':ep['title'],'pergunta':lines[6],'formato':'vertical','cartela':ep['title'],
            'cartela_sub':lines[0].replace('Pablo Guru, ',''),'cta_final':'Siga o canal para receber mais',
            'estilo_vox':'guru','cta':['SIGA O CANAL','para receber mais','@opabloguru'],
            'capa':{'titulo':capa,'objeto':prop,'paleta':paleta_capa(ep),'frase':frase or ''},
            'pagina':1+max(0,(date.fromisoformat(ep['date'])-date(2026,9,13)).days),
            'publico':ep.get('publico'),'formato':ep.get('formato','parabola'),
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
    shutil.copy2(result['capa'],out/'capa.png')
    # Capa 9:16 da grade (vai como cover_url) e TAMBÉM o 1º quadro do vídeo:
    # quem vê a grade ou o feed enxerga o título do episódio, nunca o mesmo rosto.
    import pablo_capa_vox as capa
    capa.gerar_capa_ig(script['capa'],str(out/'capa_ig.jpg'))
    capa.prefixar_capa(result['episodio'],str(out/'capa_ig.jpg'),str(out/'Pablo_Guru_Diario.mp4'))
    meta=json.loads(Path(result['metadados']).read_text())
    # Metadados históricos não são evidência de alcance nem de testes realizados.
    meta.pop('performance_esperada',None)
    meta['canal']='Pablo Guru (@opabloguru)'
    meta['motor_tts']=result['motor_tts']
    meta['motor_video']='hyperframes'
    meta['hyperframes_version']='0.8.96'
    meta['checklist_pre_publicacao']={'teste_automatizado':'pendente','revisao_visual':'pendente','teste_em_tres_dispositivos':'não realizado'}
    (out/'metadados.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
