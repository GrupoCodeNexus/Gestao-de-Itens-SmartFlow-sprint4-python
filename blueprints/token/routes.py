from flask import Blueprint, render_template, request, jsonify, url_for, redirect
import json, os
from pathlib import Path

token_bp = Blueprint("token_bp", __name__, template_folder="../../templates")

ESTOQUE_JSON = "dados/estoque/estoque.json"
PACIENTES_JSON = "dados/pacientes/pacientes.json"

def carregar_estoque():
    if not os.path.exists(ESTOQUE_JSON):
        return []
    with open(ESTOQUE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_paciente(paciente_id):
    if not os.path.exists(PACIENTES_JSON):
        return None
    with open(PACIENTES_JSON, "r", encoding="utf-8") as f:
        pacientes = json.load(f)
    for p in pacientes:
        if p.get("id") == paciente_id:
            return p
    return None

def carregar_pendente(paciente_id):
    pend_path = f"dados/pacientes/{paciente_id}/pendente.json"
    if not os.path.exists(pend_path):
        os.makedirs(os.path.dirname(pend_path), exist_ok=True)
        with open(pend_path, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, indent=2, ensure_ascii=False)
    with open(pend_path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_pendente(paciente_id, data):
    pend_path = f"dados/pacientes/{paciente_id}/pendente.json"
    with open(pend_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@token_bp.route("/<paciente_id>")
def token_index(paciente_id):
    paciente = carregar_paciente(paciente_id)
    if not paciente:
        return f"Paciente {paciente_id} não encontrado", 404
    estoque = carregar_estoque()
    pendente = carregar_pendente(paciente_id)
    return render_template("token.html", paciente=paciente, estoque=estoque, pendente=pendente)


# API para listar estoque (frontend usa para renderizar cards)
@token_bp.route("/api/estoque", methods=["GET"])
def api_estoque():
    return jsonify(carregar_estoque())


# API pendente: obter
@token_bp.route("/api/pendente/<paciente_id>", methods=["GET"])
def api_get_pendente(paciente_id):
    return jsonify(carregar_pendente(paciente_id))


# API pendente: add item (body: item_id, qty)
@token_bp.route("/api/pendente/<paciente_id>/add", methods=["POST"])
def api_add_pendente(paciente_id):
    payload = request.get_json()
    item_id = payload.get("item_id")
    qty = int(payload.get("qty", 1))
    estoque = carregar_estoque()
    item = next((i for i in estoque if i.get("id") == item_id), None)
    if not item:
        return jsonify(success=False, mensagem="Item não encontrado"), 404
    if item.get("quantidade", 0) < qty:
        return jsonify(success=False, mensagem="Quantidade insuficiente em estoque"), 400

    pend = carregar_pendente(paciente_id)
    # se item já presente, soma
    found = next((it for it in pend["items"] if it["id"] == item_id), None)
    if found:
        found["qty"] += qty
    else:
        pend["items"].append({
            "id": item["id"],
            "nome": item["nome"],
            "tipo": item["tipo"],
            "qty": qty,
            "unit_price": item.get("cost_patient", 0)
        })
    salvar_pendente(paciente_id, pend)
    return jsonify(success=True, pendente=pend)


# API pendente: remove item (body: item_id, qty) -> decreases or removes
@token_bp.route("/api/pendente/<paciente_id>/remove", methods=["POST"])
def api_remove_pendente(paciente_id):
    payload = request.get_json()
    item_id = payload.get("item_id")
    qty = int(payload.get("qty", 1))
    pend = carregar_pendente(paciente_id)
    found = next((it for it in pend["items"] if it["id"] == item_id), None)
    if not found:
        return jsonify(success=False, mensagem="Item não no pendente"), 404
    found["qty"] -= qty
    if found["qty"] <= 0:
        pend["items"] = [it for it in pend["items"] if it["id"] != item_id]
    salvar_pendente(paciente_id, pend)
    return jsonify(success=True, pendente=pend)


# API pendente: clear
@token_bp.route("/api/pendente/<paciente_id>/clear", methods=["POST"])
def api_clear_pendente(paciente_id):
    pend = {"items": []}
    salvar_pendente(paciente_id, pend)
    return jsonify(success=True)