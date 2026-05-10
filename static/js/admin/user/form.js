document.addEventListener('DOMContentLoaded', () => {
    window.AdminEntity?.initSimpleForm({
        formId: 'userForm',
        counters: [
            { selector: 'textarea[name="bio"]', countId: 'bioCount', warnAt: 180, max: 320 },
        ],
    });
});
