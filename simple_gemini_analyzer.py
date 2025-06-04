# simple_gemini_analyzer.py
import os
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from datetime import datetime

# --- Configuration and Constants ---
load_dotenv() # Carrega variáveis do .env se presente no CWD
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash-latest"

# Prompt similar ao otimizado, mas autocontido no script para simplicidade
# e para não depender do pacote nutrisnap_ai.config
SIMPLE_PROMPT = """
**PROMPT PARA ANÁLISE NUTRICIONAL DE IMAGEM (MODELO GEMINI)**

**Instrução Principal:** Você é um assistente de IA especializado em análise nutricional visual. Analise a imagem de um prato de comida e retorne uma estimativa técnica e objetiva dos alimentos e suas calorias.

**Formato Obrigatório da Resposta (JSON):**
Sua resposta DEVE ser exclusivamente um objeto JSON. Não inclua nenhum texto fora do objeto JSON.
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

**Detalhes Solicitados:**
1.  **Identificação:** Nome específico. Se incerto, "Item Não Identificado - [Índice]" e explique em 'notes'.
2.  **Calorias por Item:** Em kcal (inteiro). Se não estimável, `null` e justifique em 'notes'.
3.  **Calorias Totais:** Soma das calorias estimáveis. Se nenhuma, `null`.
4.  **Confiança:** "Alto", "Médio" ou "Baixo" para cada item.
5.  **Notas:** Detalhes sobre incertezas/observações.
"""

