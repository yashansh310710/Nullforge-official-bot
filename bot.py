import sqlite3
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8767333680:AAHOyl7zIw5R2hEeli-a-EoXBIa7ZgE-zS4"
ADMIN_ID = 7117565741
CHANNEL = "@nullforge_net"

# DATABASE
conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS banned (user_id INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS broadcast_msgs (bc_id INTEGER, msg_id INTEGER, user_id INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS support_map (msg_id INTEGER, user_id INTEGER)")
conn.commit()


# ---------------- DATABASE FUNCTIONS ----------------

def add_user(user, username):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (user, username))
    conn.commit()


def get_users():
    cur.execute("SELECT user_id FROM users")
    return [x[0] for x in cur.fetchall()]


def user_count():
    cur.execute("SELECT COUNT(*) FROM users")
    return cur.fetchone()[0]


def banned_count():
    cur.execute("SELECT COUNT(*) FROM banned")
    return cur.fetchone()[0]


def is_banned(user):
    cur.execute("SELECT * FROM banned WHERE user_id=?", (user,))
    return cur.fetchone()



def home_keyboard(user):

    if user == ADMIN_ID:

        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Broadcast Guide", callback_data="bc")],
            [InlineKeyboardButton("📊 Analytics", callback_data="analytics")],
            [InlineKeyboardButton("📜 Commands", callback_data="cmds")]
        ])

    else:

        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💼 Services", callback_data="services")],
            [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")]
        ])


# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    username = update.effective_user.username

    if is_banned(user):

        await update.message.reply_text(
            "🚫 You have been banned by admin.\n\n"
            "Contact admin to get unbanned:\n"
            "@alphaa03"
        )
        return

    # FORCE JOIN
    if user != ADMIN_ID:
        try:
            member = await context.bot.get_chat_member(CHANNEL, user)

            if member.status == "left":

                kb = [
                    [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL[1:]}")]
                ]

                await update.message.reply_text(
                    "⚠️ Join our channel first",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
                return
        except:
            pass

    add_user(user, username)

    # ADMIN PANEL
    if user == ADMIN_ID:

        kb = [
            [InlineKeyboardButton("📢 Broadcast", callback_data="bc")],
            [InlineKeyboardButton("📊 Analytics", callback_data="analytics")],
            [InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("🚫 Ban System", callback_data="banhelp")]
        ]

        await update.message.reply_text(
    "⚙️ Admin Control Panel",
    reply_markup=home_keyboard(user)
)
        return

    # USER MENU
    kb = [
        [InlineKeyboardButton("💼 Services", callback_data="services")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")]
    ]

    await update.message.reply_text(
        "🚀 Welcome!",
        reply_markup=home_keyboard(user)
    )


# ---------------- BUTTONS ----------------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data == "services":

        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

        await q.edit_message_text(
            "💼 Services\n\n"
            "🌐 Website Development\n"
            "🤖 Telegram Bots\n"
            "💻 VPS Hosting\n"
            "⚙ Automation",
            reply_markup=InlineKeyboardMarkup(kb)
        )


    elif q.data == "contact":

        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

        await q.edit_message_text(
            "📩 Send message to contact admin.",
            reply_markup=InlineKeyboardMarkup(kb)
        )


    elif q.data == "analytics":

        cur.execute("SELECT user_id, username FROM users")
        users = cur.fetchall()

        text = f"📊 Bot Analytics\n\n👥 Total Users: {len(users)}\n\n"

        for uid, uname in users[:20]:

            cur.execute("SELECT * FROM banned WHERE user_id=?", (uid,))
            banned = cur.fetchone()

            status = "🚫 BANNED" if banned else "✅ ACTIVE"

            text += f"{uid} | @{uname} | {status}\n"

        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb)
        )


    elif q.data == "bc":

        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

        await q.edit_message_text(
            "📢 Broadcast Guide\n\n"
            "Reply to any message with:\n"
            "/broadcast",
            reply_markup=InlineKeyboardMarkup(kb)
        )


    elif q.data == "cmds":

        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

        await q.edit_message_text(
            "/broadcast - Broadcast message\n"
            "/delbc - Delete broadcast\n"
            "/ban - Ban User\n"
            "/unban - Unban User\n",
            reply_markup=InlineKeyboardMarkup(kb)
        )


    elif q.data == "back":

        if user == ADMIN_ID:

            kb = [
                [InlineKeyboardButton("📢 Broadcast Guide", callback_data="bc")],
                [InlineKeyboardButton("📊 Analytics", callback_data="analytics")],
                [InlineKeyboardButton("📜 Commands", callback_data="cmds")]
            ]

            await q.edit_message_text(
                "⚙️ Admin Control Panel",
                reply_markup=InlineKeyboardMarkup(kb)
            )

        else:

            kb = [
                [InlineKeyboardButton("💼 Services", callback_data="services")],
                [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")]
            ]

            await q.edit_message_text(
                "🚀 Welcome!",
                reply_markup=InlineKeyboardMarkup(kb)
            )
# ---------------- USER MESSAGE ----------------

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message
    user = msg.from_user.id

    if user == ADMIN_ID:
        return

    if is_banned(user):

        await msg.reply_text(
            "🚫 You are banned.\nContact admin: @alphaa03"
        )
        return

    # forward message
    fwd = await msg.forward(chat_id=ADMIN_ID)

    # save mapping
    cur.execute(
        "INSERT INTO support_map VALUES (?,?)",
        (fwd.message_id, user)
    )
    conn.commit()

    await msg.reply_text("✅ Message sent successfully.")

# ---------------- ADMIN REPLY ----------------

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    if msg.from_user.id != ADMIN_ID:
        return

    if not msg.reply_to_message:
        return

    msg_id = msg.reply_to_message.message_id

    cur.execute(
        "SELECT user_id FROM support_map WHERE msg_id=?",
        (msg_id,)
    )

    r = cur.fetchone()

    if not r:
        await msg.reply_text("❌ Error: user not found")
        return

    user_id = r[0]

    try:

        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=update.effective_chat.id,
            message_id=msg.message_id
        )

        await msg.reply_text("✅ Sent")

    except:

        await msg.reply_text("❌ Error sending message")
