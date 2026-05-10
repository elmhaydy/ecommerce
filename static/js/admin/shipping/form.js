document.addEventListener('DOMContentLoaded', () => {
    window.AdminEntity?.initSimpleForm({
        formId: 'shippingForm',
        counters: [
            { selector: 'textarea[name="notes"]', countId: 'notesCount', warnAt: 160, max: 260 },
        ],
    });
});
