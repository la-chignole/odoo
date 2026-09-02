# -*- coding: utf-8 -*-
{
    "name": "Materiautheque - Suivi du poids en PoS",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Ajoute un poids (kg) sur chaque ligne de vente PoS, pour les rapports matieres",
    "description": """
Ajoute un champ "Poids (kg)" sur chaque ligne de commande PoS.

- Bouton dedie dans l'ecran de vente pour saisir le poids d'une ligne.
- Badge cliquable sur chaque ligne du ticket (vert si renseigne, orange
  sinon) pour voir et corriger le poids d'un coup d'oeil.
- Remplissage automatique a partir de la quantite pour les produits vendus
  en kg (le bouton "Poids" est alors masque, la quantite faisant deja foi ;
  le badge reste affiche en vert avec le poids deduit).
- Ecran de gestion (Point de Vente > Commandes > Poids des ventes) pour
  corriger un poids apres coup, meme sur une commande deja cloturee.
- Case "Poids non requis en PoS" sur la categorie PoS (Point de Vente >
  Configuration > Categories PoS) : les produits d'une categorie PoS ainsi
  cochee (services, par exemple) n'affichent ni le bouton ni le badge de
  poids.
""",
    "author": "Materiautheque",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_order_line_views.xml",
        "views/pos_category_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_weight/static/src/**/*",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
