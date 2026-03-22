sed -i "1i\
Ce SDK est en développement actif. L'API peut changer avant la v1.0.\n\
Contributions bienvenues — voir [CONTRIBUTING.md](CONTRIBUTING.md).\n\n" README.md
sed -i '/^| Initialisation du client |/s/|[^|]*|/| ✅ |/' README.md
sed -i '/^| Gestion des objets (CRUD) |/s/|[^|]*|/| 🚧 |/' README.md
sed -i '/^| Requêtes |/s/|[^|]*|/| 🚧 |/' README.md
sed -i '/^| Utilisateurs & Authentification |/s/|[^|]*|/| 🚧 |/' README.md
sed -i '/^| Fichiers |/s/|[^|]*|/| 📋 |/' README.md
sed -i '/^| Fonctions Cloud |/s/|[^|]*|/| 📋 |/' README.md
sed -i 's|github\.com/[^/]\+/[^/]\+|github.com/Kether-Labs/parsepy|g' README.md