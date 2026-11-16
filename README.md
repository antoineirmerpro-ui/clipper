# Clipper

Outil personnel : un lien YouTube → les meilleurs moments en extraits verticaux sous-titrés + un score de viralité estimé.
Fonctionne dans Google Colab (gratuit, avec GPU).

## Utilisation
1. Ouvrir `clipper.ipynb` dans Google Colab.
2. Exécution → Modifier le type d'exécution → **GPU T4**.
3. Exécution → Tout exécuter, puis coller le lien YouTube dans la case qui apparaît sous la cellule ② et appuyer sur Entrée.

## Avancement
- [x] Jour 1 : téléchargement + transcription horodatée
- [ ] Jour 2 : choix des moments (copier-coller avec Claude) + montage vertical sous-titré
- [ ] Jour 3 : score de viralité + mode d'emploi

Usage personnel uniquement : ne pas republier les extraits de vidéos d'autres créateurs sans leur accord.

Le notebook est généré par `tools/build_notebook.py` (`python3 tools/build_notebook.py clipper.ipynb`).
