/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { askOrderlineWeight } from "@pos_weight/overrides/utils/weight_popup";

patch(Orderline.prototype, {
    setup() {
        super.setup();
        this.pos_weight_dialog = useService("dialog");
    },

    /** Ouvre le popup de poids en cliquant directement sur le badge de la ligne. */
    async pos_weight_openWeightPopup() {
        await askOrderlineWeight(this.pos_weight_dialog, this.line);
    },
});
