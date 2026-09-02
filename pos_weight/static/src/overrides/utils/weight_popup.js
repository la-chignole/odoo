/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { parseFloat } from "@web/views/fields/parsers";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";

/**
 * Ouvre le clavier numerique pour saisir/corriger le poids d'une ligne
 * et l'applique si l'utilisateur valide.
 * @param {Object} dialogService le service "dialog" (useService("dialog"))
 * @param {import("@point_of_sale/app/models/pos_order_line").PosOrderline} line
 */
export async function askOrderlineWeight(dialogService, line) {
    const result = await makeAwaitable(dialogService, NumberPopup, {
        title: _t("Poids (kg)"),
        startingValue: line.weight || "",
        formatDisplayedValue: (buffer) => (buffer ? `${buffer} kg` : buffer),
    });

    // result est `undefined` si l'utilisateur annule/ferme le popup.
    if (result !== undefined) {
        line.setWeight(parseFloat(result));
    }
}
