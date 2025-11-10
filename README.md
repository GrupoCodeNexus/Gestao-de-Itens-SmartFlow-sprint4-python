# SmartFlow | Sprint 4

Este repositório apresenta a quarta sprint do SmartFlow, um sistema de controle e rastreamento de medicamentos para carrinhos de emergência. O objetivo principal do projeto é garantir segurança, controle e visibilidade no fluxo de suprimentos médicos.

## Resumo do Sistema:

Sistema de controle, rastreamento e responsabilização na retirada de medicamentos em carrinhos de emergência hospitalares

O sistema rastreia a saída de medicamentos do carrinho de emergência e os atrela diretamente à ficha de cada paciente. Para hospitais particulares, isso permite uma gestão de estoque precisa e uma cobrança eficiente, vinculando o uso do medicamento à conta do paciente de forma automatizada e segura.

<img width="1024" height="883" alt="image" src="https://github.com/user-attachments/assets/d59cfef7-3977-44dc-bdc3-cd4ba3fda8bc" />

## Objetivo
O objetivo é garantir segurança, rastreabilidade, redução de perdas e vinculação direta à ficha do paciente.
Toda saída de item do carrinho é registrada e vinculada ao paciente, gerando histórico e suporte à cobrança hospitalar.


- 🔗 Integração com IoT (ESP32 + RFID + Servo + LED)
- 🧠 Cadastro de Cartões RFID Autorizados:
- 📄 Geração e Download de Relatório
- ⚡ Alerta em Tempo Real no Navegador
- 🧑‍⚕️ Interface Simples e Clara para Enfermeiras

## Diagrama
![diag](https://github.com/user-attachments/assets/f402abbc-c8b5-4ddd-8ffc-82673ec3c583)

## Links úteis
Acessar o vídeo da solução no YouTube: <a href="https://www.youtube.com/watch?v=0GjBcsHMnXQ">Clique Aqui</a>

## Tecnologias utilizadas
- Python
- Flask
- SocketIO (tempo real)
- JSON para banco local
- Tailwind

## Como instalar e rodar o projeto

**Pré requisitos:**
* `Python 3` instalado no seu sistema.

**Como executar**

Siga o passo a passo para executar o projeto

1. **Clone o projeto na sua máquina com esse comando:**
```bash
git clone https://github.com/GrupoCodeNexus/Gestao-de-Itens-SmartFlow-sprint4-python.git
cd Gestao-de-Itens-SmartFlow-sprint4-python
```

2. **Instalação das bibliotecas necessárias e criando ambiente virtual para rodar o projeto**
```bash
python -m venv venv
source venv/bin/activate
pip install flask flask-socketio
```

4.  **Execute o comando para rodar o projeto:**
```bash
python app.py
```

4. **Rodando no servidor local**

Após seguir esses passos o terminal irá exibir a seguinte mensagem
 * Running on http://127.0.0.1:5000

Passe o mouse encima do link e use o comando (ctrl + click) ou clique em ``Follow link`` para acessar a aplicação.

## Pastas principais do projeto

| Pasta / Arquivo            | Função                                                                 |
|----------------------------|------------------------------------------------------------------------|
| app.py                     | Arquivo principal Flask que inicializa o sistema                       |
| blueprints/                | Contém todos os módulos (paciente / estoque / token / resumo)          |
| blueprints/paciente/       | Lógica de criação / seleção / entrada de pacientes                     |
| blueprints/estoque/        | Controle e gestão do estoque do carrinho                               |
| blueprints/token/          | Tela de seleção e consumo automatizado de medicamentos                 |
| blueprints/resumo/         | Tela final de confirmação e gravação de saída                          |
| dados/                     | Diretório raiz de persistência local                                   |
| dados/pacientes/           | Histórico, pendências e fichas individuais dos pacientes               |
| dados/estoque/             | JSON fixo contendo o estoque do carrinho                               |
| templates/                 | Arquivos HTML do sistema (Jinja)                                       |
| static/                    | Tailwind, CSS, imagens e JS estáticos                                  |


## Conheça nossa Equipe!
- [Francisco Vargas](https://github.com/Franciscov25)
- [Kayque Carvalho](https://github.com/Kay-Carv)
- [Matheus Eiki](https://github.com/Matheus-Eiki)
- [Marcelo Affonso](https://github.com/tenebres-cpu)

![Design sem nome (2)](https://github.com/user-attachments/assets/b9c18376-a90e-4d79-8b71-036ff3f51e45)