# ---------------- BROADCAST ----------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to message with /broadcast")
        return

    users = get_users()

    sent = 0
    failed = 0

    progress = await update.message.reply_text("🚀 Broadcasting...")

    semaphore = asyncio.Semaphore(300)

    bc_id = update.message.reply_to_message.message_id
    chat_id = update.message.chat_id

    async def send(user):

        nonlocal sent, failed

        async with semaphore:

            try:

                msg = await context.bot.copy_message(
                    chat_id=user,
                    from_chat_id=chat_id,
                    message_id=bc_id
                )

                cur.execute(
                    "INSERT INTO broadcast_msgs VALUES (?,?,?)",
                    (bc_id, msg.message_id, user)
                )

                sent += 1

            except:
                failed += 1


    await asyncio.gather(*[send(u) for u in users])

    conn.commit()

    await progress.edit_text(
        f"✅ Broadcast Completed\n\nSent: {sent}\nFailed: {failed}"
    )

async def delete_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to broadcast with /delbc")
        return

    bc_id = update.message.reply_to_message.message_id

    rows = cur.execute(
        "SELECT msg_id, user_id FROM broadcast_msgs WHERE bc_id=?",
        (bc_id,)
    ).fetchall()

    if not rows:
        await update.message.reply_text("❌ Broadcast not found in database")
        return

    deleted = 0

    semaphore = asyncio.Semaphore(300)

    async def delete(msg_id, user):

        nonlocal deleted

        async with semaphore:

            try:
                await context.bot.delete_message(user, msg_id)
                deleted += 1
            except:
                pass

    await asyncio.gather(*[delete(m, u) for m, u in rows])

    cur.execute("DELETE FROM broadcast_msgs WHERE bc_id=?", (bc_id,))
    conn.commit()

    await update.message.reply_text(
        f"🧹 Broadcast Deleted\n\nMessages removed: {deleted}"
    )
# ---------------- BAN ----------------

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        # BAN BY REPLY
        if update.message.reply_to_message:

            user = update.message.reply_to_message.forward_from.id

        else:

            target = context.args[0]

            # BAN BY USERNAME
            if target.startswith("@"):

                cur.execute(
                    "SELECT user_id FROM users WHERE username=?",
                    (target[1:],)
                )

                r = cur.fetchone()

                if not r:
                    await update.message.reply_text("❌ User not found in database")
                    return

                user = r[0]

            else:

                user = int(target)

        cur.execute("INSERT INTO banned VALUES (?)", (user,))
        conn.commit()

        await update.message.reply_text("🚫 User banned successfully")

    except:

        await update.message.reply_text(
            "❌ Error\n\n"
            "Use:\n"
            "/ban @username\n"
            "or reply /ban"
        )


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        if update.message.reply_to_message:

            user = update.message.reply_to_message.forward_from.id

        else:

            target = context.args[0]

            if target.startswith("@"):

                cur.execute(
                    "SELECT user_id FROM users WHERE username=?",
                    (target[1:],)
                )

                r = cur.fetchone()

                if not r:
                    await update.message.reply_text("❌ User not found")
                    return

                user = r[0]

            else:

                user = int(target)

        cur.execute("DELETE FROM banned WHERE user_id=?", (user,))
        conn.commit()

        await update.message.reply_text("✅ User unbanned")

    except:

        await update.message.reply_text(
            "❌ Error\n\n"
            "Use:\n"
            "/unban @username\n"
            "or reply /unban"
        )

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📜 Bot Commands\n\n"
        "/start - Start bot\n"
        "/broadcast - Broadcast message\n"
        "/delbc - Delete last broadcast\n"
        "/ban @username or reply /ban\n"
        "/unban @username or reply /unban\n"
        "/cmds - Show commands"
    )

# ---------------- RUN ----------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))

app.add_handler(CallbackQueryHandler(buttons))

app.add_handler(MessageHandler(filters.User(ADMIN_ID) & filters.REPLY & filters.TEXT & ~filters.COMMAND, admin_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
app.add_handler(CommandHandler("delbc", delete_broadcast))
app.add_handler(CommandHandler("cmds", cmds))
print("Bot running...")
app.run_polling()