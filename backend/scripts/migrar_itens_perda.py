"""Story 3.2: acrescenta `itens` (nome do plano por posição) aos registros antigos de perdas.

Usa as respostas do Ministério em cache (`estudo_regras_perda.py baixar`) para descobrir o
nome de cada posição (planos da esfera municipal, na ordem da API). Só preenche quando o
tamanho bate; os demais registros ficam como estão (o array posicional continua valendo).

Por padrão NÃO altera nada: grava o resultado em `<arquivo>.com_itens.json` para conferência.
Com `--aplicar`, faz backup (`<arquivo>.backup.<data>`) e substitui o arquivo de forma atômica.

Uso (a partir de backend/):
    .venv/bin/python scripts/migrar_itens_perda.py [municipios_editados.json] [--aplicar]
"""
import json
import os
import shutil
import sys
from datetime import datetime

CACHE_MIN = os.environ.get("MAISPAP_CACHE_MINISTERIO", os.path.expanduser("~/.cache/maispap-ministerio"))


def planos_municipais(resposta):
    return [r["dsPlanoOrcamentario"] for r in resposta.get("resumosPlanosOrcamentarios", [])
            if not r.get("dsEsferaAdministrativa") or r.get("dsEsferaAdministrativa") == "MUNICIPAL"]


def main(caminho, aplicar):
    dados = json.load(open(caminho, encoding="utf-8"))
    cont = {"já tinham itens": 0, "migrados": 0, "sem cache do Ministério": 0, "tamanho diferente": 0}
    for chave, reg in dados.items():
        if reg.get("itens"):
            cont["já tinham itens"] += 1
            continue
        f = os.path.join(CACHE_MIN, f"{chave}.json")
        if not os.path.exists(f):
            cont["sem cache do Ministério"] += 1
            continue
        planos = planos_municipais(json.load(open(f, encoding="utf-8")))
        perdas = reg.get("perda_recurso_mensal", [])
        if len(planos) != len(perdas):
            cont["tamanho diferente"] += 1
            continue
        reg["itens"] = [{"plano": p, "valor": v, "origem": "manual", "regra_id": None, "valor_sugerido": None}
                        for p, v in zip(planos, perdas)]
        cont["migrados"] += 1
    print(json.dumps(cont, ensure_ascii=False))

    if not aplicar:
        destino = f"{caminho}.com_itens.json"
        json.dump(dados, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Resultado salvo em {destino} (arquivo original intacto). Use --aplicar para substituir.")
        return
    backup = f"{caminho}.backup.{datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(caminho, backup)
    tmp = f"{caminho}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, caminho)
    print(f"Aplicado. Backup em {backup}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--aplicar"]
    main(args[0] if args else "municipios_editados.json", "--aplicar" in sys.argv)
