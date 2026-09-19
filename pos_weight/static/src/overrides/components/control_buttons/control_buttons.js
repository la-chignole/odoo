/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { askOrderlineWeight } from "@pos_weight/overrides/utils/weight_popup";

patch(ControlButtons.prototype, {
    // this.dialog et this.currentOrder existent deja sur ControlButtons.
    async pos_weight_clickWeight() {
        const line = this.currentOrder?.getSelectedOrderline();
        if (!line) {
            return;
        }
        await askOrderlineWeight(this.dialog, line);
    },
});
