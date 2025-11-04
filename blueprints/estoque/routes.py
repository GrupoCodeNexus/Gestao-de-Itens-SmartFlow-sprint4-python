from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import json, os
from pathlib import Path


# Blueprint para manutenção do estoque que chama o ESTOQUE_JSON para atualizar saldo
estoque_bp = Blueprint("estoque_bp", __name__, template_folder="../../templates")

ESTOQUE_JSON = "dados/estoque/estoque.json"


def carregar_estoque():
    if not os.path.exists(ESTOQUE_JSON):
        os.makedirs(os.path.dirname(ESTOQUE_JSON), exist_ok=True)
        with open(ESTOQUE_JSON, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
    with open(ESTOQUE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_estoque(data):
    with open(ESTOQUE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@estoque_bp.route("/")
def ver_estoque():
    estoque = carregar_estoque()
    # converte centavos para reais para exibir? faremos no template
    return render_template("estoque.html", estoque=estoque, success_message=request.args.get('success_message'), error_message=request.args.get('error_message'))


@estoque_bp.route("/api/list", methods=["GET"])
def api_list():
    return jsonify(carregar_estoque())


@estoque_bp.route("/adicionar", methods=["POST"])
def adicionar():
    data = carregar_estoque()
    codigo = request.form.get("codigo", "").strip()
    nome = request.form.get("nome", "").strip()
    tipo = request.form.get("tipo", "").strip()
    quantidade = int(request.form.get("quantidade", "0"))
    # valores em centavos
    cost_purchase = int(float(request.form.get("cost_purchase", "0")) * 100)
    cost_internal = int(float(request.form.get("cost_internal", "0")) * 100)
    cost_patient = int(float(request.form.get("cost_patient", "0")) * 100)

    novo = {
        "id": codigo,
        "nome": nome,
        "tipo": tipo,
        "quantidade": quantidade,
        # Separado CUSTO em 3 tipos de custos a nível ERP

        "cost_purchase": cost_purchase, #quanto hospital paga para comprar esse medicamento / item
        "cost_internal": cost_internal, # custo contábil interno hospital (custo para repor aquele carrinho)
        "cost_patient": cost_patient # preço de cobrança do paciente / plano / SUS
    }
    data.append(novo)
    salvar_estoque(data)
    return redirect(url_for("estoque_bp.ver_estoque", success_message="Item adicionado com sucesso."))


@estoque_bp.route("/remover", methods=["POST"])
def remover():
    codigo = request.form.get("codigo")
    data = carregar_estoque()
    nova = [i for i in data if i.get("id") != codigo]
    if len(nova) == len(data):
        return redirect(url_for("estoque_bp.ver_estoque", error_message="Item não encontrado."))
    salvar_estoque(nova)
    return redirect(url_for("estoque_bp.ver_estoque", success_message="Item removido."))


@estoque_bp.route("/update_quantity", methods=["POST"])
def update_quantity():
    # API para reduzir/ajustar quantidades (usada ao confirmar consumo)
    payload = request.get_json()
    item_id = payload.get("item_id")
    delta = int(payload.get("delta", 0))  # pode ser negativo
    estoque = carregar_estoque()
    for it in estoque:
        if it.get("id") == item_id:
            it["quantidade"] = max(0, it.get("quantidade", 0) + delta)
            salvar_estoque(estoque)
            return jsonify(success=True, item=it)
    return jsonify(success=False, mensagem="Item não encontrado"), 404
