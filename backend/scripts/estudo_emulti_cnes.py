"""Spike 3.1b: a perda de eMulti informada é explicada pelos profissionais do CNES? (somente leitura)

Pré-requisito: cache do Ministério preenchido por `estudo_regras_perda.py baixar`.
Coleta o CNES (API web) de cada município com competência >= 202512 e cruza com a perda informada.
Cache do CNES: ~/.cache/maispap-cnes (ou MAISPAP_CACHE_CNES).

Uso (a partir de backend/): .venv/bin/python scripts/estudo_emulti_cnes.py [municipios_editados.json]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.services.cnes import cnes_client, emulti_regras  # noqa: E402

CACHE_MIN = os.environ.get("MAISPAP_CACHE_MINISTERIO", os.path.expanduser("~/.cache/maispap-ministerio"))
CACHE_CNES = os.environ.get("MAISPAP_CACHE_CNES", os.path.expanduser("~/.cache/maispap-cnes"))


def g(p, k):
    return p.get(k) or 0


def main(caminho):
    os.makedirs(CACHE_CNES, exist_ok=True)
    editados = json.load(open(caminho, encoding="utf-8"))
    linhas = []
    for chave, v in sorted(editados.items()):
        if chave[-6:] < "202512":
            continue
        f_min = os.path.join(CACHE_MIN, f"{chave}.json")
        if not os.path.exists(f_min):
            continue
        pg = json.load(open(f_min, encoding="utf-8")).get("pagamentos") or []
        if not pg:
            continue
        p = pg[0]
        ibge = chave[:6]
        f_cnes = os.path.join(CACHE_CNES, f"{ibge}.json")
        if not os.path.exists(f_cnes):
            json.dump(cnes_client.coletar_municipio(ibge), open(f_cnes, "w", encoding="utf-8"), ensure_ascii=False)
        d = json.load(open(f_cnes, encoding="utf-8"))
        indice = emulti_regras.construir_indice_cbo(emulti_regras.agregar_por_cbo(d["profissionais"]))
        comp = emulti_regras.avaliar_modalidade(indice, "complementar")
        perdas = v["perda_recurso_mensal"]
        linhas.append({
            "chave": chave,
            "T": g(p, "qtEsfCredenciado") + g(p, "qtEapCredenciadas"),
            "T_cnes": cnes_client.contar_equipes_aps(d["equipes"]),
            "custeio_atual": g(p, "vlPagamentoEmultiCusteio"),
            "perda": perdas[2] if len(perdas) > 2 and perdas[2] else 0,
            "ch_elegivel": comp["ch_elegivel"],
            "grupos_fixos_ok": comp["grupos_fixos_ok"],
        })
    for r in sorted(linhas, key=lambda r: r["T"]):
        print(f"{r['chave']:15} T={r['T']:>3} (CNES {r['T_cnes']:>3}) atual={r['custeio_atual']:>8,.0f} "
              f"perda={r['perda']:>9,.0f} CH elegível={r['ch_elegivel']:>6} fixos={'S' if r['grupos_fixos_ok'] else 'N'}")
    sem_restricao = sum(1 for r in linhas if r["grupos_fixos_ok"] and r["ch_elegivel"] >= 200)
    print(f"\n{sem_restricao} de {len(linhas)} municípios têm grupos fixos e CH para ao menos uma Complementar")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "municipios_editados.json")
