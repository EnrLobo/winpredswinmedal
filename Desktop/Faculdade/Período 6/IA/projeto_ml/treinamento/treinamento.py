import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import numpy as np

# Nome do arquivo de dados original
FILE_NAME = 'Olympic_Swimming_Results_1912to2020.csv'

# --- 1. FUNÇÃO DE PRÉ-PROCESSAMENTO PARA DISTÂNCIA ---
def calculate_distance(dist_str):
    """
    Converte a string da distância (ex: '100m', '4x100m') para um valor numérico (em metros).
    """
    dist_str = str(dist_str).lower().replace('m', '')

    if 'x' in dist_str:
        # Lida com revezamentos (ex: '4x100' -> 400.0)
        try:
            parts = dist_str.split('x')
            return float(parts[0]) * float(parts[1])
        except ValueError:
            return None
    else:
        # Lida com distâncias individuais (ex: '100' -> 100.0)
        try:
            return float(dist_str)
        except ValueError:
            return None

# -------------------------------------------------------------------------
# ETAPA DE FILTRAGEM E PREPARAÇÃO DOS DADOS (Feature Engineering)
# -------------------------------------------------------------------------

print("--- 1. INÍCIO DA PREPARAÇÃO DOS DADOS ---")

# Carrega o Dataset Original
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    print(f"ERRO: Arquivo {FILE_NAME} não encontrado.")
    exit()

# Aplica a função para criar a feature numérica 'Distance_m'
df['Distance_m'] = df['Distance (in meters)'].apply(calculate_distance)

# Remove linhas com valores nulos em features essenciais
df.dropna(subset=['Distance_m', 'Athlete', 'Results'], inplace=True)

# 2. FILTRAGEM (Foco em medalhistas)
# Mantém apenas as linhas com rank de medalha (Rank <= 3)
df_winners = df[df['Rank'] <= 3].copy()

# 3. FILTRAGEM POR CLASSE (TOP 10 PAÍSES)
# Reduz o número de classes-alvo para os 10 países que mais ganharam medalhas
top_teams = df_winners['Team'].value_counts().nlargest(10).index
df_filtered = df_winners[df_winners['Team'].isin(top_teams)].copy()

# Remove colunas auxiliares e o 'Results' (tempo/placar) pois não é uma feature de predição
df_filtered.drop(
    columns=['Results', 'Distance (in meters)', 'Rank', 'Athlete', 'Location'],
    inplace=True,
    errors='ignore'
)

print(f"Dataset Filtrado: {len(df_filtered)} tuplas. Top 10 Países:\n{df_filtered['Team'].value_counts()}")
print("-------------------------------------------------------------------------")

# -------------------------------------------------------------------------
# ETAPA DE TREINAMENTO E TESTE DO MODELO DECISION TREE
# -------------------------------------------------------------------------

print("--- 2. TREINAMENTO DO MODELO DECISION TREE ---")

# Define Features (X) e Target (Y)
# Features escolhidas: 'Year', 'Distance_m', 'Relay?', 'Stroke', 'Gender'
features = ['Year', 'Distance_m', 'Relay?', 'Stroke', 'Gender']
X = df_filtered[features]
Y = df_filtered['Team']

# 4. CODIFICAÇÃO (One-Hot Encoding)
# Converte as features categóricas em formato numérico
X_encoded = pd.get_dummies(X, columns=['Stroke', 'Gender'], drop_first=False)
# drop_first=False é usado aqui para garantir que todas as colunas de stroke e gênero sejam visíveis no código Flask

# 5. SPLIT (Divisão Treinamento e Teste)
X_train, X_test, Y_train, Y_test = train_test_split(
    X_encoded, Y,
    test_size=0.3,
    random_state=42,
    stratify=Y
)

# 6. TREINAMENTO
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, Y_train)

# 7. AVALIAÇÃO
Y_pred = model.predict(X_test)
accuracy = accuracy_score(Y_test, Y_pred)

print(f"\nDecision Tree Treinada.")
print(f"Acurácia no Conjunto de Teste: {accuracy:.2f}")

# 8. SALVAR O MODELO PARA IMPLANTAÇÃO (Flask API)
model_file_name = 'swimming_winner_model.pkl'
joblib.dump(model, model_file_name)

print(f"\nModelo salvo com sucesso para implantação: '{model_file_name}'")

# 9. SALVAR A LISTA DE FEATURES (CRUCIAL PARA O FLASK)
model_features_list = X_encoded.columns.to_list()
print("\nLista de FEATURES FINAIS para o FLASK (Ordem Exata):")
print(model_features_list)

print("\n--- PROCESSO CONCLUÍDO ---")