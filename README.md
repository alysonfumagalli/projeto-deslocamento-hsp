# Calculador de Distância e Tempo de Deslocamento

Programa em Python que calcula a distância e o tempo de deslocamento entre CEPs de origem e um CEP de destino, utilizando o **Google Routes API** para duas modalidades de transporte:

- 🚗 **Carro**
- 🚌 **Transporte Público**

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Conta no Google Cloud com a **Routes API** habilitada
- Chave de API do Google Maps

## 🔧 Configuração da API do Google

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Routes API** em "APIs e Serviços" > "Biblioteca"
4. Crie uma credencial de API em "APIs e Serviços" > "Credenciais"
5. Copie a chave gerada

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd projeto-deslocamento-hsp
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure a chave da API:
```bash
cp .env.example .env
```
Edite o arquivo `.env` e adicione sua chave:
```
GOOGLE_MAPS_API_KEY=sua_chave_api_aqui
```

## 📝 Uso

1. **Adicione os CEPs de origem** no arquivo `ceps_origem.txt` (um por linha):
```
01310-100
04543-011
05407-002
```

2. **Execute o programa**:
```bash
python calculador_distancia.py
```

3. **Informe o CEP de destino** quando solicitado.

4. O programa irá processar cada CEP e gerar um arquivo Excel com os resultados.

## 📊 Arquivo de Saída

O programa gera um arquivo Excel (`resultado_rotas_YYYYMMDD_HHMMSS.xlsx`) contendo:

| Coluna | Descrição |
|--------|-----------|
| CEP Origem | CEP de origem da rota |
| CEP Destino | CEP de destino |
| Carro - Distância (km) | Distância em quilômetros de carro |
| Carro - Duração (min) | Tempo em minutos de carro |
| Carro - Duração | Tempo formatado (ex: 1h 30min) |
| Status Carro | OK ou Erro |
| Transp. Público - Distância (km) | Distância em km de transporte público |
| Transp. Público - Duração (min) | Tempo em minutos |
| Transp. Público - Duração | Tempo formatado |
| Status Transp. Público | OK ou Erro |

## 📁 Estrutura do Projeto

```
projeto-deslocamento-hsp/
├── calculador_distancia.py  # Código principal
├── ceps_origem.txt          # Lista de CEPs de origem
├── requirements.txt         # Dependências Python
├── .env.example             # Exemplo de configuração
├── .env                     # Configuração (criar a partir do .example)
└── README.md                # Este arquivo
```

## ⚠️ Observações

- A API do Google Routes tem custos associados. Consulte a [tabela de preços](https://developers.google.com/maps/documentation/routes/usage-and-billing).
- Rotas de transporte público podem não estar disponíveis em todas as regiões.
- Os CEPs devem ser válidos e do Brasil.

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.