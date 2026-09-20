# -*- coding: utf-8 -*-
{
    "name": "Exports Materiautheque",
    "summary": "Génére des tableurs à partir de templates en le remplissant de données issues des bases de données odoo.",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "description": """
Moteur de génération de rapports pour une materiauthèque.

Le moteur expose des métriques qu'il est possible d'insérer dans des modèles de tableurs
pour générer des rapports complexes.

Ajouter des métriques ou des rapports intégrés demande de modifier le code du module,
mais il est possible d'envoyer manuellement ses modèles depuis l'interface odoo (si les métriques nécessaires existent déjà).
""",
    "author": "contact@lachignole.org",
    "depends": ["base", "product", "stock", "point_of_sale", "account"],
    "data": [
        "security/exports_security.xml",
        "security/ir.model.access.csv",
        "views/exports_report_template_views.xml",
        "wizards/exports_export_wizard_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
