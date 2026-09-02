/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { deserializeDate, formatDate } from "@web/core/l10n/dates";

const STATE_LABELS = {
    none: _t("Non adhérent"),
    canceled: _t("Adhésion annulée"),
    old: _t("Ancien adhérent"),
    waiting: _t("Adhésion en attente"),
    invoiced: _t("Adhésion facturée"),
    free: _t("Membre gratuit"),
    paid: _t("Membre à jour"),
};

export function getMembershipStateLabel(partner) {
    // membership_state est `false` (jamais adherent) pour un partenaire qui
    // n'a jamais eu de ligne d'adhesion : on l'affiche comme "Non adherent",
    // au meme titre que l'etat explicite "none".
    return STATE_LABELS[partner?.membership_state] || STATE_LABELS.none;
}

export function getMembershipStopLabel(partner) {
    if (!partner?.membership_stop) {
        return "";
    }
    return formatDate(partner.membership_stop);
}

export function getMembershipCategoryLabel(partner) {
    const categories = partner?.membership_category_ids || [];
    if (!categories.length) {
        return "";
    }
    return categories.map((category) => category.name).join(", ");
}
