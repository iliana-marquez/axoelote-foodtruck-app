# Axoelote Food Truck Webapp

**The Problem:** Food trucks face a daily challenge - customers arrive at yesterday's location to find an empty parking spot. Meanwhile, owners juggle phone calls for private event bookings while trying to update social media with today's location.

**The Solution:** A web application for food truck business management that automates location updates and streamlines event bookings. Customers check one reliable source for current truck location and hours. Owners manage everything through a simple admin interface that prevents double-booking disasters.

**The Result:**
Axoelote Food Truck Webapp Live
<!-- Westite on different devices image placeholder -->

**How it works:**
- Owner updates today's location once → appears instantly on customer-facing site
- Customer submits private event request → system checks availability automatically
- Owner approves booking → event appears on public calendar, blocking that date
- Regular customers see "Private event today - truck unavailable" instead of wasting a trip

**Core functionality includes:**
- Real-time location and schedule updates
- Booking request system with automatic conflict prevention
- Customer accounts for tracking event requests
- Mobile-responsive design for on-the-go access
- Admin dashboard for daily business management

**Technical highlights:** User authentication, CRUD operations, automated workflows, responsive design, and cloud deployment.

#### The Details:

- [Development Methodology](#development-methodology)
- [Feature Driven User Stories](#feature-driven-user-stories)
- [Database Structure](#database-structure)
- [](#)

## Development Methodology

This project follows Agile development principles with user stories organized using the MoSCoW prioritization method (Must Have, Should Have, Could Have, Won't Have). All user stories and development progress are tracked through a GitHub Projects kanban board.

Project Board: [GitHub Projects kanban board](https://github.com/users/iliana-marquez/projects/13/views/1)

## Feature Driven User Stories

**User types:** 

- **Site Owner**: Focus on business management capabilities including booking approval, event creation, and content management through Django admin interface.
- **Customer/Visitor**: Emphasize user experience for location discovery, event booking, and general inquiries with mobile-first responsive design.

<details>
<summary>Click to display the stories 👇</summary>
<br>

**Implemented Features**

1. **Current location and opening hours**
- As a **Site Owner** I can **manage regular opening hours and locations** so that **customers see default information when no special events are scheduled.**
- As a **Visitor/Customer** I can **see the current location and opening hours** so that **I can plan my visit ahead.**

2. **Menu offer**
- As a **Visitor/Customer** I can **see the menu** so that **I know what the food truck offers.**

3. **About page**
- As a **Visitor/Customer** I can **click on the about link** so that **sI can read the about who Axoelote is.**

4. **Account creation and login**
- As a **Customer** I can **sign up and login** so that **I can make booking requests.**

5. **Booking requests & events**
- As a **Customer** I can **fill out a form** so that **I can send a booking request.**
- As a **Site Owner** I can **receive, see and manage booking requests** so that **I can confirm the request and book the event.**
- As a **Site Owner** I can **create events from booking requests or personal engagements** so that that **I can have my events displayed up to date.**

6. **Contact inquiries**
- As a **Site Owner** I can **see and manage contact inquiries** so that **I can reply back**
- As a **Visitor/Customer** I can **send a message** so that **I can request information or make inquiries**

**Future implementation**

1. **Instagram posts**
- As a **Site Owner** I can **add Instagram post URLs** so that **they can be displayed on the landing page**
- As a **Customer** I can **view instagram posts** so that **I can see what the offer looks like**

2. **Testimonials**
- As a **Site Owner**, I can **review and categorize customer testimonials** so that **I can display relevant feedback to visitors**
- As a **Customer** I can **submit feedback about my experience** so that **I can share my opinion with other potential customers**

</details>

## Database Structure
<!-- DB ERD Placeholder -->
This ERD architecture addresses the operational complexities of running a mobile food service with dual revenue streams: regular street service & private catering events.

**Business Problem Resolution**
1. **Dynamic Location Management:**
The separation between REGULAR_SCHEDULE and EVENT models solves the fundamental food truck challenge of unpredictable locations. Customers need reliable information about where to find the truck, while the owner requires flexibility to override regular patterns for higher-profit catering opportunities. The datetime fields support multi-day closures for vacation periods without disrupting the booking system.
2. **Revenue Optimization Through Booking Management:**
The BOOKING_REQUEST to EVENT workflow automates the owner's most profitable activities. The 70-guest minimum in validation rules reflects real economics - food trucks achieve better margins through private catering than street sales. The automatic event creation prevents double-booking while ensuring approved events appear on the public schedule immediately.
3. **Customer Communication & Trust:**
The conditional display logic (private vs open events) maintains customer trust by providing transparent availability information without compromising private client confidentiality. Customers see accurate schedule information while private event details remain protected.
4. **Data Integrity for Business Operations:**
The intentional redundancy between BOOKING_REQUEST and EVENT serves audit and customer service functions. When disputes arise or customers need booking confirmations, the original request data remains intact even if event details are modified for operational reasons.
5. **Growth Support Infrastructure:** *(future implementation)*
Models like TESTIMONIAL and SOCIAL_MEDIA_POST support marketing efforts essential for food truck visibility. The CONTACT_INQUIRY system handles general business questions that don't require bookings, reducing administrative overhead.

**Technical Decisions Supporting Business Needs**
1. **Automatic Event Creation:**
Eliminates manual data entry errors that could result in customer disappointment or lost revenue from scheduling conflicts.
2. **Date Uniqueness Constraints:**
Prevents overbooking scenarios that would damage business reputation and create operational chaos.
3. **User Authentication Requirements:**
Ensures booking accountability while building a customer database for future marketing efforts.

The structure balances operational efficiency with customer experience, supporting both immediate business needs and future growth scenarios typical of successful food service ventures.
