# -*- coding: utf-8 -*-
{
    "name": "PoS weight",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Ajoute un poids (kg) sur chaque ligne de vente PoS",
    "description": """
Ajoute un champ "Poids (kg)" sur chaque ligne de commande PoS.

- Bouton dedié dans l'écran de vente pour saisir le poids d'une ligne.
- Badge cliquable sur chaque ligne du ticket (vert si renseigné, orange
  sinon) pour voir et corriger le poids.
- Remplissage automatique a partir de la quantité pour les produits vendus
  en kg (le bouton "Poids" est alors masqué, la quantité faisant déjà foi ;
  le badge reste affiche en vert avec le poids déduit).
- Écran de gestion (Point de Vente > Commandes > Poids des ventes) pour
  corriger un poids après coup, meme sur une commande déjà cloturée.
- Case "Poids non requis en PoS" sur la catégorie PoS (Point de Vente >
  Configuration > Categories PoS) : les produits d'une catégorie PoS ainsi
  cochée (services, par exemple) n'affichent ni le bouton ni le badge de
  poids.
""",
    "author": "contact@lachignole.org",
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
