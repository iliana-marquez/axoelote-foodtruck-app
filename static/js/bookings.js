// =========================================
//   BOOKINGS LIST JAVASCRIPT
//   Tab filtering for bookings table
// =========================================

document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('#bookingTabs button');
    const rows = document.querySelectorAll('.booking-row');
    
    if (!tabs.length || !rows.length) return;
    
    const today = new Date().toISOString().split('T')[0];
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            rows.forEach(row => {
                const status = row.dataset.status;
                const date = row.dataset.date;
                let show = false;
                
                switch(filter) {
                    case 'all':
                        show = true;
                        break;
                    case 'pending':
                        show = status === 'pending';
                        break;
                    case 'approved':
                        show = status === 'approved';
                        break;
                    case 'active':
                        show = status === 'approved' && date >= today;
                        break;
                    case 'past':
                        show = date < today;
                        break;
                }
                
                row.style.display = show ? '' : 'none';
            });
        });
    });
});