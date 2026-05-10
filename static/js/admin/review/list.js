document.addEventListener('DOMContentLoaded', () => {
    const table = window.AdminEntity?.initFilterableTable({
        rowSelector: '#reviewsTableBody tr[data-search]',
        pageSize: 10,
        emptyStateId: 'emptyState',
    });

    if (!table) return;

    const rows = table.rows;
    const approvedCount = rows.filter((row) => row.dataset.status === 'approved').length;
    const verifiedCount = rows.filter((row) => row.dataset.verified === 'yes').length;
    const averageRating = rows.length
        ? (rows.reduce((sum, row) => sum + parseFloat(row.dataset.rating || '0'), 0) / rows.length).toFixed(1)
        : '0.0';

    const approvedNode = document.getElementById('approvedReviewsCount');
    const verifiedNode = document.getElementById('verifiedReviewsCount');
    const ratingNode = document.getElementById('averageRatingCount');

    if (approvedNode) approvedNode.textContent = String(approvedCount);
    if (verifiedNode) verifiedNode.textContent = String(verifiedCount);
    if (ratingNode) ratingNode.textContent = averageRating;

    window.AdminEntity?.confirmLinks('.delete-link', (link) => `Supprimer l'avis de ${link.dataset.name} ?`);
});
