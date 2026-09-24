"""
Regras da eMulti pela Portaria GM/MS nº 635/2023 e confronto com os profissionais do CNES.

Origem: maisprofissionais/emulti_utils.py (dados da Portaria, mapeamento de CBO e
agregação). A geração da planilha Excel não foi copiada; `avaliar_modalidade`
reproduz a análise de elegibilidade que lá é feita em `write_aba2`.
"""

# === DADOS DA PORTARIA 635/2023 ===

MODALIDADES = {
    'estrategica': {
        'nome': 'Estratégica', 'ch_min': 100, 'equipes': '1 a 4',
        'max_cat': 40, 'custeio': 'R$ 12.000',
        'fixas': [
            {'grupo': 'Grupo Único (pelo menos 1)', 'opcoes': [
                ('Nutricionista', '2237-10'),
                ('Psicólogo(a)', '2515-10'),
            ]}
        ]
    },
    'complementar': {
        'nome': 'Complementar', 'ch_min': 200, 'equipes': '5 a 9',
        'max_cat': 80, 'custeio': 'R$ 24.000',
        'fixas': [
            {'grupo': 'Grupo 1 (pelo menos 1)', 'opcoes': [
                ('Assistente Social', '2516-05'),
                ('Farmacêutico(a) Clínico(a)', '2234-45'),
                ('Nutricionista', '2237-10'),
                ('Psicólogo(a)', '2515-10'),
            ]},
            {'grupo': 'Grupo 2 (pelo menos 1)', 'opcoes': [
                ('Fisioterapeuta', '2236-05'),
                ('Fonoaudiólogo(a)', '2238-10'),
                ('Prof. de Educação Física na Saúde', '2241-40'),
                ('Terapeuta Ocupacional', '2239-05'),
            ]}
        ]
    },
    'ampliada': {
        'nome': 'Ampliada', 'ch_min': 300, 'equipes': '10 a 12',
        'max_cat': 120, 'custeio': 'R$ 36.000',
        'fixas': [
            {'grupo': 'Grupo 1 (pelo menos 1)', 'opcoes': [
                ('Assistente Social', '2516-05'),
                ('Farmacêutico(a) Clínico(a)', '2234-45'),
                ('Nutricionista', '2237-10'),
                ('Psicólogo(a)', '2515-10'),
            ]},
            {'grupo': 'Grupo 2 (pelo menos 1)', 'opcoes': [
                ('Fisioterapeuta', '2236-05'),
                ('Fonoaudiólogo(a)', '2238-10'),
                ('Prof. de Educação Física na Saúde', '2241-40'),
                ('Terapeuta Ocupacional', '2239-05'),
            ]}
        ]
    }
}

VARIAVEIS = [
    ('Arte Educador', '5153-05'),
    ('Assistente Social', '2516-05'),
    ('Farmacêutico(a) Clínico(a)', '2234-45'),
    ('Fisioterapeuta', '2236-05'),
    ('Fonoaudiólogo(a)', '2238-10'),
    ('Médico(a) Acupunturista', '2251-05'),
    ('Médico(a) Cardiologista', '2251-20'),
    ('Médico(a) Dermatologista', '2251-35'),
    ('Médico(a) Endocrinologista', '2251-55'),
    ('Médico(a) Geriatra', '2251-80'),
    ('Médico(a) Ginecologista/Obstetra', '2252-50'),
    ('Médico(a) Hansenologista', '2251-35'),
    ('Médico(a) Homeopata', '2251-95'),
    ('Médico(a) Infectologista', '2251-03'),
    ('Médico(a) Pediatra', '2251-24'),
    ('Médico(a) Psiquiatra', '2251-33'),
    ('Médico(a) Veterinário(a)', '2233-05'),
    ('Nutricionista', '2237-10'),
    ('Prof. de Educação Física na Saúde', '2241-40'),
    ('Psicólogo(a)', '2515-10'),
    ('Sanitarista', '1312-25'),
    ('Terapeuta Ocupacional', '2239-05'),
]

