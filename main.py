from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ConversationHandler, MessageHandler,
    ContextTypes, filters
)
import joblib
import pandas as pd

# Modelni yuklash
model = joblib.load("  model.pkl")

# Model uchun kerakli ustunlar
FIELDS = [
    'SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
    'InternetService_Fiber optic', 'PaymentMethod_Electronic check',
    'OnlineSecurity_Yes', 'gender_Male', 'Contract_Two year',
    'PaperlessBilling_Yes', 'TechSupport_Yes'
]

# Har bir savolga mos xabar
QUESTIONS = [
    "1/11 - Siz keksa mijozmisiz? (0 - Yo‘q, 1 - Ha):",
    "2/11 - Xizmatdan foydalanish muddati (oylarda):",
    "3/11 - Oylik to‘lov (so‘m):",
    "4/11 - Umumiy to‘lovlar (so‘m):",
    "5/11 - Fiber optik internetdan foydalanasizmi? (0 - Yo‘q, 1 - Ha):",
    "6/11 - To‘lov usuli - elektron chekmi? (0 - Yo‘q, 1 - Ha):",
    "7/11 - Onlayn xavfsizlik xizmati mavjudmi? (0 - Yo‘q, 1 - Ha):",
    "8/11 - Jinsingiz erkakmi? (0 - Yo‘q, 1 - Ha):",
    "9/11 - Shartnoma ikki yillikmi? (0 - Yo‘q, 1 - Ha):",
    "10/11 - Qog‘ozsiz billingdan foydalanasizmi? (0 - Yo‘q, 1 - Ha):",
    "11/11 - Texnik yordam xizmati mavjudmi? (0 - Yo‘q, 1 - Ha):"
]

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Mijoz ketishini bashorat qiluvchi bot.\n"
        "Bashoratni boshlash uchun /predict deb yozing."
    )

# /predict komandasi
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(QUESTIONS[0])
    return 0

# Har bir foydalanuvchi javobini qayta ishlash
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = len(context.user_data)
    field = FIELDS[step]
    user_input = update.message.text.strip()

    try:
        context.user_data[field] = float(user_input)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat sonli qiymat kiriting (masalan: 0 yoki 1, yoki narx).")
        return step

    if step + 1 < len(FIELDS):
        await update.message.reply_text(QUESTIONS[step + 1])
        return step + 1
    else:
        try:
            df_input = pd.DataFrame([context.user_data])

            # Har bir model kutayotgan ustun uchun yo'q bo'lsa - 0 qiymat berish
            for col in model.feature_names_in_:
                if col not in df_input.columns:
                    df_input[col] = 0

            # Model ustun tartibiga moslashtirish
            df_input = df_input[model.feature_names_in_]

            # Bashorat
            prob = model.predict_proba(df_input)[0][1]
            result = "\u2709\ufe0f Mijoz ehtimol ketadi" if prob >= 0.5 else "\u2705 Mijoz ehtimol qoladi"
            await update.message.reply_text(f"{result}.\nEhtimollik: {prob:.2%}")

        except Exception as e:
            await update.message.reply_text("\u274c Xatolik yuz berdi. Ma'lumotlar noto‘g‘ri bo‘lishi mumkin.")
            print("Model xatosi:", e)

        return ConversationHandler.END

# /cancel komandasi
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    return ConversationHandler.END

# BOT TOKEN (BotFather'dan olingan tokenni bu yerga joylashtiring)
TOKEN = "7901268818:AAHth_XXTnVrDR-JFp5C_uoq7z6F8zzpytA"

# Bot ilovasini yaratish
app = ApplicationBuilder().token(TOKEN).build()

# So‘zlashuv handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("predict", predict)],
    states={i: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)] for i in range(len(FIELDS))},
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Handlerlarni qo‘shish
app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

# Botni ishga tushurish
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    app.run_polling()
