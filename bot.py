import asyncio

# ========== মূল সমাধান: pyrogram ইমপোর্ট করার আগে event loop তৈরি করুন ==========
# Python 3.14 এ get_event_loop ডিফল্টভাবে loop তৈরি করে না, এখানে ম্যানুয়ালি সেট করতে হবে
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ==================================================================

from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream

# ========== এখানে আপনার তথ্য পূরণ করুন ==========
API_ID = 37953688
API_HASH = "cd4a38ad627105f20bba573575f79749"
BOT_TOKEN = "9070389160:AAFsiNkuwTHOVIgKqxcWZDBTH2oghXLaSBY"
SESSION_STRING = "1BVtsOH8Bu51pipKaAJezJO0KfLxcgSUFJRc1Teq8YOWuivT2aS5t__crHEhmIz12dP18P3Sr9zpenxembO1IZbXHfbuAY82Jb6Ai6yaRwWKKBSgfJCEyBemSucdThsGu7JoCsT1AJQyyvXtWXQehLbIxLtCzg_yRvQJOe7O0yW8_lWanp7Wgr-Ll8Di0whtvtx_KIDzhDfigS56UrWpk-cfNe6O8r-PnRmtdQR8tLbW69SjEnw6_CNThMKE0SKib3GwhAl1dHZUZTAqyGF0PPohV5H0QdnUrvxre0aZ119k1YULJDESZgxKgLmHLtSzHY4vhKeoRH9pGOZw8VJgoB-S74E9go28="
# ==============================================

# Bot ক্লায়েন্ট (কমান্ড গ্রহণের জন্য)
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ব্যক্তিগত অ্যাকাউন্ট ক্লায়েন্ট (প্রকৃতপক্ষে লাইভে যোগ দেওয়ার জন্য)
user = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True
)

# pytgcalls ক্লায়েন্ট
call_client = PyTgCalls(user)

TARGET_CHAT_ID = None
IS_JOINED = False


@bot.on_message(filters.command("set") & filters.private)
async def set_target(bot_client, message):
    global TARGET_CHAT_ID
    try:
        chat_id = int(message.text.split()[1])
        TARGET_CHAT_ID = chat_id
        await message.reply(f"✅ লক্ষ্য চ্যানেল ID সেট করা হয়েছে: `{chat_id}`")
    except (IndexError, ValueError):
        await message.reply("❌ ব্যবহার: `/set -100xxxxxxxxxx`")


@bot.on_message(filters.command("run") & filters.private)
async def run_join(bot_client, message):
    global IS_JOINED
    if not TARGET_CHAT_ID:
        return await message.reply("❌ প্রথমে /set দিয়ে চ্যানেল ID সেট করুন")
    if IS_JOINED:
        return await message.reply("ℹ️ ইতিমধ্যে যোগ দেওয়া হয়েছে")

    await message.reply("⏳ লাইভে যোগ দেওয়ার চেষ্টা করছি...")
    try:
        # audio=None মানে শুধু শ্রোতা, কথা বলবে না
        await call_client.play(
            TARGET_CHAT_ID,
            MediaStream(audio=None),
        )
        IS_JOINED = True
        await message.reply("✅ সফলভাবে লাইভে যোগ দিয়েছে (নীরব অবস্থায়)")
    except Exception as e:
        await message.reply(f"❌ যোগদান ব্যর্থ: {e}")


@bot.on_message(filters.command("stop") & filters.private)
async def stop_leave(bot_client, message):
    global IS_JOINED
    if not IS_JOINED:
        return await message.reply("ℹ️ বর্তমানে লাইভে নেই")

    await message.reply("⏳ লাইভ থেকে বের হচ্ছি...")
    try:
        await call_client.leave_call(TARGET_CHAT_ID)
        IS_JOINED = False
        await message.reply("✅ লাইভ থেকে বের হয়েছে")
    except Exception as e:
        await message.reply(f"❌ প্রস্থান ব্যর্থ: {e}")


async def main():
    await bot.start()
    await user.start()
    call_client.start()
    print("✅ সব চালু হয়েছে")
    idle()  # pytgcalls এর নিজস্ব idle, ইভেন্ট লুপ চালু রাখার জন্য


if __name__ == "__main__":
    asyncio.run(main())
