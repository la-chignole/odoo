/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import {
    getMembershipStateLabel,
    getMembershipStopLabel,
    getMembershipCategoryLabel,
} from "@pos_membership/overrides/utils/membership_label";

patch(PartnerLine.prototype, {
    materiautheque_membershipStateLabel(partner) {
        return getMembershipStateLabel(partner);
    },
    materiautheque_membershipStopLabel(partner) {
        return getMembershipStopLabel(partner);
    },
    materiautheque_membershipCategoryLabel(partner) {
        return getMembershipCategoryLabel(partner);
    },
});
