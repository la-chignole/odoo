# -*- coding: utf-8 -*-
{
    "name": "Materiautheque - Adhesions en PoS",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Affiche le statut d'adhesion (membership) des clients dans le PoS, avec code couleur",
    "description": """
Reimplementation, pour Odoo 19, du pont entre le module "membership" (OCA
vertical-association) et le Point de Vente. L'ancien module OCA
pos_membership (16.0) dependait du module core "membership", qui n'existe
plus a partir d'Odoo 19 (remplace par la version OCA vertical-association).

- Nom du client colore en rouge/vert selon son statut d'adhesion, visible
  directement dans l'ecran de vente principal (bouton client).
- Dans la liste des clients : badge colore affichant le statut, la date
  de fin et la/les categorie(s) d'adhesion en cours ou passee.

Le blocage de la validation du paiement pour les commandes non facturees
contenant une adhesion est fourni par le module "pos_force_membership_invoice".
""",
    "author": "Materiautheque",
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
