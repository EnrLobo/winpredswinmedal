import React, { useState } from 'react';
// Se você estiver usando TypeScript, você pode precisar instalar e usar o Axios, 
// mas o fetch nativo funciona perfeitamente.

const API_URL = 'http://127.0.0.1:5000/predict_winner';

function PredictionForm() {
    // 1. Estados para gerenciar a entrada do usuário e o resultado
    const [formData, setFormData] = useState({
        Year: 2028,
        'Distance (in meters)': '100m',
        Stroke: 'Freestyle',
        Gender: 'Men'
    });
    
    // Estados para feedback visual
    const [prediction, setPrediction] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // 2. Manipulador de Mudança (Atualiza o estado do formulário)
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: name === 'Year' ? parseInt(value) : value
        }));
    };

    // 3. Manipulador de Submissão (Chama a API Flask)
    const handleSubmit = async (e) => {
        e.preventDefault(); // Previne o recarregamento padrão da página

        setIsLoading(true);
        setError(null);
        setPrediction(null);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            // 4. Processa a Resposta
            if (response.ok && result.status === 'success') {
                setPrediction(result.predicted_team);
            } else {
                // Erro retornado pela API (Ex: "Feature names missing")
                throw new Error(`Erro na API: ${result.message || response.statusText}`);
            }

        } catch (err) {
            console.error("Erro ao processar a requisição:", err);
            setError(err.message.includes("Failed to fetch") 
                     ? "Erro de Conexão: Certifique-se de que a API Flask está rodando em http://127.0.0.1:5000" 
                     : err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // 5. Renderização da Interface
    return (
        <div style={styles.container}>
            <h2>🏆 Previsor de Vencedor de Natação</h2>
            
            <form onSubmit={handleSubmit} style={styles.form}>
                
                {/* Campo Ano */}
                <label style={styles.label}>Ano da Competição:</label>
                <input 
                    type="number" 
                    name="Year" 
                    value={formData.Year} 
                    onChange={handleChange} 
                    required 
                    style={styles.input}
                />

                {/* Campo Distância */}
                <label style={styles.label}>Distância (em metros):</label>
                <select 
                    name="Distance (in meters)" 
                    value={formData['Distance (in meters)']} 
                    onChange={handleChange} 
                    required
                    style={styles.select}
                >
                    {['100m', '200m', '400m', '800m', '1500m', '4x100m'].map(dist => (
                        <option key={dist} value={dist}>{dist}</option>
                    ))}
                </select>

                {/* Campo Estilo de Nado */}
                <label style={styles.label}>Estilo de Nado:</label>
                <select 
                    name="Stroke" 
                    value={formData.Stroke} 
                    onChange={handleChange} 
                    required
                    style={styles.select}
                >
                    {['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly', 'Individual medley'].map(stroke => (
                        <option key={stroke} value={stroke}>{stroke}</option>
                    ))}
                </select>
                
                {/* Campo Gênero */}
                <label style={styles.label}>Gênero:</label>
                <select 
                    name="Gender" 
                    value={formData.Gender} 
                    onChange={handleChange} 
                    required
                    style={styles.select}
                >
                    <option value="Men">Masculino</option>
                    <option value="Women">Feminino</option>
                </select>

                <button type="submit" disabled={isLoading} style={styles.button}>
                    {isLoading ? 'Prevendo...' : 'Prever Vencedor'}
                </button>
            </form>

            {/* Exibição do Resultado/Erro */}
            {error && <div style={styles.error}>{`Erro: ${error}`}</div>}
            {prediction && (
                <div style={styles.success}>
                    A equipe prevista para vencer é: <strong>{prediction}</strong>
                </div>
            )}
        </div>
    );
}

// Estilos básicos (pode ser movido para um arquivo CSS)
const styles = {
    container: { maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' },
    form: { display: 'flex', flexDirection: 'column' },
    label: { marginTop: '10px', fontWeight: 'bold' },
    input: { padding: '8px', marginTop: '4px', border: '1px solid #aaa', borderRadius: '4px', boxSizing: 'border-box' },
    select: { padding: '8px', marginTop: '4px', border: '1px solid #aaa', borderRadius: '4px' },
    button: { backgroundColor: '#007bff', color: 'white', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '20px' },
    error: { marginTop: '20px', padding: '10px', backgroundColor: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb', borderRadius: '4px' },
    success: { marginTop: '20px', padding: '15px', border: '2px solid #28a745', borderRadius: '4px', fontSize: '1.1em', fontWeight: 'bold' }
};

export default PredictionForm;