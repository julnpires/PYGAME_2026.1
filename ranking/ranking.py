import json
import os
from datetime import datetime

_DIR = os.path.dirname(__file__)
ARQUIVO_RANKING = os.path.join(_DIR, "ranking_golf.json")


def carregar_ranking():
    if not os.path.exists(ARQUIVO_RANKING):
        return {"all_time": []}
    try:
        with open(ARQUIVO_RANKING, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"all_time": []}


def salvar_ranking(data):
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def adicionar_ao_ranking(jogadores, num_fases):
    data = carregar_ranking()
    hoje = datetime.now().strftime("%Y-%m-%d %H:%M")

    for j in jogadores:
        total = j.total()
        media = round(total / num_fases, 2)

        data["all_time"].append({
            "nome": j.nome,
            "total_tacadas": total,
            "fases": num_fases,
            "media": media,
            "data": hoje,
        })

    data["all_time"].sort(key=lambda e: (e["media"], e["total_tacadas"]))
    data["all_time"] = data["all_time"][:50]

    salvar_ranking(data)
    return data
