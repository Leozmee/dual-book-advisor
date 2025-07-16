#!/usr/bin/env python3
"""
Test pour vérifier la détection des mots-clés dans SimpleAgentManager
"""

def test_simple_agent_detection():
    # Mots-clés comics/BD françaises (comme dans SimpleAgentManager)
    comics_keywords = [
        'comics', 'bd', 'bande dessinée', 'bande-dessinée', 'album',
        'superman', 'batman', 'spider-man', 'spiderman', 'wonder woman',
        'x-men', 'avengers', 'justice league', 'marvel', 'dc',
        'tintin', 'astérix', 'lucky luke', 'gaston', 'spirou',
        'superhéros', 'super-héros', 'héros', 'vilain',
        'comics français', 'bd française', 'album graphique'
    ]
    
    query = "qui a écrit Au Bonheur des Dames"
    query_lower = query.lower()
    
    print(f"🔍 Analyse de la requête: '{query}'")
    print(f"🔍 Requête minuscule: '{query_lower}'")
    
    # Vérifier chaque mot-clé
    matched_keywords = []
    for keyword in comics_keywords:
        if keyword in query_lower:
            matched_keywords.append(keyword)
            print(f"✅ Mot-clé trouvé: '{keyword}'")
    
    if matched_keywords:
        print(f"\n🎯 Mots-clés détectés: {matched_keywords}")
        print(f"💡 Nombre total: {len(matched_keywords)}")
        
        # Vérifier spécifiquement "bande dessinée"
        if 'bande dessinée' in query_lower:
            print("⚠️  'bande dessinée' détecté via substring")
        
        # Vérifier chaque partie de "bande dessinée"
        for part in ['bande', 'dessinée', 'des']:
            if part in query_lower:
                print(f"🔍 Partie '{part}' trouvée dans la requête")
    else:
        print("\n❌ Aucun mot-clé BD/comics détecté")

if __name__ == "__main__":
    test_simple_agent_detection()