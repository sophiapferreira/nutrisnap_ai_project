# nutrisnap_ai1/utils.py
import json
import os
from datetime import datetime
from PIL import Image

def print_log(level: str, message: str):
    """
    Imprime uma mensagem de log formatada.
    Níveis comuns: DEBUG, INFO, WARN, ERROR, FATAL, SYSTEM, SUCCESS.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [{level.upper()}] {message}")

def save_json_result(data: dict, output_dir_str: str, filename_prefix: str) -> str | None:
    """Salva dados em um arquivo JSON no diretório especificado."""
    try:
        output_dir = os.path.abspath(output_dir_str)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print_log("info", f"Diretório de resultados criado: {output_dir}")

        output_filename = f"{filename_prefix}_analysis.json"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print_log("success", f"Resultados salvos em: {output_path}")
        return output_path
    except IOError as e:
        print_log("error", f"Falha IO ao salvar resultados em {output_path if 'output_path' in locals() else 'diretório de saída'}: {e}")
        return None
    except Exception as e:
        print_log("error", f"Erro inesperado ao salvar resultados JSON: {e}")
        return None

def load_image(image_path_str: str) -> Image.Image | None:
    """Carrega uma imagem usando Pillow, retorna um objeto Image ou None em caso de erro."""
    try:
        image_path = os.path.abspath(image_path_str)
        if not os.path.exists(image_path):
            print_log("error", f"Arquivo de imagem não encontrado: {image_path}")
            return None
        
        img = Image.open(image_path)
        # Poderia adicionar validação de formato/tamanho aqui se necessário
        print_log("info", f"Imagem '{os.path.basename(image_path)}' carregada com sucesso de {image_path}")
        return img
    except FileNotFoundError: # Deve ser pego pelo os.path.exists, mas como redundância
        print_log("error", f"Arquivo de imagem não encontrado (FileNotFoundError): {image_path_str}")
        return None
    except IOError as e: # Captura erros como "cannot identify image file"
        print_log("error", f"Não foi possível abrir ou ler o arquivo de imagem '{image_path_str}' (pode estar corrompido ou formato não suportado). Erro: {e}")
        return None
    except Exception as e:
        print_log("error", f"Erro inesperado ao carregar imagem {image_path_str}: {e}")
        return None

def get_filename_without_extension(filepath: str) -> str:
    """Extrai o nome do arquivo sem a extensão a partir de um caminho."""
    return os.path.splitext(os.path.basename(filepath))[0]