document.addEventListener('DOMContentLoaded', () => {
    const table = window.AdminEntity?.initFilterableTable({
        rowSelector: '#couponTableBody tr[data-search]',
        pageSize: 10,
        emptyStateId: 'emptyState',
    });

    if (!table) return;

    const rows = table.rows;
    const activeCount = rows.filter((row) => row.dataset.status === 'active').length;
    const percentCount = rows.filter((row) => row.dataset.type === 'PERCENTAGE').length;
    const fixedCount = rows.filter((row) => row.dataset.type === 'FIXED').length;

    const activeNode = document.getElementById('activeCouponsCount');
    const percentNode = document.getElementById('percentCouponsCount');
    const fixedNode = document.getElementById('fixedCouponsCount');

    if (activeNode) activeNode.textContent = String(activeCount);
    if (percentNode) percentNode.textContent = String(percentCount);
    if (fixedNode) fixedNode.textContent = String(fixedCount);

    window.AdminEntity?.confirmLinks('.delete-link', (link) => `Supprimer le coupon ${link.dataset.name} ?`);
});
