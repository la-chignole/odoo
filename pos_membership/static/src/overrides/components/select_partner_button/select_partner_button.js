/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SelectPartnerButton } from "@point_of_sale/app/screens/product_screen/control_buttons/select_partner_button/select_partner_button";
import { isMembershipValid } from "@pos_membership/overrides/utils/membership_label";

patch(SelectPartnerButton.prototype, {
    pos_membershipIsValid(partner) {
        return isMembershipValid(partner);
    },
});
