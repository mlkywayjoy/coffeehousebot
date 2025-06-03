from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Put your group chat ID in .env

# Conversation states
ORDER_TYPE, DRINK_TYPE, MILK_TYPE, BYO, DELIVERY, ROOM, SUMMARY, PAYMENT, BUG_REPORT = range(9)

# Prices
PRICES = {
    "drip": 1.5,
    "espresso_shot": 2.0,
    "americano": 2.0,
    "latte": 2.5,
    "cappuccino": 2.5,
}
OATMILK_SURCHARGE = 0.5

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
    [InlineKeyboardButton("Order Now", callback_data="now")],
    [InlineKeyboardButton("Preorder", callback_data="preorder")],
    [InlineKeyboardButton("Report a Bug", callback_data="report_bug")]
        ]

    await update.message.reply_text("Welcome to RVRCoffee!\nWould you like to order now or preorder?",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return ORDER_TYPE

# Order timing
async def handle_order_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['order_type'] = query.data

    keyboard = [
        [InlineKeyboardButton("Drip Coffee", callback_data="drip")],
        [InlineKeyboardButton("Espresso", callback_data="espresso")]
    ]
    await query.edit_message_text("Great! What type of coffee would you like?",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return DRINK_TYPE

# Coffee type
async def handle_drink_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data['coffee_type'] = choice

    if choice == "espresso":
        keyboard = [
            [InlineKeyboardButton("Espresso", callback_data="espresso_shot")],
            [InlineKeyboardButton("Americano", callback_data="americano")],
            [InlineKeyboardButton("Latte", callback_data="latte")],
            [InlineKeyboardButton("Cappuccino", callback_data="cappuccino")]
        ]
        await query.edit_message_text("Which espresso drink would you like?",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return DRINK_TYPE
    else:
        context.user_data['drink'] = "Drip Coffee"
        return await prompt_milk_type(query, context)

# Specific espresso
async def handle_espresso_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data['drink'] = choice.replace("_", " ").title()

    if choice in ["espresso_shot", "americano"]:
        context.user_data['milk'] = "none"
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data="yes")],
            [InlineKeyboardButton("No", callback_data="no")]
        ]
        await query.edit_message_text("Are you bringing your own cup?",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return BYO
    else:
        return await prompt_milk_type(query, context)

# Milk type
async def prompt_milk_type(query, context):
    keyboard = [
        [InlineKeyboardButton("Milk", callback_data="milk")],
        [InlineKeyboardButton("Oat Milk", callback_data="oatmilk")]
    ]
    await query.edit_message_text("What kind of milk would you like?",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return MILK_TYPE

async def handle_milk_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    milk = query.data
    context.user_data['milk'] = milk

    keyboard = [
        [InlineKeyboardButton("Yes", callback_data="yes")],
        [InlineKeyboardButton("No", callback_data="no")]
    ]
    await query.edit_message_text("Are you bringing your own cup?",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return BYO

# Bring your own cup
async def handle_byo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    byo = query.data
    context.user_data['byo'] = byo

    if byo == "yes":
        await query.message.reply_text("☕ Please remember to bring your cup!")

    keyboard = [
        [InlineKeyboardButton("Pickup", callback_data="pickup")],
        [InlineKeyboardButton("Delivery", callback_data="delivery")]
    ]
    await query.message.reply_text("Pickup or delivery?",
                                   reply_markup=InlineKeyboardMarkup(keyboard))
    return DELIVERY

# Delivery/pickup
async def handle_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    delivery = query.data
    context.user_data['delivery'] = delivery

    if delivery == "pickup":
        context.user_data['location'] = "Pickup at coffee station"
        return await show_summary(update, context)
    else:
        await query.message.reply_text("Which block are you in? (e.g. F, G)")
        return ROOM  # We'll use ROOM to collect both block and room


# Room input
async def handle_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()

    # Basic format validation (e.g. F 201)
    parts = text.split()
    if len(parts) != 2 or not parts[0].isalpha() or not parts[1].isdigit():
        await update.message.reply_text("Please enter in the format: Block Room (e.g. F 201)")
        return ROOM

    block, room = parts
    context.user_data['block'] = block
    context.user_data['room'] = room
    context.user_data['location'] = f"Delivery to Block {block} Room {room}"

    return await show_summary(update, context)

# Show summary + QR
async def show_summary(update, context):
    data = context.user_data
    base = PRICES.get(data['drink'].lower().replace(" ", "_"), 1.5)
    if data['milk'] == "oatmilk":
        base += OATMILK_SURCHARGE
    context.user_data['price'] = round(base, 2)

    summary = f"""☕ *Order Summary*:
- Drink: {data['drink']}
- Milk: {data['milk'].capitalize()}
- BYO Cup: {'Yes' if data['byo']=='yes' else 'No'}
- - Location: {data.get('location', 'Pickup')}
- 💰 Total: ${context.user_data['price']:.2f}

Please *upload a screenshot* of your PayNow payment to confirm your order.
"""
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.message.reply_text(summary, parse_mode='Markdown')
    else:
        await update.message.reply_text(summary, parse_mode='Markdown')

    # Replace with your own QR image
    with open("paynow_qr.png", "rb") as qr:
        await update.message.reply_photo(photo=InputFile(qr), caption="Scan this QR to pay!")

    return PAYMENT

# Image upload
async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    user_id = update.message.from_user.id
    filename = f"payment_{user_id}_{datetime.now().timestamp()}.jpg"
    await file.download_to_drive(custom_path=filename)

    # Send to group chat
    order = context.user_data
    msg = f"📩 New order from user {user_id}:\n- {order['drink']} ({order['milk']})\n- {order['location']}\n- BYO: {order['byo']}\n- ${order['price']:.2f}\nPayment proof uploaded."
    with open(filename, "rb") as img:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=InputFile(img), caption=msg)

    await update.message.reply_text("Thanks! Your order has been received and is pending confirmation.")

    user = update.message.from_user
    username = user.username or "N/A"
    first_name = user.first_name
    user_id = user.id

    order = context.user_data
    msg = (
        f"📩 New order from @{username} (ID: {user_id}, Name: {first_name}):\n"
        f"- {order['drink']} ({order.get('milk', 'none')})\n"
        f"- {order['location']}\n"
        f"- BYO: {order['byo']}\n"
        f"- ${order['price']:.2f}\n"
        "Payment proof uploaded."
    )

    return ConversationHandler.END

# bug reports
async def handle_report_bug_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please describe the bug or issue you're facing.")
    return BUG_REPORT

async def handle_report_bug_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    report = f"🐞 Bug report from @{user.username or 'N/A'} (ID: {user.id}, Name: {user.first_name}):\n{text}"
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=report)

    await update.message.reply_text("Thank you! Your report has been sent to the team.")
    return ConversationHandler.END


# Main
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ORDER_TYPE: [CallbackQueryHandler(handle_order_type)],
            DRINK_TYPE: [
                CallbackQueryHandler(handle_drink_type, pattern="^(drip|espresso)$"),
                CallbackQueryHandler(handle_espresso_choice, pattern="^(espresso_shot|americano|latte|cappuccino)$")
            ],
            MILK_TYPE: [CallbackQueryHandler(handle_milk_type)],
            BYO: [CallbackQueryHandler(handle_byo)],
            DELIVERY: [CallbackQueryHandler(handle_delivery)],
            ROOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_room)],
            PAYMENT: [MessageHandler(filters.PHOTO, handle_payment_proof)],
            BUG_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report_bug_finish)],

        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
