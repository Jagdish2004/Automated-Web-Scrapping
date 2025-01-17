function showDetails(name, description) {
    const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
    document.getElementById('modalLeadName').textContent = name;
    document.getElementById('modalLeadDescription').textContent = description || 'No description available';
    modal.show();
}

// Add DataTable functionality
document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('leadsTable');
    if (table) {
        new DataTable(table, {
            pageLength: 10,
            order: [[0, 'asc']],
            responsive: true
        });
    }
});

// Export table to CSV
function exportTableToCSV() {
    const table = document.getElementById('leadsTable');
    const rows = table.getElementsByTagName('tr');
    const csvContent = [];
    
    // Get headers
    const headers = [];
    for (const cell of rows[0].getElementsByTagName('th')) {
        headers.push(cell.textContent);
    }
    csvContent.push(headers.join(','));
    
    // Get data
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const data = [];
        for (const cell of row.getElementsByTagName('td')) {
            data.push(`"${cell.textContent.trim()}"`);
        }
        csvContent.push(data.join(','));
    }
    
    // Download CSV
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'leads_export.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
} 