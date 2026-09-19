# -*- coding: utf-8 -*-
{
    "name": "PoS force membership invoice",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Empêche de valider une vente PoS contenant une adhesion sans facturer",
    "description": """
Empêche la validation du paiement si la commande contient un produit
d'adhésion et n'est pas marquée "à facturer" : le module "membership"
ne crée/renouvelle une ligne d'adhésion qu'à la validation d'une
facture client, jamais sur une simple commande PoS non facturée.
""",
    "author": "contact@lachignole.org",
    "depends": ["point_of_sale", "membership"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_force_membership_invoice/static/src/**/*",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
