document.addEventListener('DOMContentLoaded', () => {
    const table = window.AdminEntity?.initFilterableTable({
        rowSelector: '#ordersTableBody tr[data-search]',
        pageSize: 10,
        emptyStateId: 'emptyState',
    });

    if (!table) return;

    const rows = table.rows;
    const pendingCount = rows.filter((row) => row.dataset.status === 'PENDING').length;
    const deliveredCount = rows.filter((row) => row.dataset.status === 'DELIVERED').length;
    const revenue = rows.reduce((sum, row) => sum + parseFloat(row.dataset.total || '0'), 0).toFixed(2);

    const pendingNode = document.getElementById('pendingOrdersCount');
    const deliveredNode = document.getElementById('deliveredOrdersCount');
    const revenueNode = document.getElementById('ordersRevenueCount');

    if (pendingNode) pendingNode.textContent = String(pendingCount);
    if (deliveredNode) deliveredNode.textContent = String(deliveredCount);
    if (revenueNode) revenueNode.textContent = revenue;
});
