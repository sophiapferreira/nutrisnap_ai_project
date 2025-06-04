# nutrisnap_ai/analysis.py
import google.generativeai as genai
from PIL import Image
import json

from . import config
from . import utils # Para usar utils.print_log

# Modo MOCK pode ser alterado por scripts externos (ex: run_analysis.py --mock)
MOCK_MODE = False

def _mock_gemini_vision_call(image_path_str: str) -> str:
    """Retorna uma resposta mockada, como uma string JSON, similar à da API Gemini."""
    utils.print_log("info", f"**** MODO MOCK ATIVADO PARA CHAMADA GEMINI (imagem: {image_path_str}) ****")
    import time
    time.sleep(0.2) # Simula pequena latência
    
    mock_data = {
      "total_calories": 780,
      "identified_items": [
        {"item_name": "Peito de Frango Grelhado (Mock)", "estimated_calories": 320, "confidence": "Alto", "notes": "Porção de aproximadamente 150g."},
        {"item_name": "Batata Doce Assada (Mock)", "estimated_calories": 220, "confidence": "Alto", "notes": "Cerca de 200g, parece ter um pouco de azeite."},
        {"item_name": "Brócolis no Vapor (Mock)", "estimated_calories": 90, "confidence": "Médio", "notes": "Porção generosa, mas difícil estimar o volume exato."},
        {"item_name": "Item Não Identificado - 1 (Mock)", "estimated_calories": None, "confidence": "Baixo", "notes": "Pequeno item escuro no canto, aparência inconclusiva."}
      ],
      "analysis_summary_notes": "Análise mock executada. A qualidade da imagem de teste é considerada boa. Um item não pôde ser identificado."
    }
    return json.dumps(mock_data)

def _parse_gemini_response(response_text: str) -> dict | None:
    """Analisa a resposta em texto do Gemini para extrair o JSON."""
    utils.print_log("info", "Tentando parsear a resposta do modelo como JSON...")
    utils.print_log("debug", f"Texto bruto recebido para parsing (primeiros 500 chars):\n{response_text[:500]}{'...' if len(response_text)>500 else ''}")

    cleaned_text = response_text.strip()
    # Remove ```json ... ``` se presente
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:] # Remove ```json e o \n seguinte
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3] # Remove ``` do final
        cleaned_text = cleaned_text.strip()
        utils.print_log("debug", "Bloco ```json detectado e removido da resposta.")
    elif cleaned_text.startswith("```") and cleaned_text.endswith("```"): # Caso mais genérico de ```...```
        cleaned_text = cleaned_text[3:-3].strip()
        utils.print_log("debug", "Bloco ``` detectado e removido da resposta.")


    if not cleaned_text:
        utils.print_log("warn", "Após tentativa de limpeza, o texto da resposta está vazio.")
        raise ValueError("Resposta do LLM vazia após tentativa de limpeza do encapsulamento JSON.")

    try:
        parsed_data = json.loads(cleaned_text)
        # Validação básica da estrutura esperada (pode ser mais robusta)
        if not isinstance(parsed_data, dict) or \
           "identified_items" not in parsed_data or \
           "total_calories" not in parsed_data or \
           "analysis_summary_notes" not in parsed_data: # Checa se é dict e tem chaves esperadas
            utils.print_log("warn", "JSON parseado, mas faltam chaves principais ou não é um dicionário. Verifique o prompt e a resposta do modelo.")
            # Considerar levantar um erro aqui se a estrutura for estritamente necessária
            # raise ValueError("JSON parseado não contém a estrutura esperada (identified_items, total_calories, analysis_summary_notes).")
        
        if "identified_items" in parsed_data and isinstance(parsed_data["identified_items"], list):
            for item in parsed_data["identified_items"]:
                if not isinstance(item, dict) or \
                   not all(key in item for key in ["item_name", "estimated_calories", "confidence", "notes"]):
                    utils.print_log("warn", f"Item na lista 'identified_items' não possui a estrutura esperada: {item}")
                    # raise ValueError(f"Item em 'identified_items' não contém a estrutura esperada: {item}")
                    break # Para o loop na primeira inconsistência de item

        utils.print_log("success", "Resposta do LLM parseada como JSON com sucesso.")
        return parsed_data
    except json.JSONDecodeError as e:
        utils.print_log("error", f"Falha ao decodificar JSON da resposta do LLM: {e}")
        utils.print_log("debug", f"Texto que causou o erro de parsing (primeiros 500 chars): {cleaned_text[:500]}{'...' if len(cleaned_text)>500 else ''}")
        raise ValueError(f"A resposta do LLM não era um JSON válido. Erro: {e}") # Re-levanta para ser pego pelo chamador
    except Exception as e:
        utils.print_log("error", f"Erro inesperado durante o parsing do JSON: {e}")
        raise ValueError(f"Erro inesperado no parsing: {e}") # Re-levanta


