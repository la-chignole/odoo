/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import {
    isMembershipValid,
    getMembershipStateLabel,
    getMembershipStopLabel,
} from "@pos_membership/overrides/utils/membership_label";

patch(PartnerLine.prototype, {
    pos_membershipIsValid(partner) {
        return isMembershipValid(partner);
    },
    pos_membershipStateLabel(partner) {
        return getMembershipStateLabel(partner);
    },
    pos_membershipStopLabel(partner) {
        return getMembershipStopLabel(partner);
    },
});
