document.addEventListener('DOMContentLoaded', () => {
    window.AdminEntity?.initSimpleForm({
        formId: 'couponForm',
        counters: [
            { selector: 'textarea[name="description"]', countId: 'descriptionCount', warnAt: 140, max: 220 },
        ],
    });
});
