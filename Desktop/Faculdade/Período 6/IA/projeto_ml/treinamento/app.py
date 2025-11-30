import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)


# O modelo treinado
MODEL_FILE = 'swimming_winner_model.pkl'

# CARREGAR O MODELO
try:
    model = joblib.load(MODEL_FILE)
except FileNotFoundError:
    print(f"ERRO: Arquivo do modelo {MODEL_FILE} não encontrado.")
    model = None

# LISTA CORRIGIDA DE FEATURES ESPERADAS PELO MODELO (Versão Final)
# ⚠️ CORREÇÃO: Usando 'Stroke_Medley' conforme solicitado pelo erro atual.
MODEL_FEATURES = ['Year', 'Distance_m', 'Relay?', 'Stroke_Backstroke', 'Stroke_Breaststroke', 'Stroke_Butterfly', 'Stroke_Freestyle', 'Stroke_Individual medley', 'Stroke_Medley', 'Gender_Men', 'Gender_Women']
# --------------------------------------------------------------------------
# FUNÇÕES DE PRÉ-PROCESSAMENTO
# --------------------------------------------------------------------------

def calculate_distance(dist_str):
    """
    Função de conversão de distância.
    """
    dist_str = str(dist_str).lower().replace('m', '')
    if 'x' in dist_str:
        try:
            parts = dist_str.split('x')
            return float(parts[0]) * float(parts[1])
        except ValueError:
            return 100.0
    else:
        try:
            return float(dist_str)
        except ValueError:
            return 100.0

def preprocess_input(input_data):
    """
    Prepara os dados de entrada (JSON) no formato exato (OHE) que o modelo espera.
    """
    # 1. Inicializa um DataFrame com TODAS as colunas esperadas com valor 0
    data = {feature: [0] for feature in MODEL_FEATURES}
    input_df = pd.DataFrame(data)

    # 2. Preencher valores numéricos e lógicos
    input_df['Year'] = input_data.get('Year', 2024)

    distance_str = input_data.get('Distance (in meters)', '100m')
    input_df['Distance_m'] = calculate_distance(distance_str)
    
    input_df['Relay?'] = 1 if 'x' in distance_str.lower() else 0

    # 3. Handle Stroke (One-Hot Encoding)
    stroke = input_data.get('Stroke', 'Freestyle').strip().lower()
    
    # ⚠️ CORREÇÃO: Mapeia tanto 'medley' quanto 'individual medley' para 'Stroke_Medley'
    if stroke.endswith('medley'):
        stroke_col = 'Stroke_Medley' 
    else:
        # Mapeia os outros strokes (Backstroke, Breaststroke, Butterfly, Freestyle)
        stroke_col = f'Stroke_{stroke.capitalize()}' 

    if stroke_col in input_df.columns:
        input_df[stroke_col] = 1

    # 4. Handle Gender (One-Hot Encoding)
    gender = input_data.get('Gender', 'Men').capitalize()
    gender_col = f'Gender_{gender}'
    if gender_col in input_df.columns:
        input_df[gender_col] = 1
        
    # Retorna o DataFrame na ORDEM CORRETA das colunas
    return input_df[MODEL_FEATURES]

# --------------------------------------------------------------------------
# ENDPOINTS DA API
# --------------------------------------------------------------------------

@app.route('/predict_winner', methods=['POST'])
def predict_winner():
    """
    Endpoint principal para fazer a predição.
    """
    if model is None:
        return jsonify({"status": "error", "message": "Modelo não carregado. Verifique o arquivo .pkl."}), 500
        
    try:
        data = request.json
        processed_data = preprocess_input(data)
        
        # Faz a predição
        prediction = model.predict(processed_data)
        
        return jsonify({
            "status": "success",
            "predicted_team": prediction[0],
            "message": "Predição feita com sucesso pelo modelo Decision Tree."
        })
        
    except Exception as e:
        # Captura o erro e retorna no JSON
        return jsonify({
            "status": "error",
            "message": f"Erro interno ao processar a requisição: {str(e)}"
        }), 400

# --------------------------------------------------------------------------
# EXECUÇÃO DO SERVIDOR
# --------------------------------------------------------------------------

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    # ⚠️ Use 0.0.0.0 para aceitar conexões de qualquer interface de rede local
    app.run(debug=True, host='0.0.0.0', port=5000)