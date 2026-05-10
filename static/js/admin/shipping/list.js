document.addEventListener('DOMContentLoaded', () => {
    const table = window.AdminEntity?.initFilterableTable({
        rowSelector: '#shippingTableBody tr[data-search]',
        pageSize: 10,
        emptyStateId: 'emptyState',
    });

    if (!table) return;

    const rows = table.rows;
    const activeCount = rows.filter((row) => row.dataset.status === 'active').length;
    const freeCount = rows.filter((row) => row.dataset.freeEligible === 'yes').length;
    const avgFee = rows.length
        ? (rows.reduce((sum, row) => sum + parseFloat(row.dataset.fee || '0'), 0) / rows.length).toFixed(2)
        : '0.00';

    const activeNode = document.getElementById('activeZonesCount');
    const freeNode = document.getElementById('freeZonesCount');
    const avgNode = document.getElementById('avgFeeCount');

    if (activeNode) activeNode.textContent = String(activeCount);
    if (freeNode) freeNode.textContent = String(freeCount);
    if (avgNode) avgNode.textContent = avgFee;

    window.AdminEntity?.confirmLinks('.delete-link', (link) => `Supprimer la zone ${link.dataset.name} ?`);
});
