from flask import Blueprint, render_template, request, redirect, url_for
import json, os
from pathlib import Path

paciente_bp = Blueprint("paciente_bp", __name__, template_folder="../../templates")

PACIENTES_JSON = "dados/pacientes/pacientes.json"


def carregar_pacientes():
    if not os.path.exists('dados/pacientes.json'):
        return []

    if os.path.getsize('dados/pacientes.json') == 0:
        return []

    with open('dados/pacientes.json', 'r') as f:
        return json.load(f)



def salvar_pacientes(data):
    with open(PACIENTES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@paciente_bp.route("/selecionar")
def selecionar():
    pacientes = carregar_pacientes()
    return render_template("selecionar_paciente.html", pacientes=pacientes)


@paciente_bp.route("/criar", methods=["POST"])
def criar():
    pacientes = carregar_pacientes()

    nome = request.form.get("nome", "").strip()
    idade = request.form.get("idade", "0").strip()
    responsavel = request.form.get("responsavel", "").strip()
    local = request.form.get("local", "0").strip()
    observacao = request.form.get("observacao", "").strip()

    novo_id = f"P{len(pacientes)+1:04d}"

    novo_paciente = {
        "id": novo_id,
        "nome": nome,
        "idade": int(idade) if idade.isdigit() else 0,
        "responsável": responsavel,
        "local": int(local) if str(local).isdigit() else local,
        "observação": observacao
    }

    pacientes.append(novo_paciente)
    salvar_pacientes(pacientes)

    # cria pasta do paciente
    pasta = f"dados/pacientes/{novo_id}"
    Path(pasta).mkdir(parents=True, exist_ok=True)

    # cria historico inicial e pendente
    hist_path = f"{pasta}/historico.json"
    pend_path = f"{pasta}/pendente.json"
    if not os.path.exists(hist_path):
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    if not os.path.exists(pend_path):
        with open(pend_path, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, indent=2, ensure_ascii=False)

    return redirect(url_for("token_bp.token_index", paciente_id=novo_id))


@paciente_bp.route("/entrar/<paciente_id>")
def entrar(paciente_id):
    # redireciona para token do paciente
    return redirect(url_for("token_bp.token_index", paciente_id=paciente_id))
