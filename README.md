# NutriSnap AI 🥗

NutriSnap AI é um projeto que utiliza o modelo multimodal Gemini do Google para analisar imagens de pratos de comida, identificar os alimentos e estimar o total de calorias, bem como as calorias por alimento. Este repositório contém um Mínimo Produto Viável (MVP) e uma estrutura para futuras expansões.

## Funcionalidades (MVP)

* Análise de imagens de pratos de comida via linha de comando.
* Identificação de itens alimentares visíveis na imagem.
* Estimativa de calorias por item e para a refeição total.
* Saída dos resultados da análise em formato JSON.
* Uso de variáveis de ambiente para gerenciamento seguro da chave da API Gemini.
* Estrutura de projeto modular e organizada.
* Logs simples via `print()` para depuração.
* Tratamento básico de exceções e fallbacks.

## Estrutura do Projeto

nutrisnap_ai_project/
├── .env.example              # Exemplo para variáveis de ambiente
├── .gitignore                # Arquivos e pastas a serem ignorados pelo Git
├── data/
│   ├── input_images/         # Para suas imagens de entrada
│   │   ├── example_meal.jpg  # Adicione sua imagem de exemplo aqui
│   │   └── .gitkeep
│   └── results/              # Para salvar os JSONs de resultado
│       └── .gitkeep
├── nutrisnap_ai/             # Pacote principal da aplicação Python
│   ├── init.py
│   ├── analysis.py           # Lógica de análise de imagem com Gemini
│   ├── config.py             # Configurações (API Key, prompt)
│   └── utils.py              # Funções utilitárias (logs, manipulação de arquivos)
├── requirements.txt          # Dependências do projeto
├── README.md                 # Este arquivo
├── scripts/
│   └── run_analysis.py       # Script principal para executar a análise
├── simple_gemini_analyzer.py # Script simples para testes diretos com a API

## Configuração do Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone <url_do_seu_repositorio_github>
    cd nutrisnap_ai_project
    ```

2.  **Crie e ative um ambiente virtual Python:**
    ```bash
    python -m venv venv
    # No Linux/macOS:
    source venv/bin/activate
    # No Windows (Prompt de Comando):
    # venv\Scripts\activate
    # No Windows (PowerShell):
    # venv\Scripts\Activate.ps1
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a Chave da API Gemini:**
    * Renomeie o arquivo `.env.example` para `.env`.
    * Abra o arquivo `.env` e substitua `"SUA_CHAVE_DE_API_AQUI"` pela sua chave real da API Gemini.

5.  **Adicione uma Imagem de Exemplo:**
    * Coloque uma imagem de um prato de comida no diretório `data/input_images/` e nomeie-a como `example_meal.jpg` (ou use outro nome e ajuste o comando de execução).

## Como Usar

### Script Principal (`run_analysis.py`)

Este é o script recomendado para análises usando a estrutura do projeto. Execute a partir do diretório raiz (`nutrisnap_ai_project/`):

```bash
python scripts/run_analysis.py --image_path data/input_images/example_meal.jpg

Opções:

--output_dir CAMINHO_CUSTOMIZADO: Especifica um diretório diferente para salvar os resultados JSON. O padrão é data/results/.
--mock: Executa em modo de simulação (mock) sem fazer chamadas reais à API Gemini, usando dados de exemplo definidos no código. Útil para testes rápidos do fluxo da aplicação.
Os resultados da análise (um arquivo JSON) serão salvos no diretório especificado (padrão: data/results/), com um nome baseado no arquivo de imagem de entrada (ex: example_meal_analysis.json).

Script Simples de Teste (simple_gemini_analyzer.py)
Este script é para testes mais diretos e isolados com a API Gemini. Execute a partir do diretório raiz:

python simple_gemini_analyzer.py data/input_images/example_meal.jpg

Ele imprimirá o resultado JSON diretamente no console.

Prompt Utilizado para o Gemini
O sistema utiliza um prompt otimizado (definido em nutrisnap_ai/config.py) para instruir o modelo Gemini. O objetivo é obter uma identificação clara dos alimentos, estimativas calóricas, e uma indicação da confiança do modelo, tudo em formato JSON.

Resumo do Prompt:

Pede para identificar itens alimentares e estimar calorias (por item e total).
Solicita que o modelo indique seu nível de confiança ("Alto", "Médio", "Baixo") e forneça notas sobre incertezas.

Exige que a resposta seja exclusivamente um objeto JSON com uma estrutura definida:
{
  "total_calories": null, // ou integer
  "identified_items": [
    {
      "item_name": "string",
      "estimated_calories": null, // ou integer
      "confidence": "Alto|Médio|Baixo",
      "notes": "string"
    }
  ],
  "analysis_summary_notes": "string"
}

Tratamento de Erros e Fallbacks
Chave de API Ausente: O script avisará e não prosseguirá se a chave não for encontrada (a menos que em modo mock).
Imagem Inválida/Não Encontrada: Mensagens de erro serão exibidas.
Falhas na API Gemini: Erros de comunicação, prompts bloqueados, etc., são capturados e registrados.
Parsing da Resposta: Se a resposta do Gemini não for um JSON válido (apesar do prompt), o sistema tentará limpar a resposta ou registrará o erro e poderá retornar o texto bruto para depuração.
Próximos Passos e Melhorias Futuras
Este MVP é a base. Sugestões para evolução incluem:

Acurácia do Modelo: Refinamento contínuo de prompts, coleta de feedback, exploração de fine-tuning.
Estrutura de Código: Aplicação de mais princípios SOLID, design patterns, e возможно uma arquitetura hexagonal.
Interface do Usuário: Desenvolvimento de uma API Web (FastAPI/Flask) e um frontend (React/Vue) ou app mobile.
Testes Automáticos: Implementação de testes unitários, de integração e E2E robustos.
Padronização de Logs: Uso de logging estruturado e centralizado.
Integração com Banco de Dados: Para persistir análises, dados de usuários, feedback.
Integração com APIs Externas: Bancos de dados nutricionais (USDA, TACO) para enriquecer dados.








