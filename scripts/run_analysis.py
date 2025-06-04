# scripts/run_analysis.py
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path # Usar pathlib para manipulação de caminhos

# Adiciona o diretório raiz do projeto (nutrisnap_ai_project) ao sys.path
# Isso permite que 'from nutrisnap_ai ...' funcione quando o script é chamado de qualquer lugar,
# contanto que a estrutura de pastas seja mantida.
PROJECT_ROOT = Path(__file__).resolve().parent.parent # Vai para 'scripts/' e depois para 'nutrisnap_ai_project/'
sys.path.insert(0, str(PROJECT_ROOT))

from nutrisnap_ai import analysis, utils, config # Agora as importações devem funcionar

# Define diretórios padrão de dados relativos à raiz do projeto
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "input_images"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "data" / "results"

def main():
    utils.print_log("system", "------------------------------------")
    utils.print_log("system", "🥗 NutriSnap AI - Análise de Imagem 🥗")
    utils.print_log("system", "------------------------------------")
    utils.print_log("info", f"Timestamp da execução: {datetime.now().isoformat()}")
    utils.print_log("info", f"Diretório raiz do projeto inferido: {PROJECT_ROOT}")

    parser = argparse.ArgumentParser(description="NutriSnap AI: Analisa imagens de alimentos para estimativa de calorias.")
    parser.add_argument("--image_path", type=str, required=True,
                        help="Caminho para o arquivo de imagem de entrada (relativo ou absoluto).")
    parser.add_argument("--output_dir", type=str, default=str(DEFAULT_RESULTS_DIR),
                        help=f"Diretório para salvar os resultados da análise (padrão: {DEFAULT_RESULTS_DIR}).")
    parser.add_argument("--mock", action="store_true",
                        help="Executa em modo MOCK sem chamadas reais à API (para teste).")

    args = parser.parse_args()

    if args.mock:
        analysis.MOCK_MODE = True # Ativa o modo mock no módulo de análise
        utils.print_log("info", "**** MODO MOCK ATIVADO VIA LINHA DE COMANDO ****")

    # Checagem da API Key é feita dentro de analysis.analyze_image se não estiver em MOCK_MODE

    # Resolve o caminho da imagem de entrada de forma mais robusta
    input_image_path_arg = Path(args.image_path)
    
    # 1. Se o caminho fornecido é absoluto e existe
    if input_image_path_arg.is_absolute():
        if not input_image_path_arg.exists():
            utils.print_log("fatal", f"Imagem não encontrada no caminho absoluto fornecido: {input_image_path_arg}")
            sys.exit(1)
        final_image_path = input_image_path_arg
    else:
        # 2. Tenta relativo ao diretório de execução atual (CWD)
        path_from_cwd = Path.cwd() / input_image_path_arg
        if path_from_cwd.exists():
            final_image_path = path_from_cwd
        else:
            # 3. Tenta relativo ao diretório de input padrão do projeto
            path_from_default_dir = DEFAULT_INPUT_DIR / input_image_path_arg.name # Usa .name para pegar só o nome do arquivo
            if path_from_default_dir.exists():
                final_image_path = path_from_default_dir
            else:
                utils.print_log("fatal", f"Imagem '{args.image_path}' não encontrada no CWD, nem em '{DEFAULT_INPUT_DIR}'. Verifique o caminho.")
                sys.exit(1)
    
    utils.print_log("info", f"Caminho final da imagem para análise: {final_image_path}")
    utils.print_log("info", f"Diretório de saída para resultados: {args.output_dir}")

    # Executa a análise
    analysis_result_wrapper = analysis.analyze_image(str(final_image_path))

    # Prepara a estrutura final do JSON de saída
    # Garante que sempre haverá uma estrutura base, mesmo em caso de erro total
    output_data = {
        "image_file": final_image_path.name,
        "analysis_timestamp": datetime.now().isoformat(),
        "status": analysis_result_wrapper.get("status", "erro_desconhecido"),
        # Inicializa campos opcionais que podem ou não vir do wrapper
        "data": None,
        "error_message": None,
        "details": None
    }
    # Atualiza com os dados do wrapper, se existirem
    if "data" in analysis_result_wrapper:
        output_data["data"] = analysis_result_wrapper["data"]
    if "error" in analysis_result_wrapper: # Nome da chave de erro no wrapper
        output_data["error_message"] = analysis_result_wrapper["error"]
    if "details" in analysis_result_wrapper:
        output_data["details"] = analysis_result_wrapper["details"]
    
    # Remove chaves None para um JSON mais limpo
    output_data_cleaned = {k: v for k, v in output_data.items() if v is not None}


    # Log dos resultados principais
    if output_data_cleaned["status"].startswith("sucesso"):
        utils.print_log("success", "Análise concluída com sucesso.")
        res_data = output_data_cleaned.get("data")
        if res_data:
            total_cals = res_data.get("total_calories")
            if total_cals is not None:
                utils.print_log("info", f"🍽️  Total Estimado de Calorias: {total_cals}")
            
            items = res_data.get("identified_items", [])
            if items:
                utils.print_log("info", "🍏 Itens Identificados:")
                for item in items:
                    utils.print_log("info", f"  - {item.get('item_name', 'Item Desconhecido')}: "
                                            f"{item.get('estimated_calories', 'N/A')} kcal "
                                            f"(Confiança: {item.get('confidence', 'N/A')}) "
                                            f"Notas: {item.get('notes', 'Nenhuma')}")
            summary_notes = res_data.get("analysis_summary_notes")
            if summary_notes:
                 utils.print_log("info", f"📋 Notas Sumárias da Análise: {summary_notes}")

    else:
        utils.print_log("error", f"Análise falhou. Status: {output_data_cleaned['status']}.")
        if output_data_cleaned.get("error_message"):
            utils.print_log("error", f"   Mensagem de Erro: {output_data_cleaned['error_message']}")
        if output_data_cleaned.get("details"):
            utils.print_log("error", f"   Detalhes do Erro: {output_data_cleaned['details']}")

    # Salva os resultados
    image_filename_prefix = utils.get_filename_without_extension(str(final_image_path))
    output_dir_path = Path(args.output_dir) # Garante que é um objeto Path
    
    saved_path = utils.save_json_result(output_data_cleaned, str(output_dir_path), image_filename_prefix)

    if saved_path:
        utils.print_log("info", f"Relatório completo da análise salvo em: {saved_path}")
    else:
        utils.print_log("warn", f"Falha ao salvar o JSON do relatório da análise no diretório: {output_dir_path}")

    utils.print_log("system", "------------------------------------")
    utils.print_log("system", "✨ Análise Finalizada ✨")
    utils.print_log("system", "------------------------------------")

if __name__ == "__main__":
    main()