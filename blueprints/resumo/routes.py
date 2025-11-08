from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import json, os, datetime
from pathlib import Path

resumo_bp = Blueprint("resumo_bp", __name__, template_folder="../../templates")

ESTOQUE_JSON = "dados/estoque/estoque.json"
RELATORIO_TXT = "dados/relatorio_saidas.txt"

def carregar_estoque():
    if not os.path.exists(ESTOQUE_JSON):
        return []
    with open(ESTOQUE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_estoque(data):
    with open(ESTOQUE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def carregar_pendente(paciente_id):
    pend_path = f"dados/pacientes/{paciente_id}/pendente.json"
    if not os.path.exists(pend_path):
        return {"items": []}
    with open(pend_path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_pendente(paciente_id, data):
    pend_path = f"dados/pacientes/{paciente_id}/pendente.json"
    with open(pend_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_relatorio(registro):
    os.makedirs(os.path.dirname(RELATORIO_TXT), exist_ok=True)
    # grava em formato JSON linha a linha (append)
    with open(RELATORIO_TXT, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


@resumo_bp.route("/<paciente_id>")
def resumo(paciente_id):
    pend = carregar_pendente(paciente_id)
    # calcula total
    total = sum(item["qty"] * int(item.get("unit_price", 0)) for item in pend["items"])
    # converte centavos para reais no template, ou passe centavos
    return render_template("resumo.html", paciente_id=paciente_id, pendente=pend, total_centavos=total)


@resumo_bp.route("/confirmar/<paciente_id>", methods=["POST"])
def confirmar(paciente_id):
    pend = carregar_pendente(paciente_id)
    if not pend or not pend.get("items"):
        return jsonify(success=False, mensagem="Carrinho vazio"), 400

    # Carrega estoque e aplica baixa
    estoque = carregar_estoque()
    # cria mapa id->item
    estoque_map = {it["id"]: it for it in estoque}

    # valida disponibilidade
    for it in pend["items"]:
        eid = it["id"]
        qtd = int(it["qty"])
        if estoque_map.get(eid, {}).get("quantidade", 0) < qtd:
            return jsonify(success=False, mensagem=f"Estoque insuficiente para {it['nome']}"), 400

    # aplica baixa
    for it in pend["items"]:
        eid = it["id"]
        qtd = int(it["qty"])
        estoque_map[eid]["quantidade"] -= qtd

    # salva estoque atualizado
    salvar_estoque(list(estoque_map.values()))

    # grava no historico do paciente (arquivo JSON)
    hist_path = f"dados/pacientes/{paciente_id}/historico.json"
    if not os.path.exists(hist_path):
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
    with open(hist_path, "r", encoding="utf-8") as f:
        historico = json.load(f)
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # cria registros individuais no histórico e também um registro resumido para o relatorio global
    for it in pend["items"]:
        registro = {
            "hora": now_str,
            "item": it["nome"],
            "tipo": it.get("tipo", ""),
            "paciente": paciente_id,
            "quantidade": int(it["qty"]),
            "valor_unit_centavos": int(it.get("unit_price", 0)),
            "valor_total_centavos": int(it.get("unit_price", 0)) * int(it["qty"])
        }
        historico.append(registro)
        # append no relatorio global (linha JSON por saída — conforme sua escolha)
        append_relatorio(registro)

    # salva histórico do paciente
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

    # limpa pendente
    salvar_pendente(paciente_id, {"items": []})

    return jsonify(success=True, mensagem="Consumo registrado com sucesso.")