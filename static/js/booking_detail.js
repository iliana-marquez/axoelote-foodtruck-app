// =========================================
//   BOOKING DETAIL JAVASCRIPT
//   Inline editing with section toggles
// =========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Booking detail JS loaded');
    
    // =====================
    // Section Toggle
    // =====================
    const toggleBtns = document.querySelectorAll('.toggle-edit-btn');
    const cancelBtns = document.querySelectorAll('.toggle-cancel-btn');
    const saveSection = document.getElementById('save_section');

    // Track wich sections are being edited
    let activeSections = new Set();

    // Toggle button click → Show edit section
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            console.log('Edit clicked:', section);
            showEditSection(section);
            this.style.display = 'none';
        });
    });
    
    // Cancel button click → Hide edit section
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            console.log('Cancel clicked:', section);
            hideEditSection(section);
        });
    });

    function showEditSection(section) {
        const display = document.getElementById(`${section}_display`);
        const edit = document.getElementById(`${section}_edit`);
        
        if (display) display.style.display = 'none';
        if (edit) edit.style.display = 'block';
        
        activeSections.add(section);
        updateSaveButton();
    }
    
    function hideEditSection(section) {
        const display = document.getElementById(`${section}_display`);
        const edit = document.getElementById(`${section}_edit`);
        const toggleBtn = document.querySelector(`.toggle-edit-btn[data-section="${section}"]`);
        
        if (display) display.style.display = 'block';
        if (edit) edit.style.display = 'none';
        if (toggleBtn) toggleBtn.style.display = 'inline-block';
        
        activeSections.delete(section);
        updateSaveButton();
    }
    
    function updateSaveButton() {
        if (saveSection) {
            const hasEdits = activeSections.size > 0;
            saveSection.style.display = hasEdits ? 'flex' : 'none';
            console.log('Active sections:', activeSections.size, 'Show save:', hasEdits);
        }
    }

    // ==================
    // Date/Time Section
    // ==================
    const calendarEl = document.getElementById('inline_calendar');
    if (!calendarEl) return;
    
    const config = {
        bookingId: calendarEl.dataset.excludeBookingId,
        minAdvanceDays: parseInt(calendarEl.dataset.minAdvanceDays) || 15,
        preselectedDate: calendarEl.dataset.preselectedDate,
        preselectedStartTime: calendarEl.dataset.preselectedStartTime,
        preselectedEndTime: calendarEl.dataset.preselectedEndTime,
        slotsApiUrl: '/booking/slots/'
    };
    
    const elements = {
        // Display
        currentDisplay: document.getElementById('current_datetime_display'),
        displayDate: document.getElementById('display_date'),
        displayTime: document.getElementById('display_time'),
        displayDuration: document.getElementById('display_duration'),
        // Edit section
        editSection: document.getElementById('datetime_edit_section'),
        toggleBtn: document.getElementById('toggle_datetime_edit'),
        cancelBtn: document.getElementById('cancel_datetime_edit'),
        applyBtn: document.getElementById('apply_datetime_change'),
        // Form elements
        availabilityStatus: document.getElementById('availability_status'),
        timeFields: document.getElementById('time_fields'),
        startTimeSelect: document.getElementById('start_time'),
        endTimeSelect: document.getElementById('end_time'),
        nextDayWrapper: document.getElementById('next_day_wrapper'),
        nextDayCheckbox: document.getElementById('ends_next_day'),
        // Preview
        newSelectionPreview: document.getElementById('new_selection_preview'),
        previewDate: document.getElementById('preview_date'),
        previewTime: document.getElementById('preview_time'),
        previewDuration: document.getElementById('preview_duration'),
        // Error
        timeError: document.getElementById('time_error'),
        // Hidden fields
        hiddenStartDatetime: document.getElementById('id_start_datetime'),
        hiddenEndDatetime: document.getElementById('id_end_datetime')
    };
    
    let state = {
        originalDate: config.preselectedDate,
        originalStartTime: config.preselectedStartTime,
        originalEndTime: config.preselectedEndTime,
        appliedDate: config.preselectedDate,
        appliedStartTime: config.preselectedStartTime,
        appliedEndTime: config.preselectedEndTime,
        selectedDate: null,
        selectedStartTime: null,
        selectedEndTime: null,
        endsNextDay: false,
        availableSlots: [],
        calendar: null
    };
    
    let dateTimeChanged = false;
    
    // Initialize display duration
    updateMainDisplay();
    
    // Toggle handlers
    if (elements.toggleBtn) {
        elements.toggleBtn.addEventListener('click', showDateTimeEdit);
    }
    if (elements.cancelBtn) {
        elements.cancelBtn.addEventListener('click', hideDateTimeEdit);
    }
    if (elements.applyBtn) {
        elements.applyBtn.addEventListener('click', applyDateTimeChange);
    }
    if (elements.startTimeSelect) {
        elements.startTimeSelect.addEventListener('change', onTimeChange);
    }
    if (elements.endTimeSelect) {
        elements.endTimeSelect.addEventListener('change', onTimeChange);
    }
    if (elements.nextDayCheckbox) {
        elements.nextDayCheckbox.addEventListener('change', onTimeChange);
    }
    
    function updateMainDisplay() {
        if (!elements.displayDate) return;
        
        const dateObj = new Date(state.appliedDate);
        const dateStr = dateObj.toLocaleDateString('en-GB', {
            weekday: 'long',
            day: '2-digit',
            month: 'long',
            year: 'numeric'
        });
        
        elements.displayDate.textContent = dateStr;
        elements.displayTime.textContent = `${state.appliedStartTime} - ${state.appliedEndTime}`;
        
        const duration = calculateDuration(state.appliedStartTime, state.appliedEndTime, false);
        elements.displayDuration.textContent = `(${duration})`;
    }
    
    function showDateTimeEdit() {
        elements.editSection.style.display = 'block';
        elements.toggleBtn.style.display = 'none';
        
        state.selectedDate = state.appliedDate;
        state.selectedStartTime = null;
        state.selectedEndTime = null;
        
        if (!state.calendar) {
            initCalendar();
        }
        
        fetchAvailableSlots(state.appliedDate);
    }
    
    function hideDateTimeEdit() {
        elements.editSection.style.display = 'none';
        elements.toggleBtn.style.display = 'inline-block';
        
        elements.newSelectionPreview.style.display = 'none';
        elements.timeError.style.display = 'none';
        elements.applyBtn.disabled = true;
    }
    
    function applyDateTimeChange() {
        state.appliedDate = state.selectedDate;
        state.appliedStartTime = state.selectedStartTime;
        state.appliedEndTime = state.selectedEndTime;
        
        updateHiddenFields();
        updateMainDisplay();
        
        dateTimeChanged = true;
        updateSaveButton();
        
        hideDateTimeEdit();
    }
    
    function updateHiddenFields() {
        const startDatetime = `${state.appliedDate}T${state.appliedStartTime}`;
        
        let endDate = state.appliedDate;
        if (state.endsNextDay) {
            const nextDay = new Date(state.appliedDate);
            nextDay.setDate(nextDay.getDate() + 1);
            endDate = nextDay.toISOString().split('T')[0];
        }
        const endDatetime = `${endDate}T${state.appliedEndTime}`;
        
        elements.hiddenStartDatetime.value = startDatetime;
        elements.hiddenEndDatetime.value = endDatetime;
    }
    
    function initCalendar() {
        const minDate = new Date();
        minDate.setDate(minDate.getDate() + config.minAdvanceDays);
        
        state.calendar = flatpickr(calendarEl, {
            inline: true,
            mode: 'single',
            dateFormat: 'Y-m-d',
            minDate: minDate,
            defaultDate: state.appliedDate,
            onChange: function(selectedDates, dateStr) {
                if (dateStr) {
                    state.selectedDate = dateStr;
                    state.selectedStartTime = null;
                    state.selectedEndTime = null;
                    elements.applyBtn.disabled = true;
                    elements.newSelectionPreview.style.display = 'none';
                    fetchAvailableSlots(dateStr);
                }
            }
        });
    }
    
    function fetchAvailableSlots(dateStr) {
        elements.availabilityStatus.innerHTML = `
            <span class="text-muted">
                <i class="bi bi-hourglass-split me-1"></i>
                Checking availability...
            </span>
        `;
        elements.timeFields.style.display = 'none';
        elements.timeError.style.display = 'none';
        
        const url = `${config.slotsApiUrl}${dateStr}/?exclude=${config.bookingId}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    state.availableSlots = data.slots || [];
                    handleSlotsResponse(data, dateStr);
                } else {
                    showError(data.error || 'Unable to check availability');
                }
            })
            .catch(error => {
                console.error('Slot check error:', error);
                showError('Unable to check availability. Please try again.');
            });
    }
    
    function handleSlotsResponse(data, dateStr) {
        if (data.has_availability && state.availableSlots.length > 0) {
            elements.availabilityStatus.innerHTML = `
                <span class="text-success">
                    <i class="bi bi-check-circle me-1"></i>
                    ${state.availableSlots.length} slot${state.availableSlots.length > 1 ? 's' : ''} available
                </span>
            `;
            
            populateTimeDropdowns();
            elements.timeFields.style.display = 'block';
            
            if (dateStr === state.appliedDate) {
                preselectCurrentTimes();
            }
        } else {
            elements.availabilityStatus.innerHTML = `
                <span class="text-danger">
                    <i class="bi bi-x-circle me-1"></i>
                    No availability on this date
                </span>
            `;
            elements.timeFields.style.display = 'none';
        }
    }
    
    function populateTimeDropdowns() {
        elements.startTimeSelect.innerHTML = '<option value="">Select start time</option>';
        elements.endTimeSelect.innerHTML = '<option value="">Select end time</option>';
        
        const times = new Set();
        
        state.availableSlots.forEach(slot => {
            let currentTime = slot.start;
            while (currentTime <= slot.end) {
                times.add(currentTime);
                currentTime = addMinutes(currentTime, 30);
            }
        });
        
        Array.from(times).sort().forEach(time => {
            elements.startTimeSelect.innerHTML += `<option value="${time}">${time}</option>`;
            elements.endTimeSelect.innerHTML += `<option value="${time}">${time}</option>`;
        });
    }
    
    function addMinutes(timeStr, minutes) {
        const [h, m] = timeStr.split(':').map(Number);
        const totalMinutes = h * 60 + m + minutes;
        const newH = Math.floor(totalMinutes / 60) % 24;
        const newM = totalMinutes % 60;
        return `${newH.toString().padStart(2, '0')}:${newM.toString().padStart(2, '0')}`;
    }
    
    function preselectCurrentTimes() {
        const startOptions = Array.from(elements.startTimeSelect.options).map(o => o.value);
        const endOptions = Array.from(elements.endTimeSelect.options).map(o => o.value);
        
        if (startOptions.includes(state.appliedStartTime)) {
            elements.startTimeSelect.value = state.appliedStartTime;
            state.selectedStartTime = state.appliedStartTime;
        }
        if (endOptions.includes(state.appliedEndTime)) {
            elements.endTimeSelect.value = state.appliedEndTime;
            state.selectedEndTime = state.appliedEndTime;
        }
        
        if (state.selectedStartTime && state.selectedEndTime) {
            updatePreview();
        }
    }
    
    function onTimeChange() {
        state.selectedStartTime = elements.startTimeSelect.value;
        state.selectedEndTime = elements.endTimeSelect.value;
        state.endsNextDay = elements.nextDayCheckbox.checked;
        
        if (!state.selectedStartTime || !state.selectedEndTime) {
            elements.newSelectionPreview.style.display = 'none';
            elements.applyBtn.disabled = true;
            return;
        }
        
        if (state.selectedEndTime <= state.selectedStartTime && !state.endsNextDay) {
            elements.nextDayWrapper.style.display = 'block';
        } else {
            elements.nextDayWrapper.style.display = 'none';
        }
        
        elements.timeError.style.display = 'none';
        updatePreview();
    }
    
    function updatePreview() {
        if (!state.selectedDate || !state.selectedStartTime || !state.selectedEndTime) {
            return;
        }
        
        const dateObj = new Date(state.selectedDate);
        const dateStr = dateObj.toLocaleDateString('en-GB', {
            weekday: 'short',
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
        
        let timeStr = `${state.selectedStartTime} - ${state.selectedEndTime}`;
        if (state.endsNextDay) {
            timeStr += ' (next day)';
        }
        
        const duration = calculateDuration(state.selectedStartTime, state.selectedEndTime, state.endsNextDay);
        
        elements.previewDate.textContent = dateStr;
        elements.previewTime.textContent = timeStr;
        elements.previewDuration.textContent = duration;
        elements.newSelectionPreview.style.display = 'block';
        elements.applyBtn.disabled = false;
    }
    
    function calculateDuration(startTime, endTime, endsNextDay) {
        const [startH, startM] = startTime.split(':').map(Number);
        const [endH, endM] = endTime.split(':').map(Number);
        
        let startMinutes = startH * 60 + startM;
        let endMinutes = endH * 60 + endM;
        
        if (endsNextDay || endMinutes <= startMinutes) {
            endMinutes += 24 * 60;
        }
        
        const totalMinutes = endMinutes - startMinutes;
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        return minutes === 0 ? `${hours}h` : `${hours}h ${minutes}m`;
    }
    
    function showError(message) {
        elements.timeError.textContent = message;
        elements.timeError.style.display = 'block';
        elements.applyBtn.disabled = true;
    }
});