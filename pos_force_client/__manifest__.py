# -*- coding: utf-8 -*-
{
    "name": "PoS force client",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Empêche de valider une vente PoS sans avoir selectionné de client",
    "description": """
Empêche la validation du paiement dans le PoS tant qu'aucun client n'est
selectionné sur la commande.
""",
    "author": "contact@lachignole.org",
    "depends": ["point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_force_client/static/src/**/*",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
