# RVRCoffee Coffeehouse Bot
A Telegram bot for managing coffee orders in a hostel coffee club. Users can place orders through interactive buttons, choose pickup or delivery, and optionally preorder for a future date and time. Orders are sent to RVRCoffee baristas, and an admin web panel tracks all orders, statuses, and payments via PayNow.

### Features
- Order via Telegram using buttons (no typing needed)
- Drink options 
- Milk options
- Bring your own cup option
- Pickup or delivery option
- Preorder option
- Telegram group notifications for all new orders (for baristas)
- Web-based admin panel:
    - View new / upcoming / completed orders
    - Track payments
    - Daily order summaries

### Tech Stack
- **Bot**: Python, `python-telegram-bot`
- **Backend / API**: FastAPI or Flask (seehow)
- **Database**: SQLite (dev), PostgreSQL (prod-ready)
- **Frontend (Admin Panel)**: Next.js (React + Tailwind)
- **Hosting**: Railway / Render / Vercel

### Development Plan
#### Phase 1: Telegram Bot Core
- Create Telegram bot via @BotFather
- Set up Python project using python-telegram-bot
- Implement inline keyboard order flow
- Send final order summary to user and barista group chat
- Save order to local database (SQLite)

#### Phase 2: Backend API + Admin Panel
- Create FastAPI backend with endpoints: 
    - `GET /orders` (filter by status)
    - `PATCH /orders/{id}` to mark completed / paid
- Build database schema: Orders, Users, Status
- Connect Telegram bot to backend (POST order)
- Scaffold Next.js admin dashboard
    - Display all orders
    - Show daily summaries
    - Add "Mark as Completed" and "Mark as Paid" buttons

#### Phase 3: Integration + Hosting
- Host bot server (Railway/Render)
- Host frontend (Vercel/Netlify)
- Link bot to production webhook
- Deploy full working version to test group
- Write deployment instructions + documentation

#### Future Consideration
- Google Sheets backup for orders
- Notifications when coffee is ready
- Schedule auto daily summary to be sent to admin group

### Final User Flow
1. Order Timing
    - Order Now / Preorder → if Preorder, select date and time

2. Coffee Type
    - Drip Coffee or Espresso
        - If Espresso → Espresso, Americano, Latte, Cappuccino

3. Milk Type
    - Milk or Oat Milk

4. Bring Your Own Cup
    - If Yes → show message “Please remember to bring your cup!”

5. Pickup or Delivery
    - If Delivery → prompt for block and room number

6. Show Order Summary
    - Example: “You ordered a Latte with oat milk for delivery to Block __ Room ___ tomorrow at 12:30PM. Bring own cup.
    - Ask: "Please confirm your order and make payment."

7. Show PayNow QR
    - Send static QR image
    - Ask user: “Please scan the QR and upload a screenshot of your PayNow confirmation.”

8. User Uploads Screenshot
    - Store uploaded image
    - Mark order as "awaiting approval"

9. Notify admin group:
    - “New order from [Name/Block/Room]: Latte – PayNow proof uploaded.”

10. Save order to database
    - Store drink, milk, time, BYO, pickup/delivery, block and room, PayNow proof (image), timestamp