def analyze_image(image_path_str: str) -> dict:
    """Analisa a imagem dada usando a API Gemini Vision."""
    utils.print_log("info", f"Iniciando análise para a imagem: {image_path_str}")

    # Checagem da API Key (a menos que em MOCK_MODE)
    if not MOCK_MODE and not config.GEMINI_API_KEY:
        utils.print_log("error", "Chave da API Gemini (GEMINI_API_KEY) não configurada.")
        return {"status": "erro", "error": "API key não configurada", "details": "GEMINI_API_KEY não foi encontrada."}

    pil_image = utils.load_image(image_path_str)
    if not pil_image:
        return {"status": "erro", "error": "Falha ao carregar imagem", "details": f"Não foi possível carregar: {image_path_str}"}

    if MOCK_MODE:
        utils.print_log("info", "Executando em MODO MOCK.")
        try:
            mock_response_text = _mock_gemini_vision_call(image_path_str)
            parsed_data = _parse_gemini_response(mock_response_text)
            return {"status": "sucesso (mock)", "data": parsed_data}
        except Exception as e_mock_parse:
            utils.print_log("error", f"Erro ao parsear resposta mock: {e_mock_parse}")
            return {"status": "erro (mock)", "error": "Falha no parsing da resposta mock", "details": str(e_mock_parse)}

    try:
        utils.print_log("info", "Configurando cliente Gemini API...")
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.MODEL_NAME)
        utils.print_log("info", f"Modelo Gemini ({config.MODEL_NAME}) configurado.")

        prompt_to_use = config.OPTIMIZED_PROMPT # Usa o prompt do config.py

        utils.print_log("info", "Enviando requisição para a API Gemini...")
        response = model.generate_content([prompt_to_use, pil_image])
        utils.print_log("success", "Resposta recebida da API Gemini.")

        # Processamento da resposta
        response_text = ""
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason
            utils.print_log("error", f"Prompt bloqueado pela API Gemini. Razão: {reason}")
            return {"status": "erro", "error": "Prompt bloqueado", "details": str(reason), "safety_ratings": str(response.prompt_feedback.safety_ratings or "N/A")}
        
        try:
            response_text = response.text # Tentativa de acesso direto ao texto
        except ValueError as ve: # Pode ocorrer se a resposta não for texto simples
            utils.print_log("warn", f"response.text não pôde ser acessado diretamente ({ve}). Verificando 'candidates' e 'parts'...")
            try:
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    # Concatena o texto de todas as partes textuais
                    text_parts = [part.text for part in response.candidates[0].content.parts if hasattr(part, 'text')]
                    response_text = "".join(text_parts)
                else: # Se não houver candidatos ou partes como esperado
                    utils.print_log("error", "Resposta da API não contém 'candidates' ou 'parts' textuais esperadas.")
                    raise ValueError("Conteúdo de texto não encontrado na estrutura de resposta complexa.")
            except Exception as e_parts: # Captura qualquer erro ao tentar acessar as partes
                utils.print_log("error", f"Não foi possível extrair texto das 'parts' da resposta da API: {e_parts}")
                return {"status": "erro", "error": "Falha ao extrair conteúdo da resposta", "details": str(e_parts), "raw_response_preview": str(response)[:500]}
        
        if not response_text.strip(): # Checa se o texto extraído está vazio ou só com espaços
            utils.print_log("warn", "O texto da resposta do Gemini está vazio.")
            return {"status": "erro", "error": "Resposta de texto vazia", "details": "O modelo Gemini retornou um texto vazio."}

        # Parsing da resposta
        parsed_data = _parse_gemini_response(response_text)
        return {"status": "sucesso", "data": parsed_data}

    except genai.types.generation_types.BlockedPromptException as bpe:
        utils.print_log("error", f"Requisição bloqueada (BlockedPromptException): {bpe.prompt_feedback.block_reason}")
        return {"status": "erro", "error": "Prompt bloqueado pela API", "details": f"Razão: {bpe.prompt_feedback.block_reason}, Safety Ratings: {bpe.prompt_feedback.safety_ratings}"}
    except Exception as e:
        utils.print_log("error", f"Erro geral na API Gemini ou processamento: {e}")
        import traceback
        utils.print_log("debug", f"Traceback completo: {traceback.format_exc()}")
        return {"status": "erro", "error": "Erro na comunicação ou processamento da API", "details": str(e)}