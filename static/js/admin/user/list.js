document.addEventListener('DOMContentLoaded', () => {
    const table = window.AdminEntity?.initFilterableTable({
        rowSelector: '#usersTableBody tr[data-search]',
        pageSize: 10,
        emptyStateId: 'emptyState',
    });

    if (!table) return;

    const rows = table.rows;
    const activeCount = rows.filter((row) => row.dataset.status === 'active').length;
    const staffCount = rows.filter((row) => row.dataset.staff === 'yes').length;
    const superuserCount = rows.filter((row) => row.dataset.superuser === 'yes').length;

    const activeNode = document.getElementById('activeUsersCount');
    const staffNode = document.getElementById('staffUsersCount');
    const superuserNode = document.getElementById('superUsersCount');

    if (activeNode) activeNode.textContent = String(activeCount);
    if (staffNode) staffNode.textContent = String(staffCount);
    if (superuserNode) superuserNode.textContent = String(superuserCount);

    window.AdminEntity?.confirmLinks('.toggle-user-link', (link) => {
        const mode = link.dataset.mode === 'deactivate' ? 'désactiver' : 'activer';
        return `Voulez-vous ${mode} ${link.dataset.name} ?`;
    });
});
