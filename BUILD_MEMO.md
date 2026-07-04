# Mémo : Build et Release du Flight Data Recorder (FDR)

> **Dernière mise à jour :** 2026-07-04  
> **Application :** Flight Data Recorder (FDR)  
> **Dossier :** `fdr/`

---

## 📋 Sommaire

1. [Prérequis](#prerequis)
2. [Build local pour test](#build-local-pour-test)
3. [Lancer un build via GitHub Actions](#lancer-un-build-via-github-actions)
4. [Procédure complète de release](#procédure-complète-de-release)
5. [Tests recommandés](#tests-recommandés)
6. [Dépannage](#dépannage)
7. [Structure des fichiers générés](#structure-des-fichiers-générés)

---

## 🔧 Prérequis

### Outils nécessaires
- **Git** (version 2.x+)
- **Python** 3.13+ (recommandé)
- **venv** déjà configuré dans `fdr/` (avec PySide6 et PyInstaller)
- **Compte GitHub** avec accès au dépôt

### Vérification rapide
```bash
# Vérifier Python
python --version

# Vérifier PyInstaller dans le venv FDR
cd fdr
source bin/activate
pyinstaller --version
```

---

## 🏗️ Build local pour test

> **À exécuter avant de pusher un tag pour vérifier que tout fonctionne**

### Sur Linux

```bash
# 1. Aller dans le dossier FDR
cd /home/laurent/AirRallies/fdr

# 2. Activer le venv
source bin/activate

# 3. Nettoyer les anciens builds
rm -rf dist-linux build-linux

# 4. Builder
pyinstaller --onedir --name fdr --clean --distpath ./dist-linux --workpath ./build-linux fdr.py

# 5. Post-traitement (séparation PySide6)
chmod +x post_build_linux.sh
./post_build_linux.sh

# 6. Tester l'exécutable
cd dist-linux/fdr
./fdr
```

**Vérifier que :**
- ✅ L'application GUI s'ouvre
- ✅ Pas d'erreurs dans le terminal
- ✅ L'interface est en français ou anglais selon la locale
- ✅ PySide6 est bien dans le dossier `pyside6/`

### Sur Windows

```cmd
cd C:\chemin\vers\AirRallies\fdr
Scripts\activate

rmdir /s /q dist-windows build-windows

pyinstaller --onedir --name fdr --clean --distpath ./dist-windows --workpath ./build-windows --windowed fdr.py

post_build_windows.bat

cd dist-windows\fdr
double click sur fdr.bat
```

**Vérifier que :**
- ✅ L'application s'ouvre sans console
- ✅ PySide6 est dans `pyside6\`
- ✅ Les DLLs Qt6 sont dans `pyside6\lib\`

---

## 🚀 Lancer un build via GitHub Actions

### Méthode 1 : Build automatique sur Push de tag (RECOMMANDÉ)

```bash
# 1. Vérifier que tout est commité
git status

# 2. Créer un tag de version (format vX.Y.Z)
git tag v1.0.0

# 3. Pousser le tag
git push --tags
```

**Ce qui se passe automatiquement :**
1. GitHub détecte le push du tag `v1.0.0`
2. Les 3 jobs de build démarrent en parallèle (Linux, Windows, macOS)
3. Chaque job :
   - Installe les dépendances
   - Build avec PyInstaller
   - Exécute le post-build
   - Crée l'archive versionnée
4. Le job `publish-release` :
   - Télécharge les 3 archives
   - **Crée un Release GitHub** avec les assets
5. **Résultat :** Release disponible sur `github.com/[org]/AirRallies/releases`

### Méthode 2 : Build manuel via Pull Request

> **Utile pour tester avant de créer un tag**

1. Faire une branche de feature/test
2. Pousser les changements
3. Créer une Pull Request
4. GitHub Actions exécutera les builds (mais **ne publiera pas de Release**)
5. Vérifier les artifacts dans l'onglet **Actions** de la PR

---

## 🎯 Procédure complète de release

### Checklist avant release

- [ ] Code testé localement sur Linux
- [ ] Code testé localement sur Windows (si possible)
- [ ] Toutes les modifications commitées
- [ ] `fdr/BUILD.md` est à jour
- [ ] `.github/workflows/build-fdr.yml` est à jour
- [ ] Version cohérente dans `fdr.py` (ABOUT_VERSION)

### Étapes de release

```bash
# 1. Vérifier la propreté du code
git status

# 2. Mettre à jour la version dans le code si nécessaire
#    (dans fdr/ui/translations.py, chercher ABOUT_VERSION)

# 3. Tester le build local
cd fdr
source bin/activate
./build_and_test.sh  # (si tu en as un)

# 4. Tout commiter
git add .
git commit -m "Prepare release v1.0.0"

# 5. Pousser
git push

# 6. Créer et pousser le tag
git tag v1.0.0
git push --tags
```

### Après le push du tag

1. **Attendre ~10-15 minutes** (le temps que GitHub Actions termine les 3 builds)
2. **Vérifier les Actions** :
   - Aller sur : `https://github.com/[ton-org]/AirRallies/actions`
   - Vérifier que les 4 jobs (3 builds + publish-release) sont ✅ verts
3. **Vérifier le Release** :
   - Aller sur : `https://github.com/[ton-org]/AirRallies/releases`
   - Le nouveau release `v1.0.0` doit apparaître
   - Les 3 assets doivent être présents :
     - `fdr-linux-1.0.0.tar.gz`
     - `fdr-windows-1.0.0.zip`
     - `fdr-macos-1.0.0.tar.gz`

---

## 🧪 Tests recommandés

### Tests avant build

| Test | Commande | Résultat attendu |
|------|----------|------------------|
| Vérifier Python | `python --version` | 3.13.x |
| Vérifier PyInstaller | `pyinstaller --version` | 6.21.0+ |
| Vérifier les imports | `python -c "from PySide6.QtWidgets import QApplication"` | Pas d'erreur |
| Lancer l'app en dev | `cd fdr && python fdr.py` | GUI s'ouvre |

### Tests après build local

| Plateforme | Commande | Résultat attendu |
|-----------|----------|------------------|
| Linux | `cd dist-linux/fdr && ./fdr` | GUI s'ouvre, pas d'erreur |
| Linux | `ls dist-linux/fdr/pyside6/` | Dossier existe avec libs |
| Windows | `cd dist-windows\fdr && fdr.bat` | GUI s'ouvre |
| Windows | `dir dist-windows\fdr\pyside6\` | Dossier existe avec DLLs |

### Tests après GitHub Actions

1. **Télécharger les artifacts** depuis l'onglet Actions
2. **Extraire chaque archive**
3. **Vérifier la structure** :
   ```
   fdr-linux-1.0.0/
   ├── fdr          # Script de lancement
   ├── fdr.bin      # Binaire
   ├── _internal/   # Dépendances
   └── pyside6/    # PySide6 séparé
   ```
4. **Tester l'exécutable** sur chaque plateforme

---

## ⚠️ Dépannage

### Problèmes courants

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| Build échoue sur Linux | Manque de dépendances système | `sudo apt install libxcb-xinerama0` |
| PySide6 non trouvé | Venv non activé | `source bin/activate` avant le build |
| Erreur "Library not found" | DLLs/so manquants | Normal, warnings non-critiques |
| Release non créé | Tag ne commence pas par `v` | Utiliser `git tag v1.0.0` |
| Jobs bloqués | Ressources GitHub insuffisantes | Attendre ou annuler et relancer |

### Vérifier les logs GitHub Actions

1. Aller sur : `https://github.com/[ton-org]/AirRallies/actions`
2. Cliquer sur le workflow en cours
3. Voir les logs détaillés de chaque job
4. Chercher les erreurs en rouge

### Builder manuellement depuis les artifacts

Si le Release échoue mais que les artifacts sont disponibles :

```bash
# Télécharger les artifacts depuis l'onglet Actions
# Extraire et tester manuellement
mkdir test-release
cd test-release

# Pour Linux
tar -xzf fdr-linux-1.0.0.tar.gz
cd fdr-linux-1.0.0
./fdr

# Pour Windows (en PowerShell)
Expand-Archive fdr-windows-1.0.0.zip
cd fdr-windows-1.0.0
./fdr.bat
```

---

## 📦 Structure des fichiers générés

### Par plateforme

**Linux :**
```
fdr-linux-1.0.0.tar.gz
└── fdr/
    ├── fdr              # Script de lancement (bash)
    ├── fdr.bin          # Binaire exécutable
    ├── _internal/       # Code Python et ressources
    │   ├── base_library.zip
    │   ├── PySide6/      # Modules Python (liens symboliques)
    │   └── ...
    └── pyside6/         # Bibliothèques PySide6
        ├── PySide6 -> _internal/PySide6
        ├── shiboken6 -> _internal/shiboken6
        ├── lib/          # .so files
        ├── Qt/lib/       # Bibliothèques Qt6
        └── plugins/      # Plugins Qt6
```

**Windows :**
```
fdr-windows-1.0.0.zip
└── fdr\
    ├── fdr.bat          # Script de lancement (batch)
    ├── fdr_bin.exe      # Binaire exécutable
    ├── _internal\       # Code Python et ressources
    │   ├── base_library.zip
    │   ├── PySide6\     # Modules Python (junctions)
    │   └── ...
    └── pyside6\         # Bibliothèques PySide6
        ├── PySide6 -> _internal\PySide6
        ├── shiboken6 -> _internal\shiboken6
        ├── lib\         # DLL files
        ├── Qt\lib\     # Bibliothèques Qt6
        └── plugins\     # Plugins Qt6
```

**macOS :** (structure similaire à Linux)
```
fdr-macos-1.0.0.tar.gz
└── fdr/
    ├── fdr              # Script de lancement
    ├── fdr.bin          # Binaire exécutable
    ├── _internal/
    └── pyside6/
```

---

## 📚 Références

- **Documentation complète :** `fdr/BUILD.md`
- **Workflow GitHub Actions :** `.github/workflows/build-fdr.yml`
- **Scripts post-build :** `fdr/post_build_linux.sh`, `fdr/post_build_windows.bat`

---

## 📞 Support

Pour toute question ou problème :
- Vérifier d'abord ce mémo et le fichier `BUILD.md`
- Consulter les logs GitHub Actions
- Tester le build en local

---

*Ce mémo est conçu pour être imprimé ou gardé sous la main lors des opérations de build et release.*
