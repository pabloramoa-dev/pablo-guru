"""Carrossel diário das 18h — "A bolha da espiritualidade" (v1, 23/09/2026).

Série de carrosséis que olham com carinho e honestidade para as ideias que
circulam na bolha espiritual da internet: o que cada uma tem de verdade, o que
virou clichê e o que merece ser repensado. O Pablo Guru não debocha de quem
busca — ele ajuda a buscar melhor.

Este arquivo tem o BANCO INICIAL (roteiros revisados à mão, um por dia a partir
de INICIO) e a lista de TEMAS que o gerador usa quando o banco acaba.
"""
from __future__ import annotations

INICIO = '2026-09-23'

HASHTAGS_BASE = ['#pabloguru', '#espiritualidade', '#bolhaespiritual', '#autoconhecimento', '#despertar']

BANCO = [
    {
        'id': 'positividade-toxica',
        'titulo': 'Vibre alto: quando a luz vira mordaça',
        'subtitulo': 'Positividade tóxica e o que ela cala',
        'slides': [
            ('O que é', 'Positividade tóxica é exigir bom humor o tempo todo, até de quem está sofrendo. Parece luz. Na prática, pede silêncio sobre a dor.'),
            ('Como ela aparece', '“Pensa positivo.” “Não atrai isso.” “Tem gente pior.” Frases ditas com carinho que fecham a conversa em vez de abrir.'),
            ('O que ela esconde', 'Tristeza, raiva e medo não são falhas de vibração. São informações. Quem só aceita o agradável perde metade do mapa.'),
            ('O que ajuda de verdade', 'Ouvir antes de consertar. Perguntar “quer desabafar ou quer ideias?”. Deixar a pessoa sentir sem pressa de melhorar.'),
            ('Na sua vida', 'Onde você finge que está tudo bem para não parecer alguém de “baixa vibração”?'),
        ],
        'fechamento': 'A luz não precisa apagar a sombra para existir. Ela só precisa iluminar.',
        'legenda': 'Nem toda frase positiva é cuidado. Às vezes ela só pede para a dor ficar quieta.',
        'hashtags': ['#positividadetoxica', '#saudeemocional', '#acolhimento'],
    },
    {
        'id': 'bypass-espiritual',
        'titulo': 'Bypass espiritual: fugir pela porta da luz',
        'subtitulo': 'Quando a espiritualidade vira esconderijo',
        'slides': [
            ('De onde vem o termo', '“Spiritual bypassing” foi descrito pelo psicólogo John Welwood nos anos 1980: usar ideias espirituais para desviar de feridas que pedem cuidado.'),
            ('Como ele fala', '“Já perdoei.” “Isso é coisa do ego.” “Tudo acontece por um motivo.” Às vezes são verdades. Às vezes são atalhos para não sentir.'),
            ('O sinal de alerta', 'Se a prática deixa você mais calmo, mas incapaz de dizer o que sente, talvez ela esteja servindo de anestesia, não de caminho.'),
            ('O caminho do meio', 'Meditar e também conversar. Rezar e também pedir desculpas. Aceitar e também agir. Espiritualidade com os pés no chão.'),
            ('Pergunta honesta', 'Que dor você chama de “lição aprendida” só para não precisar olhar para ela?'),
        ],
        'fechamento': 'Ninguém atravessa um rio pulando a água. A travessia é pela água.',
        'legenda': 'A espiritualidade pode ser caminho ou esconderijo. A diferença está no que ela te ajuda a encarar.',
        'hashtags': ['#bypassespiritual', '#vidainterior', '#consciencia'],
    },
    {
        'id': 'frases-da-bolha',
        'titulo': '5 frases da bolha espiritual para repensar',
        'subtitulo': 'Ditas com amor, mas nem sempre ajudam',
        'slides': [
            ('“Tudo acontece por um motivo”', 'Pode consolar. Mas, dita a quem acabou de perder algo, soa como se a dor fosse merecida. Às vezes, “sinto muito” basta.'),
            ('“Você atrai tudo o que vive”', 'Pensamento importa. Mas dizer que alguém atraiu uma doença ou uma perda joga culpa em cima de quem já está sofrendo.'),
            ('“Afaste quem tem energia baixa”', 'Às vezes a pessoa “pesada” só está atravessando um inverno. Limite é saudável; descartar gente triste, nem tanto.'),
            ('“Gratidão sempre”', 'Gratidão é bonita quando nasce. Quando vira obrigação, só ensina a esconder o que dói.'),
            ('“Isso é coisa do ego”', 'Ego não é inimigo. É a parte de você que diz “eu existo”. Sem ele, nem daria para agradecer.'),
        ],
        'fechamento': 'Palavras bonitas também precisam de hora certa.',
        'legenda': 'Qual dessas você já ouviu num momento difícil? Qual delas você já disse?',
        'hashtags': ['#frasesespirituais', '#empatia', '#reflexao'],
    },
    {
        'id': 'sombra-jung',
        'titulo': 'Sombra: o que Jung disse e a bolha esqueceu',
        'subtitulo': 'Não é o seu lado mau. É o seu lado não visto.',
        'slides': [
            ('O conceito', 'Para Carl Jung, a sombra reúne partes de nós que não aceitamos e empurramos para fora da consciência. Não só defeitos: qualidades também.'),
            ('Como ela aparece', 'Na irritação exagerada com alguém. No “eu jamais faria isso”. Muitas vezes, o que mais incomoda no outro fala de nós.'),
            ('O que a bolha simplificou', '“Trabalhar a sombra” virou sinônimo de eliminar o negativo. A proposta de Jung era integrar: reconhecer e conversar, não exterminar.'),
            ('A sombra dourada', 'Autores junguianos lembram que também escondemos qualidades: a coragem que admiramos nos outros e não nos permitimos.'),
            ('Exercício simples', 'Pense em alguém que te irrita muito. Que qualidade dessa pessoa você não se permite ter?'),
        ],
        'fechamento': 'O que você não olha não desaparece. Só passa a decidir sem você ver.',
        'legenda': 'Sombra não é o seu lado ruim. É o lado que você ainda não conheceu.',
        'hashtags': ['#jung', '#sombra', '#psicologia'],
    },
    {
        'id': 'gratidao-obrigacao',
        'titulo': 'Gratidão não é mordaça',
        'subtitulo': 'Quando “seja grato” impede de dizer o que dói',
        'slides': [
            ('A gratidão que nasce', 'Nasce de perceber o que é bom. Estudos associam o hábito de notar o bom a mais bem-estar. Mas ela nasce, não se impõe.'),
            ('A gratidão obrigatória', '“Pelo menos você tem emprego.” “Tem gente pior.” Frases que usam a gratidão para calar uma queixa legítima.'),
            ('Dá para sentir as duas coisas', 'Grato pela casa e cansado dela. Grato pela família e magoado com ela. Sentimentos não fazem fila.'),
            ('O teste', 'Sua gratidão te deixa mais leve ou mais culpado? A leve abre espaço. A culpada só aperta.'),
            ('Prática de hoje', 'Escreva uma coisa pela qual você é grato e uma coisa que te incomoda. As duas são verdade.'),
        ],
        'fechamento': 'Agradecer pelo pão não obriga você a gostar da fome.',
        'legenda': 'Dá para ser grato e, mesmo assim, admitir que algo dói. Uma coisa não apaga a outra.',
        'hashtags': ['#gratidao', '#saudeemocional', '#honestidade'],
    },
    {
        'id': 'meditacao-mente-vazia',
        'titulo': 'Meditar não é esvaziar a mente',
        'subtitulo': 'O mito que faz muita gente desistir no terceiro dia',
        'slides': [
            ('O mito', '“Não consigo meditar, minha cabeça não para.” Quase todo mundo diz isso. É justamente aí que a prática começa.'),
            ('O que é, na prática', 'Em muitas tradições, meditar é notar para onde a atenção foi e trazê-la de volta. Voltar mil vezes é o exercício, não o erro.'),
            ('A imagem', 'A mente não é um copo a esvaziar. É um céu: as nuvens passam. Você aprende a ser o céu, não a nuvem.'),
            ('Começo possível', 'Três respirações contadas antes de começar o dia. Parece pouco. É uma porta.'),
            ('Sem competição', 'Não existe meditação bonita. Existe a sentada de hoje, do jeito que ela vier.'),
        ],
        'fechamento': 'Quem percebe que se distraiu já está meditando.',
        'legenda': 'Se a sua cabeça não para quando você medita, parabéns: você percebeu. Esse é o começo.',
        'hashtags': ['#meditacao', '#mindfulness', '#atencaoplena'],
    },
    {
        'id': 'desapego-frieza',
        'titulo': 'Desapego não é frieza',
        'subtitulo': 'A confusão mais comum da bolha espiritual',
        'slides': [
            ('O mal-entendido', 'Na bolha, desapego às vezes vira não se importar, não sentir falta, não se envolver. Isso tem outro nome: armadura.'),
            ('O sentido antigo', 'No budismo, o apego que gera sofrimento é o agarrar: exigir que algo não mude. Amar continua permitido.'),
            ('A imagem', 'Segurar um pássaro com a mão aberta. Ele pode ficar ou voar. Você continua amando o pássaro.'),
            ('Sinais de armadura', 'Evitar vínculos para não sofrer. Dizer “tanto faz” para tudo. Chamar medo de evolução espiritual.'),
            ('Pergunta', 'Você está soltando ou só fingindo que não quer mais?'),
        ],
        'fechamento': 'Desapegar é abrir a mão. Não é tirar o coração.',
        'legenda': 'Desapego não é deixar de amar. É parar de exigir que o amor fique do seu jeito.',
        'hashtags': ['#desapego', '#budismo', '#amor'],
    },
]

