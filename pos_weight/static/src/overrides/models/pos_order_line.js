/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

patch(PosOrderline.prototype, {
    /**
     * Vrai si le produit de la ligne est vendu en kg : la quantite
     * represente alors deja le poids, pas besoin de saisie manuelle.
     */
    isKgUnit() {
        const unit = this.getUnit();
        return Boolean(unit && unit.name && unit.name.trim().toLowerCase() === "kg");
    },
    getWeight() {
        if (this.weight) {
            return this.weight;
        }
        return this.isKgUnit() ? this.getQuantity() : 0;
    },
    setWeight(weight) {
        this.weight = weight || 0;
    },
    get weightStr() {
        return this.getWeight().toFixed(3);
    },
    get hasWeight() {
        return this.getWeight() !== 0;
    },
    get hideWeight() {
        // pos_categ_ids est un many2many : le produit peut appartenir a
        // plusieurs categories PoS, la case cochee sur une seule suffit.
        const categories = this.product_id?.product_tmpl_id?.pos_categ_ids || [];
        return categories.some((category) => category.hide_weight_in_pos);
    },
});
