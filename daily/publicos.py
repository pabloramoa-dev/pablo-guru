"""Públicos-alvo e formatos dos episódios (v3.5, 23/09/2026).

Cada episódio fala com UM público específico: o gancho, o personagem da
parábola e as hashtags apontam para a mesma pessoa. Episódios seguidos falam
com públicos diferentes, e o algoritmo recebe sinais claros de para quem
distribuir cada vídeo.

Os formatos alternam a estrutura para o perfil não virar fórmula única
(pergunta -> parábola -> diagnóstico -> pergunta).
"""
from __future__ import annotations

from datetime import date

PUBLICOS = {
    'maes': dict(nome='Mães que se cobram demais',
                 retrato='mãe que cuida de todo mundo e se sente culpada quando pensa em si',
                 hashtags=['#maternidade', '#maternidadereal', '#maes']),
    'recomeco_amoroso': dict(nome='Quem está recomeçando depois de um término',
                             retrato='pessoa que terminou um relacionamento e ainda olha para trás',
                             hashtags=['#recomeco', '#termino', '#amorproprio']),
    'vinte_e_poucos': dict(nome='Jovens de 20 e poucos que se sentem atrasados',
                           retrato='jovem adulto que compara a própria vida com a dos amigos',
                           hashtags=['#vidaadulta', '#crisedos20', '#jovensadultos']),
    'cuidadores': dict(nome='Quem cuida de pai, mãe ou alguém da família',
                       retrato='filho ou filha que cuida de um familiar e esquece de si',
                       hashtags=['#cuidador', '#familia', '#cuidardequemcuida']),
    'empreendedores': dict(nome='Pequenos empreendedores cansados',
                           retrato='dono de pequeno negócio que carrega tudo sozinho',
                           hashtags=['#empreendedorismo', '#pequenonegocio', '#empreender']),
    'cinquenta_mais': dict(nome='Pessoas de 50+ que querem recomeçar',
                           retrato='pessoa madura que acha que passou da hora de mudar',
                           hashtags=['#50mais', '#maturidade', '#nuncaetarde']),
    'concurseiros': dict(nome='Estudantes e concurseiros',
                         retrato='estudante que se cobra por resultado e tem medo de falhar',
                         hashtags=['#concurseiros', '#estudante', '#vestibular']),
    'longe_de_casa': dict(nome='Quem mora longe de casa',
                          retrato='pessoa que mudou de cidade ou país e sente saudade',
                          hashtags=['#saudade', '#morarfora', '#longedecasa']),
    'casais': dict(nome='Casais numa fase difícil',
                   retrato='pessoa casada que sente que o casal virou rotina',
                   hashtags=['#casamento', '#relacionamento', '#casal']),
    'filhos_adultos': dict(nome='Filhos adultos que ainda buscam aprovação dos pais',
                           retrato='adulto que ainda espera ouvir dos pais que fez certo',
                           hashtags=['#paisefilhos', '#familia', '#autoestima']),
    'busca_espiritual': dict(nome='Quem busca espiritualidade sem rótulo',
                             retrato='pessoa que sente falta de sentido e não se encaixa numa religião',
                             hashtags=['#espiritualidade', '#despertar', '#vidainterior']),
    'professores': dict(nome='Professores e educadores esgotados',
                        retrato='professor que se doa aos alunos e chega vazio em casa',
                        hashtags=['#professor', '#educacao', '#professores']),
    'quem_cuida_na_saude': dict(nome='Profissionais que cuidam dos outros',
                                retrato='enfermeira, técnico ou cuidador profissional que não para',
                                hashtags=['#enfermagem', '#saude', '#quemcuida']),
    'pais_de_adolescentes': dict(nome='Pais de adolescentes',
                                 retrato='pai ou mãe que sente o filho adolescente se afastando',
                                 hashtags=['#paisdeadolescentes', '#adolescencia', '#paternidade']),
    'perfeccionistas': dict(nome='Perfeccionistas que travam',
                            retrato='pessoa exigente que não começa por medo de fazer mal feito',
                            hashtags=['#perfeccionismo', '#autocobranca', '#autocompaixao']),
    'introvertidos': dict(nome='Introvertidos e tímidos',
                          retrato='pessoa quieta que se sente invisível nos grupos',
                          hashtags=['#introvertido', '#timidez', '#introversao']),
}

FORMATOS = {
    'parabola': 'Clássico: parábola de terceiros com um objeto; a virada é uma imagem.',
    'erro_do_pablo': ('O Pablo conta um ERRO DELE, em primeira pessoa, de quando era mais novo '
                      '(fala 2 começa com algo como “Quando eu era aprendiz de…”). Ele não é '
                      'perfeito; a sabedoria veio do tropeço.'),
    'marina_discorda': ('A Marina DISCORDA na fala 5: começa com “Mas, Pablo Guru,” e faz uma '
                        'objeção honesta. A fala 6 acolhe a objeção antes de virar a perspectiva.'),
    'sem_pergunta': ('Final SEM pergunta: a fala 7 é uma imagem ou frase curta que fica ecoando, '
                     'terminando em ponto final, não em interrogação.'),
    'humor': ('Episódio LEVE, com humor gentil: a parábola tem uma situação engraçada '
              '(um gato, uma avó teimosa, um bolo que não cresce). O riso abre a porta para a virada.'),
    'caderno': ('Série do CADERNO: na fala 5 a Marina liga a descoberta ao que anotou no episódio '
                'anterior (“Isso lembra o que eu anotei ontem: …”), citando a frase de ontem '
                'enviada em frase_de_ontem. Continua fazendo sentido para quem não viu o anterior.'),
}

ORDEM_PUBLICOS = list(PUBLICOS)
ORDEM_FORMATOS = ['parabola', 'erro_do_pablo', 'humor', 'marina_discorda', 'caderno',
                  'parabola', 'sem_pergunta']


def publico_do_dia(dia: str, slot: int = 0) -> str:
    """Público do dia (e do horário, no TikTok): nunca repete em dias seguidos."""
    n = date.fromisoformat(dia).toordinal() * 3 + slot
    return ORDEM_PUBLICOS[(n * 5) % len(ORDEM_PUBLICOS)]


def formato_do_dia(dia: str, slot: int = 0) -> str:
    n = date.fromisoformat(dia).toordinal() + slot * 2
    return ORDEM_FORMATOS[n % len(ORDEM_FORMATOS)]


def hashtags(publico: str | None) -> list[str]:
    return list(PUBLICOS.get(publico or '', {}).get('hashtags', []))
