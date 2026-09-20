import { patch } from "@web/core/utils/patch";
import { CategorySelector } from "@point_of_sale/app/components/category_selector/category_selector";

patch(CategorySelector.prototype, {
    getCategoriesAndSub() {
        const categories = super.getCategoriesAndSub();
        const rootCategoryIds = new Set(this.pos.rootCategories.map((category) => category.id));
        const parents = categories.filter((category) => rootCategoryIds.has(category.id));
        const children = categories.filter((category) => !rootCategoryIds.has(category.id));

        if (!children.length) {
            return categories;
        }

        return [
            ...parents,
            { id: "pos_category_rows_break", isRowBreak: true },
            ...children,
        ];
    },
});
