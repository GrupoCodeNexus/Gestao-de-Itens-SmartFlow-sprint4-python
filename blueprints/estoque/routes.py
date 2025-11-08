from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import os, json
from pathlib import Path

estoque_bp = Blueprint("estoque_bp", __name__, template_folder="../../templates")

ESTOQUE_JSON = "dados/estoque/estoque.json"
PER_PAGE = 30

# mapa gaveta -> prefixo (conforme definido)
GAVETA_PREFIX = {
    "g1ABT": "Antibioticos",  # Antibióticos
    "g2CRS": "Curativos / Sutura",  # Curativos / Sutura
    "g3IA": "IA (anti-inflamatórios / analgesia / antitérmico)",    # IA (anti-inflamatórios / analgesia / antitérmico)
    "g4SCD": "Sedação e Controle de Dor",  # Sedação e Controle de Dor
    "g5E1": "Emergência 1",    # Emergência 1
    "g6E2": "Emergência 2"     # Emergência 2
}

TYPES_LIST = [
    ("mg", "mg (miligramas)"),
    ("g", "g (gramas)"),
    ("ml", "ml (mililitros)"),
    ("un", "un (unidade)"),
    ("comprimido", "comprimido"),
    ("caps", "cápsula")
]

def carregar_estoque():
    if not os.path.exists(ESTOQUE_JSON):
        return []
    try:
        with open(ESTOQUE_JSON, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception:
        return []

def salvar_estoque(data):
    os.makedirs(os.path.dirname(ESTOQUE_JSON), exist_ok=True)
    with open(ESTOQUE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_id_for_gaveta(gaveta):
    """
    Gera ID incremental por gaveta. Ex: g1ABT001, g1ABT002...
    """
    estoque = carregar_estoque()
    prefix = GAVETA_PREFIX.get(gaveta, gaveta)
    # contar quantos já existem com esse prefixo
    existing = [it for it in estoque if it.get("gaveta") == gaveta]
    # sequencial com 3 dígitos
    seq = len(existing) + 1
    return f"{prefix}{seq:03d}"

@estoque_bp.route("/")
def listar_estoque():
    # query params: page, q (search), gaveta
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "").strip().lower()
    gaveta_filter = request.args.get("gaveta", "").strip()

    itens = carregar_estoque()

    # search (nome ou id)
    if q:
        itens = [it for it in itens if q in it.get("nome", "").lower() or q in it.get("id", "").lower()]

    # filter by gaveta
    if gaveta_filter:
        itens = [it for it in itens if it.get("gaveta") == gaveta_filter]

    total = len(itens)
    # pagination
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = itens[start:end]

    # calcular número de páginas
    total_pages = (total + PER_PAGE - 1) // PER_PAGE if total > 0 else 1

    return render_template(
        "estoque.html",
        estoque=page_items,
        page=page,
        total_pages=total_pages,
        q=request.args.get("q", ""),
        gaveta_filter=gaveta_filter,
        gavetas=GAVETA_PREFIX,
        types_list=TYPES_LIST
    )

@estoque_bp.route("/adicionar", methods=["POST"])
def adicionar_item():
    data = carregar_estoque()
    form = request.form

    # campos do formulário
    nome = form.get("nome", "").strip()
    presentation_value = form.get("presentation_value", "").strip()
    tipo = form.get("tipo", "").strip()  # unidade ex: mg
    gaveta = form.get("gaveta", "").strip()  # ex: g1ABT
    quantidade = form.get("quantidade", "0").strip()
    descricao = form.get("descricao", "").strip()
    image = None  # futuro
    # custos enviados em reais (ex: 80.00) -> converter para centavos int
    def reais_to_centavos(s):
        try:
            v = float(s.replace(",", "."))
            return int(round(v * 100))
        except Exception:
            return 0

    cost_purchase = reais_to_centavos(form.get("cost_purchase", "0"))
    cost_internal = reais_to_centavos(form.get("cost_internal", "0"))
    cost_patient = reais_to_centavos(form.get("cost_patient", "0"))

    # validações mínimas
    if not nome or not presentation_value or not tipo or not gaveta:
        return redirect(url_for("estoque_bp.listar_estoque", error_message="Campos obrigatórios faltando"))

    try:
        presentation_value_int = int(presentation_value)
    except:
        presentation_value_int = 0

    try:
        quantidade_int = int(quantidade)
    except:
        quantidade_int = 0

    new_id = generate_id_for_gaveta(gaveta)

    novo_item = {
        "id": new_id,
        "nome": nome,
        "presentation_value": presentation_value_int,
        "tipo": tipo,
        "presentation_display": None,  # não salvo a string final redundante
        "quantidade": quantidade_int,
        "gaveta": gaveta,
        "cost_purchase": cost_purchase,
        "cost_internal": cost_internal,
        "cost_patient": cost_patient,
        "image": None,
        "descricao": descricao
    }

    data.append(novo_item)
    salvar_estoque(data)
    return redirect(url_for("estoque_bp.listar_estoque"))

@estoque_bp.route("/estoque/get/<item_id>", methods=["GET"])
def get_item(item_id):
    itens = carregar_estoque()
    for it in itens:
        if it.get("id") == item_id:
            return jsonify(success=True, item=it)
    return jsonify(success=False, mensagem="Item não encontrado"), 404

@estoque_bp.route("/estoque/editar/<item_id>", methods=["POST"])
def editar_item(item_id):
    itens = carregar_estoque()
    form = request.form

    # localizar índice
    for idx, it in enumerate(itens):
        if it.get("id") == item_id:
            # atualizar campos (quantidade é absoluto)
            nome = form.get("nome", "").strip()
            presentation_value = form.get("presentation_value", "").strip()
            tipo = form.get("tipo", "").strip()
            gaveta = form.get("gaveta", "").strip()
            quantidade = form.get("quantidade", "0").strip()
            descricao = form.get("descricao", "").strip()

            def reais_to_centavos(s):
                try:
                    v = float(s.replace(",", "."))
                    return int(round(v * 100))
                except Exception:
                    return 0

            cost_purchase = reais_to_centavos(form.get("cost_purchase", "0"))
            cost_internal = reais_to_centavos(form.get("cost_internal", "0"))
            cost_patient = reais_to_centavos(form.get("cost_patient", "0"))

            # validations & conversions
            try:
                presentation_value_int = int(presentation_value)
            except:
                presentation_value_int = it.get("presentation_value", 0)

            try:
                quantidade_int = int(quantidade)
            except:
                quantidade_int = it.get("quantidade", 0)

            # atualiza
            it.update({
                "nome": nome or it.get("nome"),
                "presentation_value": presentation_value_int,
                "tipo": tipo or it.get("tipo"),
                "quantidade": quantidade_int,
                "gaveta": gaveta or it.get("gaveta"),
                "cost_purchase": cost_purchase,
                "cost_internal": cost_internal,
                "cost_patient": cost_patient,
                "descricao": descricao
            })

            # salva
            itens[idx] = it
            salvar_estoque(itens)
            return jsonify(success=True, item=it)

    return jsonify(success=False, mensagem="Item não encontrado"), 404

@estoque_bp.route("/estoque/remover/<item_id>", methods=["POST"])
def remover_item(item_id):
    itens = carregar_estoque()
    for idx, it in enumerate(itens):
        if it.get("id") == item_id:
            removed = itens.pop(idx)
            salvar_estoque(itens)
            return jsonify(success=True, mensagem=f"Item {removed.get('nome')} removido.")
    return jsonify(success=False, mensagem="Item não encontrado"), 404
