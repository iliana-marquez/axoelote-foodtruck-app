# Axoelote Food Truck Webapp

**The Problem:** Food trucks face a daily challenge - customers arrive at yesterday's location to find an empty parking spot. Meanwhile, owners juggle phone calls for private event bookings while trying to update social media with today's location.

**The Solution:** A Django-based web application for managing a mobile food truck business, featuring customer booking requests, event management, and dynamic schedule display.

**The Result:**
Axoelote Food Truck [Webapp Live](https://axoelote-foodtruck-6de5775aa776.herokuapp.com/)
![Axolote Website Screenshot](https://res.cloudinary.com/dj2lk9daf/image/upload/v1757932902/axoelote-website_u9k5v5.png)

**Technical highlights:** User authentication, full CRUD operations with user feedback, automated testing, responsive design, and cloud deployment.

## Table of Contents

- [Project Overview](#project-overview)
  - [User Stories](#user-stories)
  - [Key Features](#key-features)
- [UX Design](#ux-design)
  - [Wireframes](#wireframes)
  - [Design Decisions](#design-decisions)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
  - [Entity Relationship Diagram](#entity-relationship-diagram)
  - [Model Relationships](#model-relationships)
  - [Booking Model](#booking-model)
  - [Event Model](#event-model)
  - [RegularSchedule Model](#regularschedule-model)
- [Features](#features)
  - [CRUD Operations](#crud-operations)
  - [Booking Management System](#booking-management-system)
  - [Slot Availability System](#slot-availability-system)
  - [Authentication & Authorization](#authentication--authorization)
- [Business Rules](#business-rules)
- [Development Process](#development-process)
  - [Agile Methodology](#agile-methodology)
  - [Architecture Decisions](#architecture-decisions)
- [Testing](#testing)
  - [User Story Testing](#user-story-testing)
  - [Automated Testing](#automated-testing)
  - [Validation](#validation)
- [Bug Fixes](#bug-fixes)
- [Known Issues](#known-issues)
- [Deployment](#deployment)
  - [Heroku Deployment Steps](#heroku-deployment-steps)
  - [Local Development](#local-development)
- [Future Enhancements](#future-enhancements)
- [Usage Instructions](#usage-instructions)
- [Acknowledgements](#acknowledgements)
- [Key Takeaways](#key-takeaways)

## Project Overview

### User Stories

User stories were managed using GitHub Projects: [GitHub Project Board](https://github.com/users/iliana-marquez/projects/13/views/1)

As a **customer**, I want:
- To easily see where the food truck will be today, so I don't go to the wrong location
- To book the food truck for my private event, providing details such as date, time, and number of guests
- To know the booking rules (minimum guests, advance notice) so I understand requirements before submitting
- To view and manage my bookings with the ability to edit or cancel them
- To see real-time availability when selecting dates for my booking
- To log in securely so I can manage my bookings

As an **admin/food truck owner**, I want:
- To create and manage events directly (open events, private events, or closures)
- To have address validation and mandatory fields for open/private events
- To see events ordered chronologically in the admin panel for easier management
- To filter and search events by type, status, and creation date
- To maintain control over which staff users can manage events
- To have my events automatically override the regular schedule display, so customers always see current location information

As a **visitor**, I want:
- To understand the purpose of the app quickly from the landing page.
- To view a dynamic schedule that reflects today’s events, regular operating days, or closures.
- To know when the food truck is closed without guessing.


### Key Features

- **Customer Booking System**: Authenticated users can submit catering requests with advance notice requirements
- **Booking Management Dashboard**: View, edit, and delete bookings with tiered permissions
- **Slot Availability Checker**: Real-time availability with 10-hour gap enforcement between events
- **Inline Editing**: Edit booking details directly on the detail page with immediate feedback
- **Event Management**: Admin-controlled event creation and schedule management
- **Dynamic Schedule Display**: Real-time location information prioritizing events over regular schedule
- **Multi-day Event Support**: Proper handling of events spanning multiple days
- **File Upload Integration**: Cloudinary-powered image handling for events and bookings
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Role-based Access**: Customer vs. admin functionality separation

---
## UX Design

### Wireframes

**Home Page**

![Home Page Wireframe](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765791118/wireframe_homepage_dttemc.png)

**Booking Request Form**

![Booking Form Wireframe](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765792395/wireframe_booking_request_zrtfda.png)

**Booking Management Dashboard**

![Bookings List Wireframe](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765791118/wireframe_bookings_pewei2.png)

**Booking Detail with Inline Edit**

![Booking Detail Wireframe (based on booking request)](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765791118/wireframe_booking_detail_display_mode_fdm9jd.png)

### Design Decisions

**Peerspace-Inspired Booking Flow**

The booking interface draws inspiration from [Peerspace](https://www.peerspace.com/), implementing a progressive disclosure pattern:

1. **Pick date** → User selects date from inline calendar
2. **See availability** → System shows available time window
3. **Select times** → Filtered dropdowns show only valid options
4. **Fill details** → Complete remaining booking information
5. **Submit** → Confirmation with success feedback

This approach reduces cognitive load by showing relevant options only when needed.

**Inline Calendar vs. Date Picker**

| Approach | Pros | Cons |
|----------|------|------|
| Standard date picker | Familiar, compact | No availability context |
| Inline calendar | Shows availability instantly | Takes more space |

**Decision:** Inline calendar using Flatpickr, enabling real-time availability feedback as users browse dates.

**Information Hierarchy**

- Primary actions (Submit, Save) use brand color (danger/red)
- Secondary actions (Cancel, Back) use outline variants
- Status badges provide immediate booking state recognition
- Timestamp labels show relevant lifecycle information

---

## Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Django 4.2.1 | Python web framework |
| PostgreSQL | Production database |
| Django Allauth | Authentication system |
| Cloudinary | Media file storage and optimization |

### Frontend

| Technology | Purpose |
|------------|---------|
| Bootstrap 5 | Responsive CSS framework |
| Bootstrap Icons | Icon library via CDN |
| Crispy Forms | Enhanced form rendering |
| Summernote | Rich text editing for descriptions |
| Flatpickr | Inline calendar date picker |

### Development Tools

| Tool | Purpose |
|------|---------|
| Visual Studio Code | Primary IDE |
| Git | Version control |
| GitHub | Repository hosting and project management |

### Deployment

| Technology | Purpose |
|------------|---------|
| Heroku | Cloud platform hosting |
| WhiteNoise | Static file serving |
| Environment Variables | Secure configuration management |

---

## Database Schema (ERD)

### Entity Relationship Diagram

![ERD Diagram](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765794169/axoelote_erd_dbu9lr.png)

### Model Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Booking | One-to-Many | Customers can create multiple booking requests |
| User → Event | One-to-Many | Admin users can manage multiple events |
| RegularSchedule | Singleton | Independent fallback schedule (one active record) |

### Booking Model

Previously named `BookingRequest`, renamed to `Booking` for clarity.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | Primary Key | Auto-incrementing ID |
| customer | ForeignKey(User) | CASCADE, required | Links to customer who made request |
| event_title | CharField(100) | required | Name of the event |
| event_type | CharField(20) | choices: open, private | Type of event requested |
| guest_count | PositiveIntegerField | min_value=70 | Number of guests (business rule) |
| start_datetime | DateTimeField | required | Event start time |
| end_datetime | DateTimeField | required | Event end time |
| description | TextField | optional | Event details (required for open events) |
| message | TextField | optional | Special requests, dietary restrictions |
| status | CharField(20) | choices: pending, approved, cancelled | Request status |
| street_address | CharField(80) | required | Event location address |
| postcode | CharField(20) | required | Postal code |
| town_or_city | CharField(40) | optional | City name |
| country | CountryField | optional | Country selection |
| event_photo | CloudinaryField | optional | Event inspiration photo |
| created_at | DateTimeField | auto_now_add | Record creation timestamp |
| updated_at | DateTimeField | auto_now | Last modification timestamp |
| approved_at | DateTimeField | nullable | Approval timestamp for edit tracking |

### Event Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | Primary Key | Auto-incrementing ID |
| admin | ForeignKey(User) | PROTECT, required | Admin who created the event |
| event_title | CharField(100) | required | Event name |
| event_type | CharField(20) | choices: open, private, closure | Event type |
| start_datetime | DateTimeField | required | Event start time |
| end_datetime | DateTimeField | required | Event end time |
| street_address | CharField(80) | optional for closures | Event location |
| postcode | CharField(20) | optional | Postal code |
| town_or_city | CharField(40) | optional | City name |
| country | CountryField | optional | Country selection |
| description | TextField | required | Event description |
| message | TextField | optional | Internal admin notes |
| status | CharField(20) | choices: active, postponed, cancelled | Event status |
| event_photo | CloudinaryField | optional | Event photo |
| created_at | DateTimeField | auto_now_add | Record creation timestamp |
| updated_at | DateTimeField | auto_now | Last modification timestamp |

### RegularSchedule Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | Primary Key | Auto-incrementing ID |
| venue_name | CharField(100) | required | Location name (e.g., 'Naschmarkt') |
| street_address | CharField(80) | required | Venue address |
| postcode | CharField(20) | optional | Postal code |
| town_or_city | CharField(40) | required | City name |
| country | CountryField | optional | Country selection |
| monday - sunday | BooleanField | default varies | Open on each day |
| opening_time | TimeField | required | Daily opening time |
| closing_time | TimeField | required | Daily closing time |
| is_active | BooleanField | default=True | Schedule active status |
| updated_at | DateTimeField | auto_now | Last modification timestamp |

---

## Features
### CRUD Operations

Full Create, Read, Update, Delete functionality with user feedback on all operations.

| Operation | Feature | User Feedback |
|-----------|---------|---------------|
| **Create** | Booking request form | "Booking request submitted successfully!" |
| **Read** | Bookings list, booking detail | Tabbed interface with status filtering |
| **Update** | Inline edit on booking detail | "Booking updated successfully" |
| **Delete** | Cancel modal confirmation | "{title} has been deleted." |

CRUD Create: Booking Form Initial State
![CRUD Create: Booking Form Initial State](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795063/Screenshot_2025-12-15_at_11.37.06_jga2no.png)

CRUD Read - Bookings List
![CRUD Read - Bookings List](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795174/bookings_list_oow23e.png)

CRUD Update - Inline Edit
![CRUD Update - Inline Edit](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795316/booking_detail_w_inline_edit_toggle_btns_a9rxxr.png)

CRUD Delete - Cancel Modal
![CRUD Delete - Cancel Modal](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795739/delete_booking_modal_srgmk6.png)

**Delete Implementation Decision**

For assessment purposes, delete performs a hard delete (permanently removes record). This clearly satisfies CRUD requirements while V2 will implement soft delete for business audit trails.

| Current (Assessment) | Future (V2) |
|---------------------|-------------|
| Hard delete | Soft delete with status tracking |
| Record removed | Record hidden, preserved for audit |
| Immediate feedback | Cancellation reason tracking |

### Booking Management System

**Bookings Dashboard**

![Bookings Dashboard](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795174/bookings_list_oow23e.png)

Tabbed interface allowing users to filter bookings by status:

| Tab | Filter | Purpose |
|-----|--------|---------|
| ALL | No filter | Overview of all bookings |
| PENDING | status='pending' | Awaiting approval |
| APPROVED | status='approved' | Confirmed bookings |
| ACTIVE | Today's date in range | Currently happening |
| PAST | end_datetime < now | Historical records |



**Tiered Edit Permissions**

Edit capabilities based on proximity to event date:

| Days Until Event | Edit Level | Editable Fields |
|------------------|------------|-----------------|
| 15+ days | Full | All fields including date/time |
| 3-14 days | Cosmetic | Title, description, photo only |
| 0-2 days | None | Contact admin to make changes |
| Past/Cancelled | None | Read-only |

Constants defined in `booking/rules.py`:

```python
FULL_EDIT_DAYS = 15
COSMETIC_EDIT_DAYS = 3
```

**Inline Edit Interface**

Single page handles both display and editing:

Booking Detail - Display Mode
![Booking Detail - Display Mode](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795316/booking_detail_w_inline_edit_toggle_btns_a9rxxr.png)

Booking Detail - Edit Mode
![Booking Detail - Edit Mode](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765795316/booking_detail_edit_toggled_r0kzw0.png)

### Slot Availability System

Real-time availability checking for booking date/time selection.

**How It Works:**

1. User selects date on inline calendar
2. AJAX request to `/booking/slots/{date}/` API
3. System calculates available windows considering:
   - Existing bookings (pending + approved)
   - Admin events (active status)
   - 10-hour gap requirement between engagements
4. UI displays availability status and filtered time dropdowns

**Availability Window Display**

| Scenario | Display |
|----------|---------|
| Fully available | "Available! Window: 00:00 - 00:00 (next day)" |
| Partial availability | "Available! Window: 13:00 - 00:00 (next day)" |
| Fully booked | "Fully booked - Please select another date" |

**Slot-Aware Time Dropdowns**

Time selection dropdowns are filtered to show only valid times within the available window. Cross-midnight slots display a "Next day" separator for clarity.

Slot Availability - Available
![Slot Availability - Available](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765796161/booking_detail_inline_edit_available_slot_naic36.png)

Slot Availability - Fully Booked
![Slot Availability - Fully Booked](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765796161/booking_detail_inline_edit_fully_booked_jreh2n.png)

### Authentication & Authorization

**Role-Based Access**

| Feature | Visitor | Customer | Admin |
|---------|---------|----------|-------|
| View schedule | ✓ | ✓ | ✓ |
| View public events | ✓ | ✓ | ✓ |
| Submit booking | ✗ | ✓ | ✓ |
| View own bookings | ✗ | ✓ | ✓ |
| Edit own bookings | ✗ | ✓ | ✓ |
| Delete own bookings | ✗ | ✓ | ✓ |
| Access admin panel | ✗ | ✗ | ✓ |
| Manage all events | ✗ | ✗ | ✓ |
| Approve bookings | ✗ | ✗ | ✓ |

**Login State Reflection**

- Navigation changes based on authentication status
- Protected views redirect to login with `?next=` parameter
- Success messages confirm login/logout actions

Navigation - Logged Out
![Navigation - Logged Out](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765796313/loggedin_navbar_zzcclt.png)

Navigation - Logged In
![Navigation - Logged In](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765796312/logged_out_navbar_ebd6aa.png)


---

## Business Rules

Centralized business logic in `booking/rules.py`:

| Constant | Value | Purpose |
|----------|-------|---------|
| MINIMUM_ADVANCE_DAYS | 15 | Days required before event |
| MINIMUM_GUESTS | 70 | Minimum guest count for profitability |
| MINIMUM_GAP_HOURS | 10 | Hours between events for setup/cleanup |
| FULL_EDIT_DAYS | 15 | Days before event for full edit access |
| COSMETIC_EDIT_DAYS | 3 | Days before event for cosmetic edit |
| CONTACT_EMAIL | - | Displayed when edits restricted |
| CONTACT_PHONE | - | Displayed when edits restricted |

**Why 70 guests minimum?**

Business owner determined that private bookings are only profitable above this threshold, compared to regular street sales at weekly market location.

**Why 10-hour gap?**

Allows adequate time for cleanup, rest, travel, and setup between consecutive events.

---

## Development Process

### Initial Setup 

**Environment Configuration**
- Implemented dynamic DEBUG toggle: `DEBUG = 'DYNO' not in os.environ` for True/False Toogle in production + deployment testing
- Separated development/production database configurations
- Established secure environment variable management 

### Agile Methodology

Project managed using GitHub Projects with Kanban board.

[GitHub Project Board](https://github.com/users/iliana-marquez/projects/13/views/1)

**MoSCoW Prioritization**

| Priority | User Stories | Status |
|----------|--------------|--------|
| Must Have | Core booking, authentication, schedule display | Complete |
| Should Have | Inline editing, availability checking | Complete |
| Could Have | Email notifications, calendar export, menu, about, contact | V2 |
| Won't Have | Payment processing, multi-vendor | Out of scope / reasess for V3 |

**Sprint Workflow**

1. User stories refined into tasks
2. Feature branches for development
3. Testing before merge
4. Atomic commits with descriptive messages

### Architecture Decisions

**BookingDetailView: View vs generic.DetailView**

| generic.DetailView provides | App needs |
|----------------------------|-----------|
| Single object lookup | ✓ Same |
| GET only (display) | ✗ Need GET + POST |
| Simple context | ✗ Need form + permissions + rules |

**Decision:** Base `View` class for full control over mixed display/edit functionality.

```python
class BookingDetailView(LoginRequiredMixin, View):
    def get_booking(self, pk):  # Shared logic
    def get(self, request, pk):  # Display
    def post(self, request, pk):  # Save edits or delete
```

**Reusable Components**

| Component | Location | Used By |
|-----------|----------|---------|
| Cancel Modal | `includes/cancel_modal.html` | booking_detail, bookings list |
| Calendar Picker | Flatpickr inline | booking form, booking edit |

---

## Testing

### User Story Testing

Each user story was validated through manual testing with documented results.

**Customer User Stories**

| User Story | Test Case | Steps | Expected | Result |
|------------|-----------|-------|----------|--------|
| See where food truck is today | View homepage | Navigate to homepage | Today's location displayed | ✅ Pass |
| Book food truck for private event | Submit booking | Fill form with valid data, submit | Success message, booking created | ✅ Pass |
| Know booking rules before submitting | View booking form | Navigate to booking form | Rules displayed (70 guests, 15 days advance) | ✅ Pass |
| Upload event photos | Add photo to booking | Select image file, submit form | Image uploaded to Cloudinary | ✅ Pass |
| Log in securely | Authentication flow | Register, logout, login | Account created, session managed | ✅ Pass |
| View my bookings | Access dashboard | Navigate to /booking/bookings/ | List of own bookings displayed | ✅ Pass |
| Edit my booking | Modify booking details | Change title, save | "Booking updated successfully" | ✅ Pass |
| Cancel my booking | Delete booking | Click cancel, confirm modal | "{title} has been deleted" | ✅ Pass |
| See real-time availability | Select date on calendar | Pick date in booking edit | Availability window displayed | ✅ Pass |

**Admin User Stories**

| User Story | Test Case | Steps | Expected | Result |
|------------|-----------|-------|----------|--------|
| Create and manage events | Admin panel | Create event at /admin/ | Event appears in schedule | ✅ Pass |
| Address validation for events | Create event without address | Submit open event without location | Validation error displayed | ✅ Pass |
| See events chronologically | View admin event list | Access events in admin | Ordered by start_datetime | ✅ Pass |
| Filter and search events | Use admin filters | Filter by type, status, date | Filtered results displayed | ✅ Pass |
| Control staff access | Check permissions | Non-staff user tries admin | Access denied | ✅ Pass |

**Visitor User Stories**

| User Story | Test Case | Steps | Expected | Result |
|------------|-----------|-------|----------|--------|
| Understand app purpose | View landing page | Navigate to homepage | Clear hero section with purpose | ✅ Pass |
| View dynamic schedule | Check schedule section | View "Where to find me" | Today's event or regular schedule | ✅ Pass |
| Know when truck is closed | Check closed day | View schedule on closed day | "Closed" status displayed | ✅ Pass |

### Automated Testing

**Test Summary**
```bash
python manage.py test
# Ran 49 tests in 3.745s - OK
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_forms.py` | 15 | Form validation, business rules |
| `test_views.py` | 10 | View responses, authentication |
| `test_slots_v2.py` | 24 | Slot availability system |
| **Total** | **49** | ✅ All passing |

**Slot Availability Tests (`test_slots_v2.py`)**

Comprehensive testing of the booking slot system:

| Test Class | Tests | Purpose |
|------------|-------|---------|
| EngagementsTestCase | 5 | Fetching bookings and events for date range |
| AvailableSlotsTestCase | 3 | Slot window calculation accuracy |
| ExcludeBookingTestCase | 4 | Own booking exclusion during edit |
| CheckSlotAvailableTestCase | 6 | Conflict detection and validation |
| SlotsAPITestCase | 4 | API endpoint responses |
| NaiveDatetimeTestCase | 2 | Timezone handling (USE_TZ=False) |

Automated Test Results
[Automated Test Results](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765798580/automated_test_terminal_fxskvz.png)


### Validation

**Code Validation**

| Language | Validator | Result |
|----------|-----------|--------|
| HTML | W3C Validator | ✅ Pass |
| CSS | Jigsaw Validator | ✅ Pass |
| JavaScript | JSHint | ✅ Pass |
| Python | PEP8 / Flake8 | ✅ Pass |

**Accessibility**

| Tool | Score | Notes |
|------|-------|-------|
| Lighthouse | XX/100 | Accessibility score |
| WAVE | X errors | Details |

![Lighthouse Score](https://res.cloudinary.com/dj2lk9daf/image/upload/v1765799232/lighthouse_validation_bookings_v6hdci.png)


---
## Bug Fixes

### Timezone Handling

**Issue:** Manual testing revealed timezone inconsistencies - times displayed 1 hour differently across UI components.

**Root Cause:** Django with `USE_TZ=True` stores datetimes in UTC, but slot calculations used Vienna timezone. Mixed comparisons failed silently.

**Solution:** Set `USE_TZ=False` for single-timezone Vienna-only app.

| Factor | With USE_TZ=True | With USE_TZ=False |
|--------|-----------------|-------------------|
| Storage | UTC in database | Local time in database |
| Complexity | High | Low (WYSIWYG) |
| Admin display | Shows UTC | Shows Vienna |
| App scope | Multi-timezone ready | Vienna-only (current need) |

### Slot Validation Bug

**Issue:** Editing booking date/time showed false "Conflicts with existing engagement" errors.

**Root Causes & Fixes:**

| File | Issue | Fix |
|------|-------|-----|
| settings.py | USE_TZ=True mixed timezones | Set USE_TZ=False |
| views.py | API ignored ?exclude= param | Pass exclude_id to slot calculation |
| slots.py | Event filter wrong | Filter by status='active' |
| slots.py | exclude_id type mismatch | Convert string to int |
| forms.py | clean() didn't exclude self | Pass self.instance.pk |

### Row Click vs Button Click

**Issue:** Clickable table rows captured button clicks, preventing Edit/Cancel actions.

**Fix:** Add `onclick="event.stopPropagation()"` to actions `<td>` element.

---

## Known Issues

### Booking Request Form — Time Dropdowns Not Filtered

The booking request form (new bookings) still displays all 24-hour time options regardless of availability window, while the booking detail page (edit mode) correctly filters dropdowns to show only valid times within the available slot.

| Page | Time Dropdown Behavior |
|------|----------------------|
| booking_detail (edit) | ✅ Filtered to slot window |
| booking_request (create) | ❌ Shows all 00:00 - 23:30 |

**Impact:** Users creating new bookings can select invalid times that may conflict with existing engagements. Backend validation catches this on submit, but UX could be improved.

**Status:** Backend validation prevents conflicts. Frontend filtering to be aligned with booking_detail behavior in future update.

### Default Availability Window Display

When a date has no engagements, the availability window displays as "00:00 - 00:00 (next day)". While technically correct (full 24h availability), this may confuse users.

- **Current display:** "Available! Window: 00:00 - 00:00 (next day)"
- **User perception:** Potentially misleading, may appear as "no availability"
- **Business rule:** Owner allows any times as long as 10-hour gap exists
- **Status:** UX improvement needed for clearer messaging

### Double-booking Prevention

Currently, overlapping bookings can be created through admin interface. Slot validation only applies to customer-facing booking form.

**Future Enhancement:** Database-level constraints and comprehensive conflict checking across all creation methods.

### Clear Link Non-Functional

The "Clear" link on the booking request form has no functionality. Intended to reset form fields but not implemented.

### Inconsistent Link Styling

Links outside the navbar, buttons, and footer lack consistent styling. Visual polish needed for inline text links throughout the application.

---
## Deployment

### Heroku Deployment Steps

The application is deployed via Heroku Dashboard:

1. Create new app on [Heroku Dashboard](https://dashboard.heroku.com/)
2. Connect GitHub repository under "Deploy" tab
3. Add PostgreSQL under "Resources" → "Add-ons"
4. Configure environment variables under "Settings" → "Config Vars":
   - `SECRET_KEY`
   - `CLOUDINARY_URL`
   - `DATABASE_URL` (auto-set by PostgreSQL add-on)
   - `DEBUG` = `False`
5. Deploy branch under "Deploy" → "Manual Deploy"
6. Run migrations via "More" → "Run Console": `python manage.py migrate`

**Live Application:** [axoelote-foodtruck.herokuapp.com](https://axoelote-foodtruck-6de5775aa776.herokuapp.com/)

### Local Development
```bash
git clone https://github.com/iliana-marquez/axoelote-foodtruck-app.git
cd axoelote-foodtruck-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure your values
python manage.py migrate
python manage.py runserver
```

---

**Future Enhancement:**  
- Implement database-level constraints and comprehensive conflict checking across all booking and event crveation methods.  
- Ensure that admin-created events and customer booking requests cannot overlap for the same date/time.  
- Provide clear error messages to users when a requested slot is unavailable.  
- Implement time-aware schedule logic that considers event end times vs. regular schedule start times
- Establish business rules with stakeholders for minimum prep/setup time between events
- Add configurable buffer periods to determine when regular schedule should resume

## Admin-Configurable Settings (for V2)

**Current state:** Constants in `booking/rules.py`
- MINIMUM_ADVANCE_DAYS = X day in advanced for booking system 
- MINIMUM_GUESTS = X guest for booking system 
- MINIMUM_GAP_HOURS = X hours gap between events for booking system 
- FULL_EDIT_DAYS = X days for edit booking permissions
- COSMETIC_EDIT_DAYS = x days for edit booking permissions
- CONTACT_EMAIL for UI display 
- CONTACT_PHONE for UI display 

**Future state:** All configurable via admin panel

**Why:**
- Business owner can adjust rules without developer
- Seasonal flexibility (e.g., reduce advance days for slow periods)
- White-label ready for multiple clients
- Quick response to market needs

**Scope:**
- Business rules (days, guests, hours)
- Contact information
- Cancellation policy percentages
- Any other operational constants


## Booking Timeline UI instead of sigle timestamp with current record (for V2)

**Concept:** Visual timeline showing booking lifecycle

**Statuses to track:**
- Submitted (created_at)
- Approved (approved_at)
- Edit Requested (edit_requested_at)
- Cancelled (cancelled_at)
- Completed (end_datetime passed)

**Model fields needed:**
- cancelled_at (DateTimeField, null=True)
- edit_requested_at (DateTimeField, null=True)

**UI:** Horizontal or vertical progress indicator with dates

**Inspiration:** Shipping trackers, order status pages

**Benefit:** Professional UX, clear communication, audit trail


### Display Logic Edge Cases
When multiple approved bookings exist for the same day, only the first booking displays in the schedule. The system doesn't break but could provide more complete information.

**Multi-Timezone Support (for V2)**

When expanding to multiple cities/countries, re-enable `USE_TZ = True` and implement proper timezone handling: add timezone field to Client/Venue model, create timezone conversion utilities, update all datetime displays and slot calculations to normalize times consistently.


### Hard Delete for Booking from customer's side

For assessment purposes, the cancel/delete functionality performs a hard delete, permanently removing the booking record from the database. 

| Action | Result |
|--------|--------|
| User clicks Cancel | Modal confirmation appears |
| User confirms | Record deleted from database |
| Feedback | Success message displayed |
| Redirect | Returns to bookings list |

**V2 Enhancement: Soft Delete**

For production business use, soft delete is preferred for audit trails and refund processing:

| User Action | Status Change | Visibility |
|-------------|---------------|------------|
| Customer cancels | `status='cancelled_by_customer'` | Hidden from customer, visible to admin |
| Site owner cancels | `status='cancelled_by_admin'` | Hidden from customer, visible to admin |

Benefits of soft delete:
- Preserves booking history for reporting
- Enables refund tracking and processing
- Audit trail for disputes
- Admin can review cancellation patterns

Implementation requires:
- Add `cancelled_by` field (customer/admin)
- Add `cancelled_at` timestamp
- Filter cancelled bookings from customer views
- Admin dashboard for cancelled bookings

---

## Future Enhancements

### V2 Priorities

| Feature | Description |
|---------|-------------|
| Soft Delete | Preserve cancelled bookings for audit trail |
| Multi-Timezone Support | Re-enable USE_TZ with proper handling |
| Admin-Configurable Rules | Business rules via admin panel |
| Email Notifications | Booking confirmation and status updates |
| Calendar Export | iCal/Google Calendar integration |
| Booking Form Time Filtering | Align with booking_detail dropdown behavior |

### Long-term Features

- Automated customer notifications
- Calendar view for schedule management
- Dietary restriction structured selection
- Advanced reporting and analytics
- Menu display and management
- Social media integration
- Customer testimonials and reviews

---

## Usage Instructions

### For Assessors

#### Test Accounts
- **Admin User**: `Axoelote` / `[password provided separately]`
- **Customer User**: `Patricia` / `[password provided separately]`

#### Key Features to Test

**As a Customer (patricia):**
1. **Register/Login**: Test authentication system
2. **View Schedule**: See today's food truck location on homepage
3. **Submit Booking**: Create and submit a catering request (70+ guests, 72hr advance notice)

**As an Admin (axoelote):**
1. **Admin Panel**: Access Django admin at `/admin/`
2. **Manage Events**: Create, Edit or Delete events that override regular schedule
3. **Manage Bookings**: Approve/reject customer requests
4. **Update Schedule**: Modify regular operating hours and see them reflected on "where to find me" section

#### Testing the Business Logic
- **Schedule Priority**: Events override regular schedule display
- **Validation**: Try booking with <70 guests or <72hr advance notice
- **Multi-day Events**: Create events spanning multiple days

### For Users

#### Customer Workflow
1. Register for an account
2. Check today's location on homepage
3. Submit catering requests through the booking form 


#### Admin Workflow
1. Login to admin panel
2. Create events to override schedule
3. Review and respond to booking requests
4. Update regular schedule as needed

## Acknowledgements

This project was heavily inspired and informed by the **Code Institute’s Codestar Blog Project**.  
The structure, best practices, and overall workflow provided wonderful insights that gave me a lot of knowledge and motivation for building this application.  
The **logo** and **food truck business concept** used in this project is the property of Axoelote. 

A huge thanks to Code Institute for their excellent learning materials and for sparking the ideas that shaped this project. 

Special thanks to **Axoelote** for inspiring this project and for being my first **business customer case**, which marked an important milestone in my development journey. 

I’m excited to continue learning and can’t wait to start working on **Version 2** with even more features and refinements.  


## Key Takeaways

### Planning vs. Agility Balance
I spent considerable time upfront planning, writing detailed user stories, and preparing the project board. However, during development, things changed quickly and pivots happened organically - which somewhat diminished the value of extensive pre-planning. A middle ground between thorough planning and documenting-as-you-go might be more efficient for future projects.

### The Value of Initial Architecture
Despite the planning overhead, the upfront work paid dividends during development. Almost no major setbacks occurred - just a couple of URL wiring issues in the booking app, which were quickly resolved. This suggests that architectural planning, even if not followed exactly, provides a solid foundation.

### Flexible Design Principles
Being adaptable and understanding the core business purposes enabled building robust models that could evolve naturally. Even pivot decisions were made with long-term growth in mind, always trying to keep the database as flexible as possible. This approach reduces stress when implementing changes in production environments.

### Development Velocity
The combination of solid planning and flexible execution were key on the delivery of a production-ready MVP, which demonstrates that good architecture enables rapid feature development and deployment.

## Links

- **Live Application:** [Axoelote Food Truck Webapp](https://axoelote-foodtruck-6de5775aa776.herokuapp.com/)
- **GitHub Repository:** [axoelote-foodtruck-app](https://github.com/iliana-marquez/axoelote-foodtruck-app)