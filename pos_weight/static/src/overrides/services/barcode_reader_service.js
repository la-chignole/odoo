/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { BarcodeReader } from "@point_of_sale/app/services/barcode_reader_service";

// Le service "barcode" de Odoo ecoute le clavier sur toute la page : une
// suite de touches tapees rapidement puis "Entree" (ex. "123" + Entree dans
// le popup de poids) est prise pour un scan, ce qui affiche une notification
// "Code barre inconnu" avec un son. On ignore donc les scans tant qu'un popup
// de saisie du poids est ouvert.
let suspendCount = 0;

/**
 * Ignore les scans de code-barres jusqu'a l'appel de la fonction retournee.
 * @returns {Function} fonction qui reactive les scans
 */
export function pos_weight_suspendBarcodeScan() {
    suspendCount++;
    let resumed = false;
    return () => {
        if (!resumed) {
            resumed = true;
            suspendCount--;
        }
    };
}

patch(BarcodeReader.prototype, {
    // scan() est appele de facon synchrone pendant le keydown, avant que le
    // raccourci "Entree" du popup ne le ferme : le compteur est donc encore
    // actif au moment du test.
    scan(code) {
        if (suspendCount > 0) {
            return Promise.resolve();
        }
        return super.scan(...arguments);
    },
});
