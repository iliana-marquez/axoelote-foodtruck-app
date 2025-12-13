// =========================================
//   BOOKING FORM JAVASCRIPT
//   Configurable for Create and Edit models
//   IMPORTANT: Business rules come from data attributes set by Django.
// =========================================

console.log('=== booking_form.js loaded ===');

document.addEventListener('DOMContentLoaded', function() {
    // =========================================
    // Check if on booking form page
    // =========================================
    const calendarEl = document.getElementById('inline_calendar');
    if (!calendarEl) return; // exit if no booking form page

    // =========================================
    // CONFIGURATION (form data attributes)
    // =========================================
    const config = {
        mode: calendarEl.dataset.mode || 'create',
        minAdvanceDays: parseInt(calendarEl.dataset.minAdvanceDays),
        excludeBookingId: calendarEl.dataset.excludeBookingId || null,
        preselectedDate: calendarEl.dataset.preselectedDate || null,
        preselectedStartTime: calendarEl.dataset.preselectedStartTime || null,
        preselectedEndTime: calendarEl.dataset.preselectedEndTime || null,
        preselectedNextDay: calendarEl.dataset.preselectedNextDay === 'true',
        slotsApiUrl: '/booking/slots/'
    };

    // Validate required configuration
    if (isNaN(config.minAdvanceDays)) {
        console.error('Booking form error: data-min-advance-days attribute is required');
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
        timeError: document.getElementById('time_error'),
        clearBtn: document.getElementById('clear_when'),
        detailsSection: document.getElementById('details_section'),
        startDatetimeHidden: document.getElementById('id_start_datetime'),
        endDatetimeHidden: document.getElementById('id_end_datetime'),
        eventTypeField: document.getElementById('id_event_type'),
        descriptionField: document.getElementById('description_field')
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
    const minDate = new Date();
    minDate.setDate(minDate.getDate() + config.minAdvanceDays);

    const calendarOptions = {
        inline: true,
        dateFormat: 'd.m.Y',
        minDate: config.mode === 'edit' ? null : minDate,
        locale: {
            firstDayOfWeek: 1
        },
        onChange: function(selectedDates, dateStr, instance) {
            console.log('Calendar clicked!');
            console.log('selectedDates:', selectedDates);
            console.log('dateStr:', dateStr);
            if (selectedDates.length > 0) {
                state.selectedDate = selectedDates[0];
                const apiDate = instance.formatDate(selectedDates[0], 'Y-m-d');
                checkAvailability(apiDate, dateStr);
            }
        }
    };

    if (config.preselectedDate) {
        calendarOptions.defaultDate = config.preselectedDate;
    }

    const calendar = flatpickr('#inline_calendar', calendarOptions);

    // ==========================================================================
    // EDIT MODE INITIALIZATION
    // ==========================================================================
    if (config.mode === 'edit' && config.preselectedDate) {
        const apiDate = config.preselectedDate;
        const displayDate = calendar.formatDate(new Date(config.preselectedDate), 'd.m.Y');
        state.selectedDate = new Date(config.preselectedDate);
        checkAvailability(apiDate, displayDate, true);
    }

    // ==========================================================================
    // EVENT LISTENERS
    // ==========================================================================
    elements.clearBtn.addEventListener('click', function() {
        calendar.clear();
        resetForm();
    });

    elements.startTimeSelect.addEventListener('change', populateEndTimes);
    elements.endTimeSelect.addEventListener('change', updateSummary);
    elements.endsNextDayCheckbox.addEventListener('change', updateSummary);

    if (elements.eventTypeField) {
        elements.eventTypeField.addEventListener('change', toggleDescription);
        toggleDescription();
    }

    // ==========================================================================
    // API FUNCTIONS
    // ==========================================================================
    function checkAvailability(apiDate, displayDate, isInitialLoad = false) {
        console.log('checkAvailability called with:', apiDate);
        elements.availabilityStatus.innerHTML = `
            <span class="text-muted">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Checking availability...
            </span>`;
        
        if (!isInitialLoad) {
            elements.timeFields.style.display = 'none';
            elements.bookingSummary.style.display = 'none';
            elements.detailsSection.style.display = 'none';
        }

        let apiUrl = `${config.slotsApiUrl}${apiDate}/`;
        if (config.excludeBookingId) {
            apiUrl += `?exclude=${config.excludeBookingId}`;
        }

        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.has_availability) {
                    showAvailable(data.slots[0], displayDate, isInitialLoad);
                } else if (data.success && !data.has_availability) {
                    showFullyBooked();
                } else {
                    showError(data.error || 'Error checking availability');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Connection error. Please try again.');
            });
    }

    // ==========================================================================
    // AVAILABILITY DISPLAY
    // ==========================================================================
    function showAvailable(slot, displayDate, isInitialLoad = false) {
        state.currentSlot = slot;

        const windowEnd = slot.end_date
            ? `${slot.end_time} (next day)`
            : slot.end_time;

        elements.availabilityStatus.innerHTML = `
            <div class="slot-available">
                <i class="bi bi-check-circle-fill me-2"></i>
                <strong>Available!</strong>
            </div>
            <small class="text-muted d-block mt-1">
                Window: ${slot.start_time} - ${windowEnd}
            </small>`;

        populateTimeOptions(slot, isInitialLoad);
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
            <div class="slot-unavailable">
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
    }

    // ==========================================================================
    // TIME OPTIONS
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

    function populateTimeOptions(slot, isInitialLoad = false) {
        const times = generateTimeOptions();

        elements.startTimeSelect.innerHTML = '<option value="">Select start time</option>';
        times.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            elements.startTimeSelect.appendChild(option);
        });

        if (isInitialLoad && config.preselectedStartTime) {
            elements.startTimeSelect.value = config.preselectedStartTime;
        } else if (times.includes(slot.start_time)) {
            elements.startTimeSelect.value = slot.start_time;
        }

        populateEndTimes(isInitialLoad);
    }

    function populateEndTimes(isInitialLoad = false) {
        const times = generateTimeOptions();

        elements.endTimeSelect.innerHTML = '<option value="">Select end time</option>';
        times.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            elements.endTimeSelect.appendChild(option);
        });

        if (isInitialLoad && config.preselectedEndTime) {
            elements.endTimeSelect.value = config.preselectedEndTime;
            elements.endsNextDayCheckbox.checked = config.preselectedNextDay;
        }

        updateSummary();
    }

    // ==========================================================================
    // SUMMARY & VALIDATION
    // ==========================================================================
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
            const hint = !endsNextDay && endTime < startTime
                ? ' Check "Ends next day" for overnight events.'
                : '';
            elements.timeError.innerHTML = `
                <i class="bi bi-exclamation-triangle me-2"></i>
                End time must be after start time.${hint}`;
            elements.timeError.style.display = 'block';
            elements.bookingSummary.style.display = 'none';
            elements.detailsSection.style.display = 'none';
            elements.startDatetimeHidden.value = '';
            elements.endDatetimeHidden.value = '';
            return;
        }

        const validation = validateWithinSlot(startDate, endDate);
        if (!validation.valid) {
            elements.timeError.innerHTML = `
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${validation.message}`;
            elements.timeError.style.display = 'block';
            elements.bookingSummary.style.display = 'none';
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

        const dateOptions = { day: '2-digit', month: '2-digit', year: 'numeric' };
        const displayDateStr = state.selectedDate.toLocaleDateString('de-AT', dateOptions);

        let summary = `${startTime} - ${endTime}`;
        if (endsNextDay) summary += ' (next day)';
        summary += ` on ${displayDateStr}`;

        elements.summaryText.textContent = summary;
        elements.durationText.textContent = duration;

        elements.timeError.style.display = 'none';
        elements.bookingSummary.style.display = 'block';
        elements.detailsSection.style.display = 'block';

        elements.startDatetimeHidden.value = formatForBackend(startDate);
        elements.endDatetimeHidden.value = formatForBackend(endDate);
    }

    function validateWithinSlot(startDate, endDate) {
        if (!state.currentSlot) return { valid: false, message: 'No slot selected' };

        const slotStart = parseSlotDateTime(state.currentSlot.start_date, state.currentSlot.start_time);
        const slotEnd = parseSlotDateTime(
            state.currentSlot.end_date || state.currentSlot.start_date,
            state.currentSlot.end_time
        );

        if (startDate < slotStart) {
            return {
                valid: false,
                message: `Start time cannot be before ${state.currentSlot.start_time}`
            };
        }

        if (endDate > slotEnd) {
            const endTimeStr = state.currentSlot.end_date
                ? `${state.currentSlot.end_time} (next day)`
                : state.currentSlot.end_time;
            return {
                valid: false,
                message: `End time cannot be after ${endTimeStr}`
            };
        }

        return { valid: true };
    }

    // ==========================================================================
    // UTILITIES
    // ==========================================================================
    function parseSlotDateTime(dateStr, timeStr) {
        const [day, month, year] = dateStr.split('.');
        const [hours, mins] = timeStr.split(':');
        return new Date(year, month - 1, day, hours, mins);
    }

    function formatForBackend(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const mins = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${mins}`;
    }

    function resetForm() {
        state.selectedDate = null;
        state.currentSlot = null;
        elements.availabilityStatus.innerHTML = `
            <span class="text-muted">
                <i class="bi bi-arrow-left-circle"></i>
                Select a date to check availability
            </span>`;
        elements.timeFields.style.display = 'none';
        elements.bookingSummary.style.display = 'none';
        elements.timeError.style.display = 'none';
        elements.detailsSection.style.display = 'none';
        elements.startDatetimeHidden.value = '';
        elements.endDatetimeHidden.value = '';
    }

    function toggleDescription() {
        if (elements.eventTypeField && elements.descriptionField) {
            elements.descriptionField.style.display = 
                elements.eventTypeField.value === 'open' ? 'block' : 'none';
        }
    }
});