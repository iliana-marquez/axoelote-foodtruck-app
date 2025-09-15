# Axoelote Food Truck Webapp

**The Problem:** Food trucks face a daily challenge - customers arrive at yesterday's location to find an empty parking spot. Meanwhile, owners juggle phone calls for private event bookings while trying to update social media with today's location.

**The Solution:** A Django-based web application for managing a mobile food truck business, featuring customer booking requests, event management, and dynamic schedule display.

**The Result:**
Axoelote Food Truck [Webapp Live](https://axoelote-foodtruck-6de5775aa776.herokuapp.com/)
![Axolote Website Screenshot](https://res.cloudinary.com/dj2lk9daf/image/upload/v1757932902/axoelote-website_u9k5v5.png)

**Technical highlights:** User authentication, CRUD operations, automated workflows, responsive design, and cloud deployment.

#### The Details:
- [Project Overview](#project-overview)
  - [User Stories](#user-stories)
  - [Key Features](#key-features)
- [Technology Stack](#technology-stack)
  - [Backend](#backend)
  - [Development Tools](#development-tools)
  - [Frontend](#frontend)
  - [Deployment](#deployment)
- [Database Schema (ERD)](#database-schema-erd)
    - [Model Realationships](#model-relationships)
    - [BookingRequest Table](#bookingrequest-table)
    - [Event Table](#event-table)
    - [RegularSchedule Table](#regularschedule-table)
    - [Key Design Decisions](#key-design-decisions)
    - [Business Logic Implementation](#business-logic-implementation)
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
- [Contact & Support](#contact--support)
- [Acknowledgements](#acknowledgements)
- [Key Takeaways](#acknowledgements)
    - [Planning vs. Agility Balance](#planning-vs-agility-balance)
    - [The Value of Initial Architecture](#the-value-of-initial-architecture)
    - [Flexible Design Principles](#flexible-design-principles)
    - [Development Velocity](#development-velocity)

## Project Overview

### User Stories

As a **customer**, I want:
- To easily see where the food truck will be today, so I don’t go to the wrong location.
- To book the food truck for my private event, providing details such as date, time, and number of guests.
- To know the booking rules (minimum guests, advance notice) so I understand the requirements before submitting.
- To upload event photos or inspiration when making a booking request.
- To log in securely so I can manage my bookings.

As an **admin/food truck owner**, I want:
- To create and manage events directly (open events, private events, or closures).
- To have address validation and mandatory fields for open/private events.
- To see events ordered chronologically in the admin panel for easier management.
- To filter and search events by type, status, and creation date.
- To maintain control over which staff users can manage events in the admin panel.

As a **visitor**, I want:
- To understand the purpose of the app quickly from the landing page.
- To view a dynamic schedule that reflects today’s events, regular operating days, or closures.
- To know when the food truck is closed without guessing.


### Key Features

- **Customer Booking System**: Authenticated users can submit catering requests with 72-hour advance notice
- **Event Management**: Admin-controlled event creation with conflict prevention 
- **Dynamic Schedule Display**: Real-time location information prioritizing events over regular schedule
- **Multi-day Event Support**: Proper handling of events spanning multiple days
- **File Upload Integration**: Cloudinary-powered image handling for events and bookings
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Role-based Access**: Customer vs. admin functionality separation
</details>

## Technology Stack

### Backend
- **Django 4.2.1**: Python web framework
- **PostgreSQL**: Production database
- **Django Allauth**: Authentication system
- **Cloudinary**: Media file storage and optimization

### Frontend
- **Bootstrap 5**: Responsive CSS framework
- **Crispy Forms**: Enhanced form rendering
- **Summernote**: Rich text editing for descriptions

### Development Tools
- **Visual Studio Code**: Primary code editor and IDE
- **Git**: Version control system
- **GitHub**: [Repository](https://github.com/iliana-marquez/axoelote-foodtruck-app) hosting and project management ([GitHub Project](https://github.com/users/iliana-marquez/projects/13/views/1))

### Deployment
- **Heroku**: Cloud platform hosting
- **WhiteNoise**: Static file serving
- **Environment Variables**: Secure configuration management

## Database Schema (ERD)

### Model Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → BookingRequest | One-to-Many | Customers can create multiple booking requests |
| User → Event | One-to-Many | Admin users can manage multiple events |
| RegularSchedule | Singleton | Independent fallback schedule (one active record) |

## BookingRequest Table

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
| status | CharField(20) | choices: pending, approved, rejected | Request status |
| street_address | CharField(80) | required | Event location address |
| postcode | CharField(20) | required | Postal code |
| town_or_city | CharField(40) | optional | City name |
| country | CountryField | optional | Country selection |
| event_photo | CloudinaryField | optional | Event inspiration photo |
| created_at | DateTimeField | auto_now_add | Record creation timestamp |
| updated_at | DateTimeField | auto_now | Last modification timestamp |

## Event Table

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

## RegularSchedule Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | Primary Key | Auto-incrementing ID |
| venue_name | CharField(100) | required | Location name (e.g., 'Naschmarkt') |
| street_address | CharField(80) | required | Venue address |
| postcode | CharField(20) | optional | Postal code |
| town_or_city | CharField(40) | required | City name |
| country | CountryField | optional | Country selection |
| monday | BooleanField | default=False | Open on Monday |
| tuesday | BooleanField | default=True | Open on Tuesday |
| wednesday | BooleanField | default=True | Open on Wednesday |
| thursday | BooleanField | default=True | Open on Thursday |
| friday | BooleanField | default=True | Open on Friday |
| saturday | BooleanField | default=True | Open on Saturday |
| sunday | BooleanField | default=False | Open on Sunday |
| opening_time | TimeField | required | Daily opening time |
| closing_time | TimeField | required | Daily closing time |
| is_active | BooleanField | default=True | Schedule active status |
| updated_at | DateTimeField | auto_now | Last modification timestamp |

### Key Design Decisions

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

## Known Limitations

### Double-booking Prevention
Currently, the system allows overlapping bookings and events to be created and edited through separate interfaces.  
Although initial attempts were made to handle this at the form-validation level, the logic was not reliable and has not been implemented in production.  

**Future Enhancement:**  
- Implement database-level constraints and comprehensive conflict checking across all booking and event creation methods.  
- Ensure that admin-created events and customer booking requests cannot overlap for the same date/time.  
- Provide clear error messages to users when a requested slot is unavailable.  

### Display Logic Edge Cases
When multiple approved bookings exist for the same day, only the first booking displays in the schedule. The system doesn't break but could provide more complete information.

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
2. **Django Countries Update**: Replace deprecated package before November 2025

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