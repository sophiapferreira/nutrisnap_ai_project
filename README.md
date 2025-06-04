# 🍽️ NutriSnap AI - Análise Calórica Inteligente de Pratos

Este projeto foi desenvolvido como parte do desafio técnico da **Gs Company**. O objetivo é criar um script Python capaz de receber imagens de pratos de comida, interagir com um modelo de linguagem multimodal (LLM) e retornar uma análise dos alimentos e uma estimativa calórica para o prato.

---

## 🧠 Visão Geral

O NutriSnap AI permite:
- Enviar uma ou mais imagens de alimentos.
- Processar as imagens com o modelo **Gemini Pro Vision** (via Google AI Studio).
- Retornar a descrição dos alimentos e estimativa de calorias do prato como um todo ou por componentes.
- Exibir o resultado final ao usuário em formato simples e direto.

---

## ⚙️ Configuração e Execução

### 1. Clone o repositório

git clone https://github.com/sophiapferreira/nutrisnap_ai_project.git
cd nutrisnap_ai_project

2. Crie e ative um ambiente virtual (opcional, mas recomendado)

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Instale as dependências

pip install -r requirements.txt

4. Configure sua chave de API do Gemini

Crie um arquivo .env com o seguinte conteúdo:

GEMINI_API_KEY="sua-chave-do-gemini"

Use o arquivo .env.example como referência.

5. Execute o script

python scripts/simple_gemini_analyzer.py

🧩 Escolhas de Design e Arquitetura

🔷 Modelo Utilizado

Gemini Pro Vision (Google AI Studio): escolhido por sua capacidade de interpretar imagens e responder com linguagem natural de forma rápida e precisa.

🏗️ Prompt Engineering

Foram feitos ajustes iterativos no prompt para guiar o modelo a:

- Descrever com clareza os itens alimentares detectados.
- Estimar calorias com base em porções realistas.
- Ignorar elementos irrelevantes da imagem (fundo, utensílios).

📚 Bibliotecas Utilizadas

requests: para chamadas HTTP à API.
dotenv: para gerenciar a chave da API de forma segura.
Pillow: para abrir e tratar imagens.
json, os, time: utilitários para controle de arquivos e fluxo.

🖼️ Entrada e Saída

Entrada: imagens .jpg ou .png de pratos completos ou refeições.

Saída: texto contendo descrição dos alimentos e estimativa calórica por componente ou total.

📌 Escopo do Projeto

✅ O que o script faz

- Recebe imagens de pratos.
- Envia a imagem para o LLM da Gemini.
- Exibe uma resposta com análise e calorias.

❌ O que o script não faz (ainda)

- Classificação por tipo de refeição.
- Exportação de relatórios.
- Interface gráfica ou web.
- Validação rigorosa da entrada.

🧗‍♀️ Desafios Encontrados

- Restrições de acesso à API: soluções usando variáveis de ambiente para segurança.
- Qualidade das respostas do LLM: foi necessário afinar os prompts e testar diferentes descrições.
- Imagens com baixa qualidade: afetaram a precisão das respostas, exigindo novas tentativas.

🚧 Limitações Conhecidas

- A estimativa calórica ainda depende muito da qualidade da imagem e do "contexto visual".
- Respostas às vezes são vagas, principalmente em pratos muito misturados.
- O modelo pode errar alimentos visualmente semelhantes.

🚀 Melhorias Futuras

- Treinar um classificador auxiliar com modelo de visão próprio (ex: YOLO, Detectron).
- Interface web com upload direto de imagens.
- Armazenamento de histórico de análises.
- Exportação para PDF/CSV.
- Avaliação cruzada com base de dados nutricional confiável (ex: TACO, USDA).







