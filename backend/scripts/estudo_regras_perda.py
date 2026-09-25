"""Estudo das regras de perda (story 3.1): compara as perdas informadas com a API do Ministério.

Somente leitura: não altera nenhum arquivo do projeto. As respostas da API ficam em cache
fora do repositório (padrão: ~/.cache/maispap-ministerio).

Uso:
    python backend/scripts/estudo_regras_perda.py baixar   [municipios_editados.json]
    python backend/scripts/estudo_regras_perda.py analisar [municipios_editados.json]
"""
import collections
import json
import os
import sys
import time

URL = "https://relatorioaps-prd.saude.gov.br/financiamento/pagamento"
CACHE = os.environ.get("MAISPAP_CACHE_MINISTERIO", os.path.expanduser("~/.cache/maispap-ministerio"))
VALOR_ACS = 3242          # valor por ACS usado pelo usuário (Ministério pagava 3.036 em 2025)
BOM_PARA_OTIMO_ESF = 4000  # +2.000 vínculo +2.000 qualidade por equipe
EXTRA_NOVA_ESF = 16000     # vínculo + qualidade ÓTIMO de uma equipe nova (8.000 + 8.000)


def carregar_editados(caminho):
    return json.load(open(caminho, encoding="utf-8"))


def baixar(editados):
    import httpx
    os.makedirs(CACHE, exist_ok=True)
    headers = {"Accept": "application/json", "User-Agent": "papprefeito-ConsultaDados/1.0"}
    with httpx.Client(timeout=60, headers=headers) as client:
        for i, chave in enumerate(editados, 1):
            destino = os.path.join(CACHE, f"{chave}.json")
            if os.path.exists(destino):
                continue
            ibge, comp = chave.split("_")
            ibge = ibge[:6]
            params = {"unidadeGeografica": "MUNICIPIO", "coUf": ibge[:2], "coUfIbge": ibge[:2],
                      "coMunicipio": ibge, "coMunicipioIbge": ibge, "nuParcelaInicio": comp,
                      "nuParcelaFim": comp, "tipoRelatorio": "COMPLETO"}
            for tentativa in range(3):
                try:
                    r = client.get(URL, params=params)
                    r.raise_for_status()
                    json.dump(r.json(), open(destino, "w", encoding="utf-8"), ensure_ascii=False)
                    print(i, chave, "ok", flush=True)
                    break
                except Exception as e:  # noqa: BLE001
                    print(i, chave, "erro", type(e).__name__, flush=True)
                    time.sleep(3 * (tentativa + 1))
            time.sleep(0.5)


def g(p, k):
    return p.get(k) or 0


def perda(ps, i):
    return ps[i] if len(ps) > i and ps[i] else 0


def regra_acs(p):
    return (g(p, "qtAcsDiretoCredenciado") - g(p, "qtAcsDiretoPgto")) * VALOR_ACS


def regra_esf(p):
    n = g(p, "qtEsfTotalPgto")
    fixo = round(g(p, "vlFixoEsf") / n, -3) if n else 0
    novas = max(g(p, "qtTetoEsf") - g(p, "qtEsfCredenciado"), 0)
    return n * BOM_PARA_OTIMO_ESF + novas * (fixo + EXTRA_NOVA_ESF)


def analisar(editados):
    linhas = []
    for chave, v in editados.items():
        f = os.path.join(CACHE, f"{chave}.json")
        if not os.path.exists(f):
            continue
        pg = json.load(open(f, encoding="utf-8")).get("pagamentos") or []
        if pg:
            linhas.append((chave, v["perda_recurso_mensal"], pg[0]))
    print(f"registros com dados do Ministério: {len(linhas)} de {len(editados)}")
    for nome, idx, regra, unidade in [("ACS", 3, regra_acs, VALOR_ACS), ("eSF/eAP", 0, regra_esf, None)]:
        c = collections.defaultdict(collections.Counter)
        for chave, ps, p in linhas:
            v = perda(ps, idx)
            if v <= 0:
                continue
            era = "até 202510" if chave[-6:] <= "202510" else "desde 202512"
            c[era]["n"] += 1
            if abs(regra(p) - v) <= 1:
                c[era]["regra exata"] += 1
            if unidade and abs(v / unidade - round(v / unidade)) < 1e-6:
                c[era][f"múltiplo de {unidade}"] += 1
            if unidade and abs(v - regra(p)) <= 2 * unidade:
                c[era]["regra ±2 unidades"] += 1
        print(f"\n== {nome}")
        for era, cnt in sorted(c.items()):
            n = cnt.pop("n")
            print(f"  {era} (n={n}): " + ", ".join(f"{k} {q} ({q / n:.0%})" for k, q in cnt.items()))


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "analisar"
    caminho = sys.argv[2] if len(sys.argv) > 2 else "backend/municipios_editados.json"
    dados = carregar_editados(caminho)
    baixar(dados) if acao == "baixar" else analisar(dados)
