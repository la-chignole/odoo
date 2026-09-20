# -*- coding: utf-8 -*-
{
    "name": "PoS category rows",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Affiche les sous-categories PoS sur une ligne separee des categories parentes",
    "description": """
Dans l'ecran de vente, quand une categorie parente est selectionnee, ses
sous-categories s'affichent normalement intercalees dans la meme grille que
les categories parentes. Ce module les regroupe sur une ligne distincte,
sous la ligne des categories parentes, pour rendre la barre de categories
plus lisible.
""",
    "author": "contact@lachignole.org",
    "depends": ["point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_category_rows/static/src/**/*",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
