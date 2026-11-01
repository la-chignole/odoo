/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { parseFloat } from "@web/views/fields/parsers";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { pos_weight_suspendBarcodeScan } from "@pos_weight/overrides/services/barcode_reader_service";

/**
 * Ouvre le clavier numerique pour saisir/corriger le poids d'une ligne
 * et l'applique si l'utilisateur valide.
 * @param {Object} dialogService le service "dialog" (useService("dialog"))
 * @param {import("@point_of_sale/app/models/pos_order_line").PosOrderline} line
 */
export async function askOrderlineWeight(dialogService, line) {
    // Sans cela, taper "123" + Entree au clavier est pris pour un scan de
    // code-barres ("Code barre inconnu 123").
    const resumeBarcodeScan = pos_weight_suspendBarcodeScan();
    let result;
    try {
        result = await makeAwaitable(dialogService, NumberPopup, {
            title: _t("Poids (kg)"),
            startingValue: line.weight || "",
            formatDisplayedValue: (buffer) => (buffer ? `${buffer} kg` : buffer),
        });
    } finally {
        resumeBarcodeScan();
    }

    // result est `undefined` si l'utilisateur annule/ferme le popup.
    if (result !== undefined) {
        const weight = parseFloat(result);
        line.setWeight(weight);
        // Produit vendu au kg : la quantite est le poids, on la met a jour
        // aussi pour ne saisir la valeur qu'une seule fois.
        if (line.isKgUnit()) {
            line.setQuantity(weight);
        }
    }
}
