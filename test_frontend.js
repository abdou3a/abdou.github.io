// Test de connexion au serveur OSINT-AI
const API_BASE_URL = 'http://localhost:8000';

async function testServer() {
    console.log('🧪 Test de connexion au serveur OSINT-AI...');
    
    try {
        // Test 1: Health check
        console.log('1. Test de santé du serveur...');
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        const healthData = await healthResponse.json();
        console.log('✅ Serveur en ligne:', healthData);
        
        // Test 2: Test d'inscription
        console.log('2. Test d\'inscription...');
        const registerData = {
            username: 'testuser123',
            email: 'test123@example.com',
            password: 'testpassword',
            plan: 'free'
        };
        
        const registerResponse = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });
        
        if (registerResponse.ok) {
            const registerResult = await registerResponse.json();
            console.log('✅ Inscription réussie:', registerResult);
        } else {
            const errorData = await registerResponse.json();
            console.log('❌ Erreur d\'inscription:', errorData);
        }
        
    } catch (error) {
        console.error('❌ Erreur de connexion:', error);
    }
}

// Exécuter le test
testServer();
