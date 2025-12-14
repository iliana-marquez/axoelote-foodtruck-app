// =========================================
//   BOOKING FORM JAVASCRIPT
//   Configurable for Create and Edit modes
//   IMPORTANT: Business rules come from data attributes set by Django.
// =========================================

console.log('=== booking_form.js loaded ===');

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('inline_calendar');
    if (!calendarEl) return;
    
    if (typeof flatpickr === 'undefined') {
        console.error('Flatpickr not loaded!');
        return;
    }
    
    const minAdvanceDays = parseInt(calendarEl.dataset.minAdvanceDays);
    if (isNaN(minAdvanceDays)) {
        console.error('data-min-advance-days is required');
        return;
    }
    
    // ==========================================================================
    // ELEMENTS
    // ==========================================================================
    const elements = {
        availabilityStatus: document.getElementById('availability_status'),
        timeFields: document.getElementById('time_fields'),
        startTimeSelect: document.getElementById('start_time'),
        endTimeSelect: document.getElementById('end_time'),
        endsNextDayCheckbox: document.getElementById('ends_next_day'),
        nextDayWrapper: document.getElementById('next_day_wrapper'),
        bookingSummary: document.getElementById('booking_summary'),
        summaryText: document.getElementById('summary_text'),
        durationText: document.getElementById('duration_text'),
        detailsSection: document.getElementById('details_section'),
        startDatetimeHidden: document.getElementById('id_start_datetime'),
        endDatetimeHidden: document.getElementById('id_end_datetime')
    };
    
    // ==========================================================================
    // STATE
    // ==========================================================================
    let state = {
        selectedDate: null,
        currentSlot: null
    };
    
    // ==========================================================================
    // CALENDAR SETUP
    // ==========================================================================
    calendarEl.classList.remove('d-none');
    
    const minDate = new Date();
    minDate.setDate(minDate.getDate() + minAdvanceDays);
    
    const calendar = flatpickr(calendarEl, {
        inline: true,
        mode: 'single',  // Required for onChange to receive selectedDates
        dateFormat: 'd.m.Y',
        minDate: minDate,
        locale: {
            firstDayOfWeek: 1
        },
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length === 0) return;
            
            const clickedDate = selectedDates[0];
            const year = clickedDate.getFullYear();
            const month = String(clickedDate.getMonth() + 1).padStart(2, '0');
            const day = String(clickedDate.getDate()).padStart(2, '0');
            const apiDate = `${year}-${month}-${day}`;
            
            console.log('=== Date selected:', dateStr, '| API:', apiDate);
            
            state.selectedDate = clickedDate;
            
            showLoading();
            checkAvailability(apiDate);
        }
    });

    // ==========================================================================
    // TIME SELECTION LISTENERS
    // ==========================================================================
    elements.startTimeSelect.addEventListener('change', updateSummary);
    elements.endTimeSelect.addEventListener('change', updateSummary);
    elements.endsNextDayCheckbox.addEventListener('change', updateSummary);

    // ==========================================================================
    // API FUNCTIONS
    // ==========================================================================
    function checkAvailability(apiDate) {
        fetch(`/booking/slots/${apiDate}/`)
            .then(response => response.json())
            .then(data => {
                console.log('=== API response:', data);
                
                if (data.success && data.has_availability) {
                    showAvailable(data.slots[0]);
                } else if (data.success && !data.has_availability) {
                    showFullyBooked();
                } else {
                    showError(data.error || 'Error checking availability');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                showError('Connection error. Please try again.');
            });
    }
    
    // ==========================================================================
    // UI FUNCTIONS
    // ==========================================================================
    function showLoading() {
        elements.availabilityStatus.innerHTML = `
            <span class="text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Checking availability...
            </span>`;
        elements.timeFields.style.display = 'none';
        elements.bookingSummary.style.display = 'none';
        elements.detailsSection.style.display = 'none';
    }
    
    function showAvailable(slot) {
        state.currentSlot = slot;
        
        const windowEnd = slot.end_date
            ? `${slot.end_time} (next day)`
            : slot.end_time;
        
        elements.availabilityStatus.innerHTML = `
            <div class="text-success">
                <i class="bi bi-check-circle-fill me-2"></i>
                <strong>Available!</strong>
            </div>
            <small class="text-muted d-block mt-1">
                Window: ${slot.start_time} - ${windowEnd}
            </small>`;
        
        populateTimeOptions(slot);
        
        elements.timeFields.style.display = 'block';
        
        if (slot.crosses_midnight) {
            elements.nextDayWrapper.style.display = 'block';
        } else {
            elements.nextDayWrapper.style.display = 'none';
            elements.endsNextDayCheckbox.checked = false;
        }
    }
    
    function showFullyBooked() {
        state.currentSlot = null;
        
        elements.availabilityStatus.innerHTML = `
            <div class="text-danger">
                <i class="bi bi-x-circle-fill me-2"></i>
                <strong>Fully booked</strong>
            </div>
            <small class="text-muted d-block mt-1">
                Please select another date
            </small>`;
        
        elements.timeFields.style.display = 'none';
        elements.bookingSummary.style.display = 'none';
        elements.detailsSection.style.display = 'none';
    }
    
    function showError(message) {
        elements.availabilityStatus.innerHTML = `
            <div class="text-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                ${message}
            </div>`;
        
        elements.timeFields.style.display = 'none';
        elements.bookingSummary.style.display = 'none';
        elements.detailsSection.style.display = 'none';
    }
    
    // ==========================================================================
    // TIME FUNCTIONS
    // ==========================================================================
    function generateTimeOptions() {
        const times = [];
        for (let h = 0; h < 24; h++) {
            for (let m = 0; m < 60; m += 30) {
                const hour = String(h).padStart(2, '0');
                const min = String(m).padStart(2, '0');
                times.push(`${hour}:${min}`);
            }
        }
        return times;
    }
    
    function populateTimeOptions(slot) {
        const times = generateTimeOptions();
        
        elements.startTimeSelect.innerHTML = '<option value="">Select start time</option>';
        times.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            elements.startTimeSelect.appendChild(option);
        });
        
        if (times.includes(slot.start_time)) {
            elements.startTimeSelect.value = slot.start_time;
        }
        
        elements.endTimeSelect.innerHTML = '<option value="">Select end time</option>';
        times.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            elements.endTimeSelect.appendChild(option);
        });
        
        updateSummary();
    }
    
    function updateSummary() {
        const startTime = elements.startTimeSelect.value;
        const endTime = elements.endTimeSelect.value;
        
        if (!state.selectedDate || !startTime || !endTime) {
            elements.bookingSummary.style.display = 'none';
            elements.detailsSection.style.display = 'none';
            elements.startDatetimeHidden.value = '';
            elements.endDatetimeHidden.value = '';
            return;
        }
        
        const endsNextDay = elements.endsNextDayCheckbox.checked;
        
        const startDate = new Date(state.selectedDate);
        const endDate = new Date(state.selectedDate);
        if (endsNextDay) {
            endDate.setDate(endDate.getDate() + 1);
        }
        
        const [startH, startM] = startTime.split(':');
        const [endH, endM] = endTime.split(':');
        startDate.setHours(parseInt(startH), parseInt(startM), 0, 0);
        endDate.setHours(parseInt(endH), parseInt(endM), 0, 0);
        
        if (endDate <= startDate) {
            elements.bookingSummary.innerHTML = `
                <div class="text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    End time must be after start time
                </div>`;
            elements.bookingSummary.style.display = 'block';
            elements.detailsSection.style.display = 'none';
            elements.startDatetimeHidden.value = '';
            elements.endDatetimeHidden.value = '';
            return;
        }
        
        const diffMs = endDate - startDate;
        const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        
        let duration = `${diffHrs}h`;
        if (diffMins > 0) duration += ` ${diffMins}m`;
        
        const displayDate = state.selectedDate.toLocaleDateString('de-AT', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        
        let summary = `${startTime} - ${endTime}`;
        if (endsNextDay) summary += ' (next day)';
        summary += ` on ${displayDate}`;
        
        elements.bookingSummary.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>
                    <i class="bi bi-check-circle text-success me-2"></i>
                    ${summary}
                </span>
                <strong>${duration}</strong>
            </div>`;
        elements.bookingSummary.style.display = 'block';
        elements.detailsSection.style.display = 'block';
        
        elements.startDatetimeHidden.value = formatForBackend(startDate);
        elements.endDatetimeHidden.value = formatForBackend(endDate);
        
        console.log('=== Form values:', {
            start: elements.startDatetimeHidden.value,
            end: elements.endDatetimeHidden.value
        });
    }
    
    function formatForBackend(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const mins = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${mins}`;
    }
    
    console.log('=== Booking form ready ===');
});