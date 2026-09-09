import os
from pathlib import Path

import resend
from dotenv import load_dotenv


# .env lives at the project root (Nti_Dev_team-main/.env), not next to this
# file. Resolve it explicitly so it loads correctly no matter which
# directory `streamlit run` is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# قراءة Resend API Key
resend.api_key = os.getenv("RESEND_API_KEY")


def send_notification_email(
    recipient_email: str,
    quiz_hours: int,
    remaining_material: int,
    total_material: int,
    study_hours_needed: float,
    schedule_updated: bool,
) -> bool:
    """
    إرسال Notification للمستخدم على الإيميل الشخصي المسجل.
    """

    # التأكد من وجود API Key
    if not resend.api_key:
        print("❌ Resend API Key is missing.")
        return False

    # تحديد حالة تحديث الجدول
    schedule_status = "Yes" if schedule_updated else "No"

    # عنوان الإيميل
    subject = "📚 Intelligent Study Planner - Alert"

    # محتوى الإيميل
    message = f"""
Hello,

📚 Intelligent Study Planner Alert

⚠️ You have a quiz in {quiz_hours} hours.

📖 Remaining material:
{remaining_material} out of {total_material}

⏱️ Study hours needed:
{study_hours_needed} hours

🔄 Schedule updated:
{schedule_status}

Good luck with your studies! 🎓
"""

    try:
        # إرسال الإيميل باستخدام Resend
        response = resend.Emails.send(
            {
                "from": "Study Planner <onboarding@resend.dev>",
                "to": [recipient_email],
                "subject": subject,
                "text": message,
            }
        )

        print("✅ Notification email sent successfully.")
        print(response)

        return True

    except Exception as error:
        print(f"❌ Failed to send notification email: {error}")
        return False