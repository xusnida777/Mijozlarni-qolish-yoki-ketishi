from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ConversationHandler, MessageHandler,
    ContextTypes, filters
)
import joblib
import pandas as pd

# Modelni yuklash
model = joblib.load("C:/Users/user/Desktop/modullar/Mustaqil/model.pkl")

FIELDS = [
    'SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
    'InternetService_Fiber optic', 'PaymentMethod_Electronic check',
    'OnlineSecurity_Yes', 'gender_Male', 'Contract_Two year',
    'PaperlessBilling_Yes', 'TechSupport_Yes'
]

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

# Bosqichlar uchun integer qiymatlar
STEPS = list(range(len(FIELDS)))  # 0..10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! /predict deb yozing va mijoz ketishini bashorat qilamiz."
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(QUESTIONS[0])
    return STEPS[0]

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = len(context.user_data)
    field = FIELDS[step]
    text = update.message.text.strip()
    try:
        context.user_data[field] = float(text)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat son kiriting.")
        return STEPS[step]

    if step < len(FIELDS) - 1:
        await update.message.reply_text(QUESTIONS[step + 1])
        return STEPS[step + 1]
    else:
        try:
            df = pd.DataFrame([context.user_data])

            # ⚙️ Etishmayotgan ustunlarni 0 bilan to‘liqlash
            for col in model.feature_names_in_:
                if col not in df.columns:
                    df[col] = 0

            df = df[model.feature_names_in_]

            prob = model.predict_proba(df)[0][1]
            result = "📩 Mijoz ketishi mumkin" if prob >= 0 else "✅ Mijoz qolishi mumkin"
            await update.message.reply_text(f"{result}\nEhtimollik: {prob:.2%}")
        except Exception as e:
            print("Model xatosi:", e)
            await update.message.reply_text("❌ Xatolik yuz berdi.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("7901268818:AAHth_XXTnVrDR-JFp5C_uoq7z6F8zzpytA").build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={step: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)]
                for step in STEPS},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True, per_chat=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
