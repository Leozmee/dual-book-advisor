#!/usr/bin/env python3
"""
Test pour identifier le problème de détection des mots-clés manga
"""

def test_manga_keywords():
    manga_keywords = [
        'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
        'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
        'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
        'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
        'tintin', 'astérix', 'superhéros'
    ]
    
    query = "qui a écrit Au Bonheur des Dames"
    query_lower = query.lower()
    
    print(f"🔍 Analyse de la requête: '{query}'")
    print(f"🔍 Requête minuscule: '{query_lower}'")
    
    # Vérifier chaque mot-clé
    matched_keywords = []
    for keyword in manga_keywords:
        if keyword in query_lower:
            matched_keywords.append(keyword)
            print(f"✅ Mot-clé trouvé: '{keyword}'")
    
    if matched_keywords:
        print(f"\n🎯 Mots-clés détectés: {matched_keywords}")
        print(f"💡 Nombre total: {len(matched_keywords)}")
    else:
        print("\n❌ Aucun mot-clé manga détecté")

if __name__ == "__main__":
    test_manga_keywords()