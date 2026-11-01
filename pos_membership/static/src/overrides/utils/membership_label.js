/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { deserializeDate, formatDate } from "@web/core/l10n/dates";

const VALID_MEMBERSHIP_STATES = ["invoiced", "paid", "free"];

const STATE_LABELS = {
    none: _t("Non adhérent"),
    canceled: _t("Adhésion annulée"),
    old: _t("Ancien adhérent"),
    waiting: _t("Adhésion en attente"),
    invoiced: _t("Adhésion facturée"),
    free: _t("Membre gratuit"),
    paid: _t("Membre à jour"),
};

export function isMembershipValid(partner) {
    return Boolean(VALID_MEMBERSHIP_STATES.includes(partner?.membership_state));
}

export function getMembershipStateLabel(partner) {
    // membership_state est `false` (jamais adhérent) pour un partenaire qui
    // n'a jamais eu de ligne d'adhésion : on l'affiche comme "Non adherent",
    // au meme titre que l'état explicite "none".
    return STATE_LABELS[partner?.membership_state] || STATE_LABELS.none;
}

export function getMembershipStopLabel(partner) {
    if (!partner?.membership_stop) {
        return "";
    }
    return formatDate(partner.membership_stop);
}
