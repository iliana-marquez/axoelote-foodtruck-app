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
- [Application Architecture](#application-architecture)
  - [App Structure](#app-structure)
  - [Data Models](#data-models)
  - [Business Logic Priority](#business-logic-priority)
- [Development Process](#development-process)
  - [Initial Setup & Architecture Decisions](#initial-setup--architecture-decisions)
  - [Model Development & Testing](#model-development--testing)
  - [Form Development & Validation](#form-development--validation)
  - [Testing Strategy](#testing-strategy)
  - [Critical Bug Fixes](#critical-bug-fixes)
- [Known Limitations](#known-limitations)
- [Installation & Setup](#installation--setup)
  - [Local Development](#local-development)
  - [Production Deployment](#production-deployment)
- [Future Enhancements](#future-enhancements)
- [Usage Instructions](#usage-instructions)
- [Acknowledgements](#acknowledgements)
- [Key Takeaways](#acknowledgements)
    - [Planning vs. Agility Balance](#planning-vs-agility-balance)
    - [The Value of Initial Architecture](#the-value-of-initial-architecture)
    - [Flexible Design Principles](#flexible-design-principles)
    - [Development Velocity](#development-velocity)

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

- **BookingRequest.customer**: ForeignKey with CASCADE deletion (if user deleted, their bookings are removed)
- **Event.admin**: ForeignKey with PROTECT deletion (prevents accidental admin deletion if they have events)
- **RegularSchedule**: Independent model for default schedule fallback
- **CloudinaryField**: Used for image storage in both BookingRequest and Event models
- **CountryField**: Standardized country selection across all location-based models

### Business Logic Implementation

1. **Schedule Priority**: Events override RegularSchedule for display
2. **Validation**: 70+ guest minimum enforced at model level
3. **Status Tracking**: Both BookingRequest and Event models include status management
4. **Audit Trail**: created_at/updated_at timestamps on all user-generated content


## Application Architecture

### App Structure
```
axoelote_foodtruck/
├── home/              # Landing page and schedule orchestration
├── booking/           # Customer booking request management  
├── events/            # Admin event creation and management
└── templates/         # Shared template inheritance
```

### Data Models

#### BookingRequest
- Customer-submitted catering requests
- 70+ guest minimum with 72-hour advance notice
- Address validation and photo upload support
- Status tracking: pending → approved/rejected

#### Event  
- Admin-created schedule overrides
- Event types: open (public), private, closure
- Multi-day support with proper conflict checking
- Status management: active, postponed, cancelled

#### RegularSchedule
- Default operating pattern (Tue-Sat at Naschmarkt)
- Boolean day fields for flexible scheduling
- Fallback display when no events scheduled

### Business Logic Priority
1. **Active Events** (highest priority)
2. **Approved Bookings** (second priority)  
3. **Regular Schedule** (fallback)
4. **Closed** (no schedule available)

## Development Process

### Initial Setup & Architecture Decisions

**Environment Configuration**
- Implemented dynamic DEBUG toggle: `DEBUG = 'DYNO' not in os.environ`
- Separated development/production database configurations
- Established secure environment variable management

**User Management**
- Created test users: Axoelote (admin) and Patricia (customer)
- Resolved database conflicts from previous projects by requesting new DATABASE_URL
- Implemented Allauth for robust authentication flow

**Third-party Integrations**
- **Cloudinary**: Verified image upload functionality through shell testing
- **Summernote**: Rich text editing for event descriptions and special requests
- **Crispy Forms**: Bootstrap 5 template pack for professional form rendering
- **Django Countries**: Geographic validation (pending deprecation update)

### Model Development & Testing

**BookingRequest Evolution**
- Initial model established guest minimum validation (70+ guests)
- Added conditional description requirements for open events
- Implemented 72-hour advance booking business rule
- Enhanced with file upload and dietary restriction messaging

**Event Model Architecture**
- Designed with PROTECT constraints for admin accountability
- Conditional address validation based on event type
- Status tracking with future notification feature preparation
- Chronological ordering for intuitive admin management

**RegularSchedule Implementation**
- Boolean day fields for flexible schedule management
- Dynamic day range display logic (consecutive vs. non-consecutive)
- Integration with priority-based schedule display system

### Form Development & Validation

**BookingRequestForm Features**
- HTML5 datetime-local inputs for better UX
- Comprehensive validation: time order, guest minimums, conditional descriptions
- File upload handling with Cloudinary integration
- Authentication requirement with proper error messaging

**EventAdminForm Security**
- Restricted admin dropdown to staff users only
- Conflict detection to prevent double-booking
- Time validation and conditional address requirements
- Self-exclusion logic for editing existing events


### BookingDetailView: View vs generic.DetailView

**Decision:** Use base `View` class instead of `generic.DetailView`

**Context:** BookingDetailView handles both display and inline editing on the same page.

**Why not generic.DetailView:**

| generic.DetailView provides | Food Truck App needs |
|----------------------------|-----------|
| Single object lookup | ✓ Same |
| GET only (display) | ✗ Need GET + POST |
| Simple context | ✗ Need form + permissions + business rules |
| Standard template rendering | ✗ Need conditional edit sections |

**Why base View is better here:**

| Benefit | Explanation |
|---------|-------------|
| Full control | Custom GET (display) and POST (save) methods |
| Mixed responsibilities | Same URL handles view + edit |
| Permission logic | Tiered edit permissions (full/cosmetic/none) |
| Locked fields | Restore locked fields on cosmetic edit |
| Clean separation | `get()` for display, `post()` for save, `get_booking()` shared |

**Code clarity:**
```python
class BookingDetailView(LoginRequiredMixin, View):
    def get_booking(self, pk):  # Shared logic
    def get(self, request, pk):  # Display
    def post(self, request, pk):  # Save edits
```

**When to use each:**

| Scenario | Class |
|----------|-------|
| Simple list | `generic.ListView` |
| Simple display | `generic.DetailView` |
| Simple form | `generic.CreateView` / `generic.UpdateView` |
| Mixed display + edit | `View` ✓ |
| Custom business logic | `View` |

### Dynamic Timestamp Labels (No Migration Needed)

**Problem:** Display relevant booking timestamp without adding new model fields.

**Solution:** Use existing fields (`created_at`, `updated_at`, `approved_at`) with logic to determine lifecycle stage.

**Existing fields used:**
- `created_at`: Auto-set on creation
- `updated_at`: Auto-updated on any save
- `approved_at`: Set when admin approves

**Logic in `utils.py` → `get_status_timestamp()`:**

| Condition | Label | Timestamp |
|-----------|-------|-----------|
| status == cancelled | Cancelled | updated_at |
| approved_at is None + updated_at == created_at | Submitted | created_at |
| approved_at is None + updated_at > created_at | Edited before approval | updated_at |
| approved_at exists + updated_at == approved_at | Approved | approved_at |
| approved_at exists + updated_at > approved_at | Edited after approval | updated_at |

**Key insight:** `updated_at > approved_at` means user edited after approval. No new fields required.

**Display format:**
```
[Badge: Status] · [Label] [Date]
[Pending] · Edited before approval 15.12.2025
[Approved] · Edited after approval 17.12.2025
```

**Benefit:** 
- Zero migrations
- Clean audit trail
- User-friendly labels
- Leverages Django's auto-timestamp fields

**Lesson:** Before adding new fields, check if existing data + logic can solve the problem.

### Testing Strategy

**Comprehensive Test Coverage**
```bash
# Form Testing
python manage.py test booking.test_forms  # 15 passing tests
python manage.py test booking.test_views  # 10 passing tests

# Test Categories Covered:
- Form validation (all business rules)
- Authentication requirements  
- File upload handling
- Edge cases (time conflicts, guest minimums)
- Success/error message integration
```

**Manual Testing Scenarios**
- Multi-day event display validation
- Schedule priority logic verification
- Admin panel functionality across user roles
- Mobile responsiveness testing
- File upload integration with Cloudinary

### Critical Bug Fixes

**Multi-day Event Display Issue**
```python
# Problem: Events only showed on start date
start_datetime__date=target_date

# Solution: Check for events active during target date  
start_datetime__date__lte=target_date,
end_datetime__date__gte=target_date
```

**72-hour Validation Logic**
- New bookings: 72-hour minimum enforced
- Existing booking updates: No time restrictions (admin flexibility)
- Maintains business policy while enabling operational adjustments

**Cloudinary Integration Fix**
- Resolved urllib3 version conflict (1.26.20 → 1.26.15)
- Proper CloudinaryField import consistency across models
- Successful file upload testing in production environment

## Bug Fixes:
### Row Click vs Button Click Bug
**Issue:** Clickable table rows captured button clicks, preventing Edit/Cancel actions.
**Fix:** Add `onclick="event.stopPropagation()"` to actions `<td>` element.
**Lesson:** When using row-level click handlers, always stop propagation on interactive child elements.


**Timezone Handling Decision**
Manual testing of the booking edit feature revealed timezone inconsistencies:
- Availability status showed "Available" for dates with existing events
- Form validation error messages displayed booking times 1 hour earlier than the summary display
- Same event showed different times in different parts of the UI

Automated tests confirmed the root cause: Django with `USE_TZ = True` stores datetimes in UTC, but slot calculations created some datetimes in Vienna timezone. When mixed, availability windows calculated incorrectly and timezone comparisons failed silently.

```
Slot start: 2026-01-08 00:00:00+01:00 (Vienna)
Slot end:   2026-01-09 01:00:00+00:00 (UTC)  ← Mixed timezones!
```

**Decision: Disable timezone support (`USE_TZ = False`)**

| Factor | With `USE_TZ = True` | With `USE_TZ = False` |
|--------|---------------------|----------------------|
| Storage | UTC in database | Local time in database |
| Complexity | High (conversions everywhere) | Low (WYSIWYG) |
| Admin display | Shows UTC (confusing) | Shows Vienna (correct) |
| Multi-timezone | Ready | Would need migration |
| App scope | Overkill for Vienna-only | Perfect fit |

**Rationale:**
For a single-location food truck app serving Vienna, timezone complexity adds no value and introduces bugs. The pragmatic choice is naive datetimes until multi-region support is needed.

### Slot Validation Bug
**Problem:** Editing a booking's date/time failed with false conflict errors.

**Symptoms identified through manual and automated testing:**
- Own booking showed "Fully booked" when trying to edit same date
- Form validation rejected edits with "Conflicts with existing engagement"
- Events with `status='active'` not detected in availability check
- Timezone inconsistencies caused 1-hour display differences

**Root causes:**
| File | Issue |
|------|-------|
| `settings.py` | `USE_TZ=True` caused UTC/Vienna mixing |
| `views.py` | API ignored `?exclude=` query parameter |
| `slots.py` | Event filter wrong, exclude_id not converted from string |
| `forms.py` | `clean()` didn't exclude own booking on edit |

**Fixes applied:**
- **settings.py:** Set `USE_TZ=False` for single-timezone app
- **views.py:** Pass `exclude_id` from URL params to slot calculation
- **slots.py:** Filter events by `status='active'`, convert string exclude_id to int
- **forms.py:** Pass `self.instance.pk` as exclude_booking_id during validation

**Testing:**
- 24 automated tests covering slot calculation, exclusion logic, and API
- Manual test cases for edit scenarios with/without conflicts

**Lesson learned:** When implementing edit functionality, ensure validation logic accounts for the record being edited to prevent self-conflict false positives.


## Known Limitations

### Double-booking Prevention
Currently, the system allows overlapping bookings and events to be created and edited through separate interfaces.  
Although initial attempts were made to handle this at the form-validation level, the logic was not reliable and has not been implemented in production.  

### Cross-Day Event Schedule Override
Events spanning midnight (e.g., wedding 18:00-02:00) currently override the following day's regular schedule entirely. This may prevent normal operations when the food truck could realistically serve the regular schedule after late events conclude. 

###  Default Availability Window Display**

When a date has no engagements, the availability window displays as "00:00 - 00:00 (next day)". While technically correct (full 24h availability), this may confuse users into thinking late-night bookings aren't possible or that no slots are available.

- **Current display:** "Available! Window: 00:00 - 00:00 (next day)"
- **User perception:** Potentially misleading, may appear as "no availability" eventhough bookings can extend overnight if slot is available (manually posible by checking "Ends next day") under End time input
- **Business rule:** Business owner allows any times as long as 10-hour gap exists between events
- **Status:** UX improvement needed for clearer messaging or extended default window (e.g., 02:00 or 06:00 next day)


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


## Installation & Setup

### Local Development
```bash
# Clone repository
git clone [repository-url]
cd axoelote-foodtruck-app

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with your configuration values

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Production Deployment
The application is configured for Heroku deployment with:
- PostgreSQL database integration
- Cloudinary media storage
- WhiteNoise static file serving
- Secure environment variable management

## Future Enhancements

### Immediate Priorities
1. **Double-booking Prevention**: Implement to eliminate overlapping bookings and events
2. **Cross-Day Event Logic**: Refine schedule override behavior for events spanning midnight
3. **Django Countries Update**: Replace deprecated package before November 2025

### Long-term Features
1. **Automated Customer Notifications**: Leverage postponed event status
2. **Calendar View**: Broader UX for schedule management
3. **Dietary Restriction Management**: Structured dropdown selections
4. **Advanced Reporting**: Analytics for booking patterns and revenue
5. **Menu Display & Management**: Showcase food offerings with pricing and availability
6. **Social Media Integration**: Connect Instagram/Facebook feeds and sharing capabilities
7. **Customer Testimonials & Reviews**: Display feedback and ratings system
8. **About Section w/ Contact Form**: For visitors and users to address general inquiries
9. **Support Contact Form**: For visitors and users to reach technical support or address inquiries directly through the application.

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