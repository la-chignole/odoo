# -*- coding: utf-8 -*-
{
    "name": "PoS - Facture obligatoire pour les adhesions",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Empeche de valider une vente PoS contenant une adhesion sans facturer",
    "description": """
Empeche la validation du paiement si la commande contient un produit
d'adhesion et n'est pas marquee "a facturer" : le module "membership"
ne cree/renouvelle une ligne d'adhesion qu'a la validation d'une
facture client, jamais sur une simple commande PoS non facturee.
""",
    "author": "Materiautheque",
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
