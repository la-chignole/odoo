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

        const hasMembershipProduct = this.order
            .getOrderlines()
            .some((line) => line.product_id?.product_tmpl_id?.membership);

        if (hasMembershipProduct && !this.order.isToInvoice()) {
            this.pos.dialog.add(AlertDialog, {
                title: _t("Facture requise"),
                body: _t(
                    "Une facture est necessaire pour vendre une adhesion : le" +
                        " renouvellement n'est enregistre qu'a la validation d'une" +
                        " facture. Activez la facturation pour cette commande avant" +
                        " de valider le paiement."
                ),
            });
            return false;
        }

        return true;
    },
});