# Mapeamento flexível: CBO CNES → CBO Portaria (para matching)
CBO_MAP = {
    '2516-05': '2516-05',  # Assistente Social
    '2234-45': '2234-45',  # Farmacêutico Clínico (match direto)
    '2234-05': '2234-05',  # Farmacêutico genérico (NÃO é match direto com 2234-45)
    '2237-10': '2237-10',  # Nutricionista
    '2515-10': '2515-10',  # Psicólogo
    '2515-05': '2515-10',  # Psicólogo social → aceitar como Psicólogo
    '2236-05': '2236-05',  # Fisioterapeuta
    '2238-10': '2238-10',  # Fonoaudiólogo
    '2241-40': '2241-40',  # Ed. Física
    '2239-05': '2239-05',  # Terapeuta Ocupacional
    '5153-05': '5153-05',  # Arte Educador
    '2251-05': '2251-05',  # Acupunturista
    '2251-20': '2251-20',  # Cardiologista
    '2251-35': '2251-35',  # Dermatologista/Hansenologista
    '2251-55': '2251-55',  # Endocrinologista
    '2251-80': '2251-80',  # Geriatra
    '2252-50': '2252-50',  # Gineco/Obstetra
    '2251-95': '2251-95',  # Homeopata
    '2251-03': '2251-03',  # Infectologista
    '2251-24': '2251-24',  # Pediatra
    '2251-33': '2251-33',  # Psiquiatra
    '2233-05': '2233-05',  # Veterinário
    '1312-25': '1312-25',  # Sanitarista
}

def agregar_por_cbo(profissionais):
    """
    Agrega os profissionais vindos da API do CNES por CBO.

    Returns:
        dict {cbo: {'nome': descrição do CBO, 'qtd': int, 'ch': carga horária semanal}}
    """
    agregado = {}
    for p in profissionais:
        cbo = p.get('cbo_fmt') or ''
        if not cbo:
            continue
        item = agregado.setdefault(cbo, {'nome': p.get('dsCbo', ''), 'qtd': 0,
                                         'ch': 0, 'cns': set()})
        # 'qtd' conta vínculos; 'cns' guarda as pessoas distintas — um mesmo
        # profissional pode ter vínculo em mais de uma unidade do município.
        item['qtd'] += 1
        item['ch'] += int(p.get('ch_total') or 0)
        if p.get('cns'):
            item['cns'].add(p['cns'])
    return agregado


def construir_indice_cbo(agregado):
    """
    Índice para confronto com a Portaria, aplicando as equivalências de CBO_MAP.

    Ex.: 2515-05 (psicólogo social) é contabilizado como 2515-10 (psicólogo).
    O CBO originalmente cadastrado é preservado em 'cbos_origem' para que a
    planilha possa mostrar o que está de fato no SCNES.
    """
    indice = {}
    for cbo, item in agregado.items():
        destino = CBO_MAP.get(cbo, cbo)
        alvo = indice.setdefault(destino, {'nome': item['nome'], 'qtd': 0, 'ch': 0,
                                           'cns': set(), 'cbos_origem': []})
        alvo['qtd'] += item['qtd']
        alvo['ch'] += item['ch']
        alvo['cns'] |= item['cns']
        alvo['cbos_origem'].append(cbo)
    return indice


# === Complementos para o cálculo de perda (não existem no original) ===

# Custeio federal mensal em reais e faixa de eSF/eAP vinculadas por modalidade
CUSTEIO = {'estrategica': 12000, 'complementar': 24000, 'ampliada': 36000}
FAIXA_EQUIPES = {'estrategica': (1, 4), 'complementar': (5, 9), 'ampliada': (10, 12)}


def avaliar_modalidade(cbo_index, modalidade_key):
    """
    Confronta a composição exigida pela modalidade com os profissionais do CNES.

    Mesma lógica de write_aba2 do original: cada grupo fixo precisa de ao menos uma
    categoria disponível (o Farmacêutico genérico 2234-05 conta como "verificar"), e
    a CH das categorias elegíveis (fixas + variáveis) é somada.

    Returns:
        dict com 'grupos_fixos_ok' (bool), 'grupos_verificar' (bool),
        'ch_elegivel' (int) e 'ch_suficiente' (bool).
    """
    mod = MODALIDADES[modalidade_key]
    grupos_ok, verificar = True, False
    elegiveis = {}
    for grupo in mod['fixas']:
        atendido = False
        for _cat, cbo in grupo['opcoes']:
            if cbo in cbo_index:
                atendido = True
                elegiveis[cbo] = cbo_index[cbo]['ch']
            elif cbo == '2234-45' and '2234-05' in cbo_index:
                verificar = True
                elegiveis['2234-05'] = cbo_index['2234-05']['ch']
        grupos_ok = grupos_ok and atendido
    for _cat, cbo in VARIAVEIS:
        if cbo in cbo_index:
            elegiveis[cbo] = cbo_index[cbo]['ch']
    ch = sum(elegiveis.values())
    return {
        'grupos_fixos_ok': grupos_ok,
        'grupos_verificar': verificar,
        'ch_elegivel': ch,
        'ch_suficiente': ch >= mod['ch_min'],
    }
