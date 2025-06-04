# nutrisnap_ai/config.py
import os
from dotenv import load_dotenv
from .utils import print_log # Importa print_log do mesmo pacote

# Encontra o diretório raiz do projeto para carregar o .env de forma consistente
# Presume que config.py está em nutrisnap_ai/ e .env está em nutrisnap_ai_project/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')

if os.path.exists(dotenv_path):
    print_log("info", f"Carregando arquivo .env de: {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print_log("warn", f"Arquivo .env não encontrado em: {dotenv_path}. Tentando load_dotenv() padrão (pode não funcionar se o CWD não for a raiz do projeto).")
    load_dotenv() # Tenta carregar .env do CWD ou diretórios pais

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print_log("error", "GEMINI_API_KEY não encontrada. Certifique-se de que está definida no seu arquivo .env.")
else:
    print_log("info", "GEMINI_API_KEY carregada com sucesso.")

# Modelo Gemini a ser usado
MODEL_NAME = "gemini-1.5-flash-latest" # Ou 'gemini-pro-vision', 'gemini-1.5-pro-latest'

# Prompt padrão otimizado
OPTIMIZED_PROMPT = """
**PROMPT PARA ANÁLISE NUTRICIONAL DE IMAGEM (MODELO GEMINI)**

**Instrução Principal:** Você é um assistente de IA especializado em análise nutricional visual. Sua tarefa é analisar a imagem de um prato de comida fornecida e retornar uma estimativa técnica e objetiva dos alimentos presentes e suas calorias.

**Objetivos Detalhados:**
1.  **Identificação dos Alimentos:** Liste cada item alimentar distinto visível na imagem. Utilize nomes específicos e técnicos (ex: "Salmão assado com crosta de gergelim", "Brócolis cozido no vapor", "Arroz integral"). Se um item não puder ser identificado com segurança, rotule-o como "Item Não Identificado - [Índice]" (ex: "Item Não Identificado - 1") e explique o motivo na seção de notas do item (ex: "Obscurecido por outro alimento", "Aparência visual inconclusiva").
2.  **Estimativa Calórica por Item:** Para cada item alimentar IDENTIFICADO, forneça uma estimativa de suas calorias em kcal (quilocalorias). Apresente este valor como um número inteiro. Se um item for identificado, mas a estimativa calórica não puder ser feita com segurança (ex: método de preparo incerto, porção não clara apesar da identificação), atribua `null` ao campo `estimated_calories` e justifique na seção de notas do item.
3.  **Estimativa Calórica Total:** Forneça a soma total estimada de calorias para todos os itens cujas calorias puderam ser estimadas. Se nenhum item tiver calorias estimáveis, o total deve ser `null` ou 0 com uma nota explicativa no sumário.
4.  **Nível de Confiança e Observações:** Para cada item (identificado ou não), indique seu nível de confiança na análise (identificação e estimativa calórica) usando os termos: "Alto", "Médio" ou "Baixo". Utilize o campo "notes" para detalhar as razões para qualquer incerteza (na identificação ou na estimativa calórica), ou para adicionar observações relevantes sobre o item (ex: "Porção aparentemente pequena", "Possível presença de óleo não visível").

**Formato Obrigatório da Resposta (JSON):**
Sua resposta DEVE ser exclusivamente um objeto JSON. Não inclua nenhum texto introdutório, comentários ou qualquer formatação fora da estrutura JSON especificada abaixo.
{
  "total_calories": null,
  "identified_items": [
    {
      "item_name": "string",
      "estimated_calories": null,
      "confidence": "Alto|Médio|Baixo",
      "notes": "string"
    }
  ],
  "analysis_summary_notes": "string"
}

**Diretrizes Adicionais para Consistência:** Analise apenas os alimentos contidos no prato principal ou porção sendo apresentada. Ignore o ambiente ao redor. Baseie as estimativas calóricas em porções visualmente aparentes. Mantenha um tom técnico, direto e objetivo em todas as descrições e notas.
"""