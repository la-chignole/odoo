# -*- coding: utf-8 -*-
{
    "name": "PoS membership",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Affiche le statut d'adhésion (membership) des clients dans le PoS, avec code couleur",
    "description": """
- Nom du client colore en rouge/vert selon son statut d'adhésion, visible
  directement dans l'écran de vente principal (bouton client).
- Dans la liste des clients : badge coloré affichant le statut, la date
  de fin et la/les catégorie(s) d'adhésion en cours ou passee.
""",
    "author": "contact@lachignole.org",
    "depends": ["point_of_sale", "membership", "pos_force_membership_invoice"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_membership/static/src/**/*",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
