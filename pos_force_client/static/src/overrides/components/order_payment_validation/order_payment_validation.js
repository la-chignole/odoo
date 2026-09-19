/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

patch(OrderPaymentValidation.prototype, {
    async isOrderValid(isForceValidate) {
        const valid = await super.isOrderValid(isForceValidate);
        if (!valid) {
            return false;
        }

        if (!this.order.getPartner()) {
            this.pos.dialog.add(AlertDialog, {
                title: _t("Client requis"),
                body: _t(
                    "Merci de selectionner un client avant de valider le" + " paiement."
                ),
            });
            return false;
        }

        return true;
    },
});