# Temas para o gerador depois do banco (sempre sobre a bolha espiritual).
TEMAS = [
    'Karma não é castigo: o que a palavra significa nas tradições de origem',
    'Lei da atração: o que ela acerta e o que ela esquece',
    'Manifestar ou agir? O perigo de esperar o universo',
    'Sincronicidade: o que Jung quis dizer e o que a internet diz',
    '"Energia": quando uma palavra explica tudo e nada',
    'Gurus de internet: sinais de alerta antes de seguir alguém',
    'Autocuidado virou consumo? Retiros, cristais e cursos',
    'Perdoar não é esquecer nem voltar a conviver',
    'Silêncio: a prática espiritual mais barata e mais difícil',
    'Espiritualidade sem religião: o que é e o que não é',
    'Ego não é vilão: o que ele faz por você',
    'Mercúrio retrógrado e a vontade de terceirizar a culpa',
    'Despertar espiritual não é se sentir superior',
    'Pessoas "de luz" também erram',
    'Propósito de vida: e se ele for pequeno e cotidiano?',
    'Presença: estar aqui é mais difícil do que parece',
    'Oração, meditação e pedido de ajuda podem andar juntos',
    'Escassez e abundância: quando o discurso ignora a realidade',
    'Aceitação não é resignação',
    'Rituais simples do dia a dia que já são espiritualidade',
    'O perigo de transformar cada problema em "lição"',
    'Solidão escolhida e isolamento: a diferença',
    'Compaixão começa em como você fala consigo',
    'Intuição ou medo? Como diferenciar',
    'Humildade espiritual: ninguém tem todas as respostas',
    'Recomeçar sem precisar de "um novo eu"',
    'O luto também é sagrado',
    'Limites saudáveis também são espiritualidade',
    'Vulnerabilidade não é fraqueza',
    'Comparação espiritual: a competição de quem é mais evoluído',
]
