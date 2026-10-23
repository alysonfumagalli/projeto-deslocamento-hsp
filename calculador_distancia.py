"""
Calculador de Distância e Tempo de Deslocamento
Utiliza o Google Routes API para calcular distância e tempo entre CEPs
para modalidades de carro e transporte público.
"""

import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def formatar_cep(cep: str) -> str:
    """Remove caracteres não numéricos do CEP e formata para busca."""
    cep_limpo = "".join(filter(str.isdigit, cep))
    return f"{cep_limpo}, Brasil"


def calcular_rota(
    origem: str,
    destino: str,
    modo_transporte: str,
    api_key: str
) -> Optional[dict]:
    """
    Calcula a rota entre origem e destino usando Google Routes API.
    
    Args:
        origem: CEP ou endereço de origem
        destino: CEP ou endereço de destino
        modo_transporte: "DRIVE" para carro ou "TRANSIT" para transporte público
        api_key: Chave da API do Google
    
    Returns:
        Dicionário com distância (metros), duração (segundos) e detalhes,
        ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs"
    }
    
    body = {
        "origin": {
            "address": formatar_cep(origem)
        },
        "destination": {
            "address": formatar_cep(destino)
        },
        "travelMode": modo_transporte,
        "languageCode": "pt-BR",
        "units": "METRIC"
    }
    
    # Para transporte público, adiciona configurações específicas
    if modo_transporte == "TRANSIT":
        body["transitPreferences"] = {
            "routingPreference": "LESS_WALKING"
        }
    
    try:
        response = requests.post(ROUTES_API_URL, headers=headers, json=body)
        response.raise_for_status()
        
        data = response.json()
        
        if "routes" not in data or len(data["routes"]) == 0:
            print(f"  ⚠ Nenhuma rota encontrada para {origem} -> {destino} ({modo_transporte})")
            return None
        
        rota = data["routes"][0]
        
        # Extrai duração (remove o 's' do final e converte para int)
        duracao_str = rota.get("duration", "0s")
        duracao_segundos = int(duracao_str.replace("s", ""))
        
        return {
            "distancia_metros": rota.get("distanceMeters", 0),
            "duracao_segundos": duracao_segundos,
            "duracao_formatada": formatar_duracao(duracao_segundos),
            "distancia_km": round(rota.get("distanceMeters", 0) / 1000, 2)
        }
        
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ Erro HTTP ao calcular rota: {e}")
        if response.text:
            print(f"    Detalhes: {response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erro de conexão: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Erro inesperado: {e}")
        return None


def formatar_duracao(segundos: int) -> str:
    """Converte segundos para formato legível (ex: 1h 30min)."""
    if segundos < 60:
        return f"{segundos}s"
    
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    
    if horas > 0:
        return f"{horas}h {minutos}min"
    return f"{minutos}min"


def carregar_ceps_origem(arquivo: str) -> list[str]:
    """
    Carrega lista de CEPs de um arquivo texto.
    Ignora linhas vazias e comentários (começando com #).
    """
    ceps = []
    
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#"):
                    ceps.append(linha)
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado.")
        return []
    
    return ceps


def processar_rotas(
    ceps_origem: list[str],
    cep_destino: str,
    api_key: str
) -> list[dict]:
    """
    Processa todas as rotas para os CEPs de origem.
    
    Args:
        ceps_origem: Lista de CEPs de origem
        cep_destino: CEP de destino
        api_key: Chave da API do Google
    
    Returns:
        Lista de dicionários com resultados para cada CEP
    """
    resultados = []
    total = len(ceps_origem)
    
    print(f"\n{'='*60}")
    print(f"Calculando rotas para {total} CEPs de origem")
    print(f"Destino: {cep_destino}")
    print(f"{'='*60}\n")
    
    for idx, cep_origem in enumerate(ceps_origem, 1):
        print(f"[{idx}/{total}] Processando CEP: {cep_origem}")
        
        resultado = {
            "cep_origem": cep_origem,
            "cep_destino": cep_destino,
            # Carro
            "carro_distancia_km": None,
            "carro_duracao_min": None,
            "carro_duracao_formatada": None,
            # Transporte Público
            "transporte_publico_distancia_km": None,
            "transporte_publico_duracao_min": None,
            "transporte_publico_duracao_formatada": None,
            # Status
            "status_carro": "Erro",
            "status_transporte": "Erro"
        }
        
        # Calcular rota de carro
        print("  → Calculando rota de carro...")
        rota_carro = calcular_rota(cep_origem, cep_destino, "DRIVE", api_key)
        
        if rota_carro:
            resultado["carro_distancia_km"] = rota_carro["distancia_km"]
            resultado["carro_duracao_min"] = round(rota_carro["duracao_segundos"] / 60, 1)
            resultado["carro_duracao_formatada"] = rota_carro["duracao_formatada"]
            resultado["status_carro"] = "OK"
            print(f"    ✓ Carro: {rota_carro['distancia_km']} km, {rota_carro['duracao_formatada']}")
        
        # Calcular rota de transporte público
        print("  → Calculando rota de transporte público...")
        rota_transporte = calcular_rota(cep_origem, cep_destino, "TRANSIT", api_key)
        
        if rota_transporte:
            resultado["transporte_publico_distancia_km"] = rota_transporte["distancia_km"]
            resultado["transporte_publico_duracao_min"] = round(rota_transporte["duracao_segundos"] / 60, 1)
            resultado["transporte_publico_duracao_formatada"] = rota_transporte["duracao_formatada"]
            resultado["status_transporte"] = "OK"
            print(f"    ✓ Transporte Público: {rota_transporte['distancia_km']} km, {rota_transporte['duracao_formatada']}")
        
        resultados.append(resultado)
        print()
    
    return resultados


def salvar_excel(resultados: list[dict], arquivo_saida: str) -> None:
    """Salva os resultados em um arquivo Excel formatado."""
    
    df = pd.DataFrame(resultados)
    
    # Renomeia colunas para nomes mais amigáveis
    colunas_renomeadas = {
        "cep_origem": "CEP Origem",
        "cep_destino": "CEP Destino",
        "carro_distancia_km": "Carro - Distância (km)",
        "carro_duracao_min": "Carro - Duração (min)",
        "carro_duracao_formatada": "Carro - Duração",
        "transporte_publico_distancia_km": "Transp. Público - Distância (km)",
        "transporte_publico_duracao_min": "Transp. Público - Duração (min)",
        "transporte_publico_duracao_formatada": "Transp. Público - Duração",
        "status_carro": "Status Carro",
        "status_transporte": "Status Transp. Público"
    }
    
    df = df.rename(columns=colunas_renomeadas)
    
    # Reordena colunas
    colunas_ordenadas = [
        "CEP Origem",
        "CEP Destino",
        "Carro - Distância (km)",
        "Carro - Duração (min)",
        "Carro - Duração",
        "Status Carro",
        "Transp. Público - Distância (km)",
        "Transp. Público - Duração (min)",
        "Transp. Público - Duração",
        "Status Transp. Público"
    ]
    
    df = df[colunas_ordenadas]
    
    # Salva com formatação
    with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Rotas")
        
        # Ajusta largura das colunas
        worksheet = writer.sheets["Rotas"]
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 30)
    
    print(f"\n✓ Resultados salvos em: {arquivo_saida}")


def main():
    """Função principal do programa."""
    
    print("\n" + "="*60)
    print("  CALCULADOR DE DISTÂNCIA E TEMPO DE DESLOCAMENTO")
    print("  Usando Google Routes API")
    print("="*60)
    
    # Verifica se a API key está configurada
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "sua_chave_api_aqui":
        print("\n✗ ERRO: Chave da API do Google não configurada!")
        print("  1. Copie o arquivo .env.example para .env")
        print("  2. Adicione sua chave da API no arquivo .env")
        print("  3. Execute o programa novamente")
        return
    
    # Configurações do usuário
    arquivo_ceps = "ceps_origem.txt"
    cep_destino = input("\nDigite o CEP de destino (ex: 05403-010): ").strip()
    
    if not cep_destino:
        print("✗ CEP de destino não informado. Encerrando.")
        return
    
    # Carrega CEPs de origem
    ceps_origem = carregar_ceps_origem(arquivo_ceps)
    
    if not ceps_origem:
        print(f"\n✗ Nenhum CEP encontrado no arquivo {arquivo_ceps}")
        print("  Adicione os CEPs de origem (um por linha) no arquivo.")
        return
    
    print(f"\n✓ {len(ceps_origem)} CEPs de origem carregados")
    
    # Processa as rotas
    resultados = processar_rotas(ceps_origem, cep_destino, GOOGLE_API_KEY)
    
    # Gera nome do arquivo de saída com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = f"resultado_rotas_{timestamp}.xlsx"
    
    # Salva resultados
    salvar_excel(resultados, arquivo_saida)
    
    # Resumo
    total = len(resultados)
    ok_carro = sum(1 for r in resultados if r["status_carro"] == "OK")
    ok_transporte = sum(1 for r in resultados if r["status_transporte"] == "OK")
    
    print("\n" + "="*60)
    print("  RESUMO")
    print("="*60)
    print(f"  Total de CEPs processados: {total}")
    print(f"  Rotas de carro calculadas: {ok_carro}/{total}")
    print(f"  Rotas de transporte público calculadas: {ok_transporte}/{total}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