# --- Helper Functions ---
def print_log_simple(level: str, message: str):
    """Helper function for printing formatted logs (standalone)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [{level.upper()}] {message}")

# --- Core Logic ---
def analyze_image_standalone(image_path_obj: Path, prompt_text: str) -> dict:
    print_log_simple("info", f"Iniciando análise standalone para: {image_path_obj}")

    if not GEMINI_API_KEY:
        print_log_simple("fatal", "GEMINI_API_KEY não encontrada nas variáveis de ambiente. Crie um arquivo .env ou defina a variável.")
        return {"status": "erro", "error": "API Key não configurada"}
    
    print_log_simple("info", "Chave da API Gemini carregada.")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e_conf:
        print_log_simple("fatal", f"Erro ao configurar a API Gemini: {e_conf}")
        return {"status": "erro", "error": "Falha na configuração da API Gemini", "details": str(e_conf)}

    try:
        print_log_simple("info", f"Carregando imagem de: {image_path_obj}...")
        if not image_path_obj.exists():
            print_log_simple("error", f"Arquivo de imagem não encontrado: {image_path_obj}")
            return {"status": "erro", "error": "Imagem não encontrada", "details": str(image_path_obj)}
        
        img = Image.open(image_path_obj)
        print_log_simple("success", f"Imagem '{image_path_obj.name}' carregada com sucesso.")
    except Exception as e_img:
        print_log_simple("error", f"Erro ao carregar imagem '{image_path_obj}': {e_img}")
        return {"status": "erro", "error": "Erro ao carregar imagem", "details": str(e_img)}

    try:
        print_log_simple("info", f"Configurando o modelo Gemini: {MODEL_NAME}...")
        model = genai.GenerativeModel(MODEL_NAME)
        print_log_simple("info", "Modelo configurado.")

        print_log_simple("info", "Enviando imagem e prompt para o modelo Gemini...")
        response = model.generate_content([prompt_text, img])
        print_log_simple("success", "Resposta recebida do modelo Gemini.")

        # Processamento da resposta
        response_text = ""
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason
            print_log_simple("error", f"Prompt bloqueado pela API Gemini. Razão: {reason}")
            return {"status": "erro", "error": "Prompt bloqueado", "details": str(reason), "safety_ratings": str(response.prompt_feedback.safety_ratings or "N/A")}
        
        try:
            response_text = response.text
        except ValueError as ve:
            print_log_simple("warn", f"response.text não pôde ser acessado diretamente ({ve}). Verificando 'candidates' e 'parts'...")
            try:
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    text_parts = [part.text for part in response.candidates[0].content.parts if hasattr(part, 'text')]
                    response_text = "".join(text_parts)
                else:
                    raise ValueError("Conteúdo de texto não encontrado na estrutura de resposta complexa.")
            except Exception as e_parts:
                print_log_simple("error", f"Não foi possível extrair texto das 'parts' da resposta da API: {e_parts}")
                return {"status": "erro", "error": "Falha ao extrair conteúdo da resposta", "details": str(e_parts), "raw_response_preview": str(response)[:500]}
        
        if not response_text.strip():
            print_log_simple("warn", "O texto da resposta do Gemini está vazio.")
            return {"status": "erro", "error": "Resposta de texto vazia", "details": "O modelo Gemini retornou um texto vazio."}

        print_log_simple("info", "Texto da resposta obtido. Tentando parsear como JSON...")
        print_log_simple("debug", f"Texto bruto da resposta (primeiros 500 chars):\n{response_text[:500]}{'...' if len(response_text)>500 else ''}")
        
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:].strip() # Remove ```json e \n
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3].strip() # Remove ``` do final
        elif cleaned_text.startswith("```") and cleaned_text.endswith("```"): # caso genérico de markdown code block
            cleaned_text = cleaned_text[3:-3].strip()


        try:
            parsed_json = json.loads(cleaned_text)
            print_log_simple("success", "JSON da resposta parseado com sucesso!")
            return {"status": "sucesso", "data": parsed_json}
        except json.JSONDecodeError as e_json:
            print_log_simple("error", f"Falha ao parsear a resposta JSON: {e_json}")
            print_log_simple("info", "Fallback: Retornando o texto bruto da resposta pois não é um JSON válido.")
            return {"status": "erro", "error": "Falha no parsing do JSON", "details": str(e_json), "raw_text_response": response_text}

    except genai.types.generation_types.BlockedPromptException as bpe:
        print_log_simple("error", f"Requisição bloqueada (BlockedPromptException): {bpe.prompt_feedback.block_reason}")
        return {"status": "erro", "error": "Prompt bloqueado pela API", "details": f"Razão: {bpe.prompt_feedback.block_reason}, Safety Ratings: {bpe.prompt_feedback.safety_ratings}"}
    except Exception as e_api:
        print_log_simple("error", f"Ocorreu um erro inesperado durante a comunicação com a API Gemini ou processamento: {e_api}")
        import traceback
        print_log_simple("debug", f"Traceback completo: {traceback.format_exc()}")
        return {"status": "erro", "error": "Erro na API Gemini ou processamento", "details": str(e_api)}

# --- Main Execution ---
if __name__ == "__main__":
    print_log_simple("system", "Analisador Simples de Imagem com Gemini (Standalone) iniciado.")

    parser = argparse.ArgumentParser(description="Analisa uma imagem de comida usando o Google Gemini (versão standalone).")
    parser.add_argument("image_path", type=str, help="Caminho para o arquivo de imagem a ser analisado.")
    parser.add_argument("--prompt", type=str, default=SIMPLE_PROMPT, help="Prompt personalizado para o modelo Gemini.")
    
    args = parser.parse_args()

    image_file_to_analyze = Path(args.image_path)
    custom_prompt_text = args.prompt

    print_log_simple("info", f"Caminho da imagem recebido: {image_file_to_analyze}")
    if custom_prompt_text != SIMPLE_PROMPT:
        print_log_simple("info", "Usando prompt personalizado.")
        print_log_simple("debug", f"Prompt Personalizado (preview):\n{custom_prompt_text[:200]}...")
    else:
        print_log_simple("info", "Usando prompt padrão.")


    # Chama a função principal de análise
    final_result = analyze_image_standalone(image_file_to_analyze, custom_prompt_text)

    print_log_simple("system", "--- Resultado Final da Análise (Standalone) ---")
    # Imprime o resultado de forma legível
    print(json.dumps(final_result, indent=2, ensure_ascii=False))
    
    print_log_simple("system", "Script standalone finalizado.")