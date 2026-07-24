import json
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================================================
# الإعدادات
# ==================================================

TOKEN = "8618588998:AAHuilhb0Po6tETJtdGZHZx9lfLHFEH3Pk4"

OWNER_ID = 8024474119

DATABASE_FILE = "database.json"

USERS_FILE = "users.json"

# ==================================================
# المواد
# ==================================================

SUBJECTS = {
    "math": "📘 الرياضيات",
    "physics": "⚡ الفيزياء",
    "chemistry": "🧪 الكيمياء",
    "biology": "🧬 الأحياء",
    "arabic": "📖 اللغة العربية",
    "english": "🇬🇧 اللغة الإنجليزية",
    "islamic": "☪️ التربية الإسلامية",
}

# ==================================================
# البيانات
# ==================================================

MATERIALS = {}

for subject, title in SUBJECTS.items():

    MATERIALS[subject] = {
        "title": title,
        "teachers": {}
    }

# ==================================================
# المستخدمون
# ==================================================

USERS = {}

# ==================================================
# حفظ البيانات
# ==================================================

def save_data():

    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            MATERIALS,
            file,
            ensure_ascii=False,
            indent=4
        )

# ==================================================
# تحميل البيانات
# ==================================================

def load_data():

    if not os.path.exists(
        DATABASE_FILE
    ):

        save_data()

        return

    try:

        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved = json.load(file)

        for subject in saved:

            if subject in MATERIALS:

                MATERIALS[
                    subject
                ][
                    "teachers"
                ] = saved[
                    subject
                ].get(
                    "teachers",
                    {}
                )

    except Exception as e:

        print(
            "⚠️ خطأ في تحميل البيانات:",
            e
        )

# ==================================================
# حفظ المستخدمين
# ==================================================

def save_users():

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            USERS,
            file,
            ensure_ascii=False,
            indent=4
        )

# ==================================================
# تحميل المستخدمين
# ==================================================

def load_users():

    global USERS

    if not os.path.exists(
        USERS_FILE
    ):

        USERS = {}

        save_users()

        return

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            USERS = json.load(file)

    except Exception as e:

        print(
            "⚠️ خطأ في تحميل المستخدمين:",
            e
        )

        USERS = {}

# ==================================================
# تسجيل المستخدم
# ==================================================

def register_user(user):

    if not user:

        return

    user_id = str(
        user.id
    )

    username = user.username or ""

    first_name = user.first_name or ""

    last_name = user.last_name or ""

    USERS[user_id] = {

        "id": user.id,

        "username": username,

        "first_name": first_name,

        "last_name": last_name,

    }

    save_users()

# ==================================================
# لوحة المالك
# ==================================================

def owner_menu():

    keyboard = [

        [

            InlineKeyboardButton(
                "👨‍🏫 إدارة المدرسين",
                callback_data="owner_teachers"
            )

        ],

        [

            InlineKeyboardButton(
                "📚 إدارة الملازم",
                callback_data="owner_books"
            )

        ],

        [

            InlineKeyboardButton(
                "👥 المستخدمون",
                callback_data="owner_users"
            )

        ],

        [

            InlineKeyboardButton(
                "📊 الإحصائيات",
                callback_data="owner_stats"
            )

        ],

    ]

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# قائمة المواد للمستخدم
# ==================================================

def user_subjects_menu():

    keyboard = []

    for subject, title in SUBJECTS.items():

        keyboard.append([

            InlineKeyboardButton(
                title,
                callback_data=(
                    f"user_subject:{subject}"
                )
            )

        ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# قائمة المدرسين للمستخدم
# ==================================================

def user_teachers_menu(
    subject
):

    keyboard = []

    teachers = MATERIALS[
        subject
    ][
        "teachers"
    ]

    for teacher in teachers:

        keyboard.append([

            InlineKeyboardButton(
                f"👨‍🏫 {teacher}",
                callback_data=(
                    f"user_teacher:"
                    f"{subject}:"
                    f"{teacher}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="user_home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# قائمة الملازم للمستخدم
# ==================================================

def user_books_menu(
    subject,
    teacher
):

    keyboard = []

    books = MATERIALS[
        subject
    ][
        "teachers"
    ][
        teacher
    ]

    for book_name in books:

        keyboard.append([

            InlineKeyboardButton(
                f"📘 {book_name}",
                callback_data=(
                    f"user_book:"
                    f"{subject}:"
                    f"{teacher}:"
                    f"{book_name}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 رجوع للمدرسين",
            callback_data=(
                f"user_subject:{subject}"
            )
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# مواد المالك
# ==================================================

def owner_subjects_menu(
    prefix
):

    keyboard = []

    for subject, title in SUBJECTS.items():

        keyboard.append([

            InlineKeyboardButton(
                title,
                callback_data=(
                    f"{prefix}:{subject}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 لوحة المالك",
            callback_data="owner_home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# إدارة المدرسين
# ==================================================

def teacher_manage_menu(
    subject
):

    keyboard = [

        [

            InlineKeyboardButton(
                "➕ إضافة مدرس",
                callback_data=(
                    f"add_teacher:{subject}"
                )
            )

        ]

    ]

    for teacher in MATERIALS[
        subject
    ][
        "teachers"
    ]:

        keyboard.append([

            InlineKeyboardButton(
                f"👨‍🏫 {teacher}",
                callback_data="no_action"
            ),

            InlineKeyboardButton(
                "🗑️",
                callback_data=(
                    f"delete_teacher:"
                    f"{subject}:"
                    f"{teacher}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="owner_teachers"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# اختيار مدرس لإدارة الملازم
# ==================================================

def teacher_books_menu(
    subject
):

    keyboard = []

    for teacher in MATERIALS[
        subject
    ][
        "teachers"
    ]:

        keyboard.append([

            InlineKeyboardButton(
                f"👨‍🏫 {teacher}",
                callback_data=(
                    f"manage_books:"
                    f"{subject}:"
                    f"{teacher}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="owner_books"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# إدارة الملازم
# ==================================================

def books_manage_menu(
    subject,
    teacher
):

    keyboard = [

        [

            InlineKeyboardButton(
                "➕ إضافة ملزمة PDF",
                callback_data=(
                    f"add_book:"
                    f"{subject}:"
                    f"{teacher}"
                )
            )

        ]

    ]

    for book_name in MATERIALS[
        subject
    ][
        "teachers"
    ][
        teacher
    ]:

        keyboard.append([

            InlineKeyboardButton(
                f"📘 {book_name}",
                callback_data="no_action"
            ),

            InlineKeyboardButton(
                "🗑️",
                callback_data=(
                    f"delete_book:"
                    f"{subject}:"
                    f"{teacher}:"
                    f"{book_name}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "🔙 رجوع",
            callback_data=(
                f"manage_subject_books:"
                f"{subject}"
            )
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )

# ==================================================
# START
# ==================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(user)

    if user.id == OWNER_ID:

        await update.message.reply_text(

            "👑 أهلاً بك أيها المالك\n\n"
            "🛠️ لوحة تحكم البوت:",

            reply_markup=owner_menu()

        )

        return

    await update.message.reply_text(

        "🎓 أهلاً بك في بوت ملازم السادس الإعدادي\n\n"
        "📚 اختر المادة:",

        reply_markup=user_subjects_menu()

    )

# ==================================================
# الأزرار
# ==================================================

async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    user_id = query.from_user.id

    # تسجيل المستخدم عند الضغط على أي زر

    register_user(
        query.from_user
    )

    # ==================================================
    # واجهة المستخدم
    # ==================================================

    if data == "user_home":

        await query.edit_message_text(

            "🎓 بوت ملازم السادس الإعدادي\n\n"
            "📚 اختر المادة:",

            reply_markup=user_subjects_menu()

        )

        return

    # اختيار المادة

    if data.startswith(
        "user_subject:"
    ):

        subject = data.split(
            ":",
            1
        )[1]

        if subject not in MATERIALS:

            return

        teachers = MATERIALS[
            subject
        ][
            "teachers"
        ]

        if not teachers:

            await query.answer(

                "🚧 لا يوجد مدرسون لهذه المادة حاليًا.",

                show_alert=True

            )

            return

        await query.edit_message_text(

            f"{MATERIALS[subject]['title']}\n\n"
            "👨‍🏫 اختر المدرس:",

            reply_markup=user_teachers_menu(
                subject
            )

        )

        return

    # اختيار المدرس

    if data.startswith(
        "user_teacher:"
    ):

        _, subject, teacher = data.split(
            ":",
            2
        )

        if subject not in MATERIALS:

            return

        if teacher not in MATERIALS[
            subject
        ][
            "teachers"
        ]:

            return

        books = MATERIALS[
            subject
        ][
            "teachers"
        ][
            teacher
        ]

        if not books:

            await query.answer(

                "🚧 لا توجد ملازم لهذا المدرس حاليًا.",

                show_alert=True

            )

            return

        await query.edit_message_text(

            f"{MATERIALS[subject]['title']}\n"
            f"👨‍🏫 {teacher}\n\n"
            "📚 اختر الملزمة:",

            reply_markup=user_books_menu(
                subject,
                teacher
            )

        )

        return

    # ==================================================
    # إرسال PDF للمستخدم
    # ==================================================

    if data.startswith("user_book:"):

        _, subject, teacher, book_name = data.split(":", 3)

        try:

            # التأكد من وجود المادة
            if subject not in MATERIALS:

                await query.answer(
                    "❌ المادة غير موجودة.",
                    show_alert=True
                )

                return

            # التأكد من وجود المدرس
            if teacher not in MATERIALS[subject]["teachers"]:

                await query.answer(
                    "❌ المدرس غير موجود.",
                    show_alert=True
                )

                return

            # التأكد من وجود الملزمة
            if book_name not in MATERIALS[subject]["teachers"][teacher]:

                await query.answer(
                    "❌ الملزمة غير موجودة.",
                    show_alert=True
                )

                return

            # الحصول على File ID
            file_id = MATERIALS[
                subject
            ][
                "teachers"
            ][
                teacher
            ][
                book_name
            ]

            # التأكد من وجود File ID
            if not file_id:

                await query.answer(
                    "❌ ملف PDF غير موجود.",
                    show_alert=True
                )

                return

            # إرسال PDF للمستخدم
            await context.bot.send_document(

                chat_id=query.from_user.id,

                document=file_id,

                caption=(
                    f"📘 {book_name}\n"
                    f"👨‍🏫 {teacher}\n\n"
                    "🎓 بالتوفيق في دراستك!"
                )

            )

        except Exception as e:

            print(
                "❌ خطأ في إرسال PDF:",
                repr(e)
            )

            await query.message.reply_text(

                "❌ حدث خطأ أثناء إرسال ملف PDF.\n\n"
                "تأكد من أن ملف PDF محفوظ بشكل صحيح."

            )

        return
    # ==================================================
    # حماية لوحة المالك
    # ==================================================

    if user_id != OWNER_ID:

        await query.answer(

            "❌ ليس لديك صلاحية الوصول.",

            show_alert=True

        )

        return

    # ==================================================
    # لوحة المالك
    # ==================================================

    if data == "owner_home":

        await query.edit_message_text(

            "👑 لوحة تحكم المالك:",

            reply_markup=owner_menu()

        )

        return

    # ==================================================
    # إدارة المدرسين
    # ==================================================

    if data == "owner_teachers":

        await query.edit_message_text(

            "👨‍🏫 إدارة المدرسين\n\n"
            "اختر المادة:",

            reply_markup=owner_subjects_menu(
                "manage_teacher"
            )

        )

        return

    if data.startswith(
        "manage_teacher:"
    ):

        subject = data.split(
            ":",
            1
        )[1]

        await query.edit_message_text(

            f"{MATERIALS[subject]['title']}\n\n"
            "👨‍🏫 إدارة المدرسين:",

            reply_markup=teacher_manage_menu(
                subject
            )

        )

        return

    # إضافة مدرس

    if data.startswith(
        "add_teacher:"
    ):

        subject = data.split(
            ":",
            1
        )[1]

        context.user_data[
            "adding_teacher"
        ] = subject

        await query.edit_message_text(

            "➕ أرسل اسم المدرس الآن:"

        )

        return

    # حذف مدرس

    if data.startswith(
        "delete_teacher:"
    ):

        _, subject, teacher = data.split(
            ":",
            2
        )

        keyboard = [

            [

                InlineKeyboardButton(
                    "✅ نعم، احذف",
                    callback_data=(
                        f"confirm_delete_teacher:"
                        f"{subject}:"
                        f"{teacher}"
                    )
                )

            ],

            [

                InlineKeyboardButton(
                    "❌ إلغاء",
                    callback_data=(
                        f"manage_teacher:"
                        f"{subject}"
                    )
                )

            ]

        ]

        await query.edit_message_text(

            "⚠️ تأكيد الحذف\n\n"

            f"👨‍🏫 المدرس: {teacher}\n\n"

            "⚠️ سيتم حذف المدرس وجميع ملازمه.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )

        return

    # تأكيد حذف المدرس

    if data.startswith(
        "confirm_delete_teacher:"
    ):

        _, subject, teacher = data.split(
            ":",
            2
        )

        if teacher in MATERIALS[
            subject
        ][
            "teachers"
        ]:

            del MATERIALS[
                subject
            ][
                "teachers"
            ][
                teacher
            ]

            save_data()

        await query.edit_message_text(

            "✅ تم حذف المدرس وجميع ملازمه.",

            reply_markup=teacher_manage_menu(
                subject
            )

        )

        return

    # ==================================================
    # إدارة الملازم
    # ==================================================

    if data == "owner_books":

        await query.edit_message_text(

            "📚 إدارة الملازم\n\n"
            "اختر المادة:",

            reply_markup=owner_subjects_menu(
                "manage_subject_books"
            )

        )

        return

    if data.startswith(
        "manage_subject_books:"
    ):

        subject = data.split(
            ":",
            1
        )[1]

        await query.edit_message_text(

            f"{MATERIALS[subject]['title']}\n\n"
            "👨‍🏫 اختر المدرس:",

            reply_markup=teacher_books_menu(
                subject
            )

        )

        return

    # اختيار مدرس

    if data.startswith(
        "manage_books:"
    ):

        _, subject, teacher = data.split(
            ":",
            2
        )

        await query.edit_message_text(

            f"{MATERIALS[subject]['title']}\n"
            f"👨‍🏫 {teacher}\n\n"
            "📚 الملازم:",

            reply_markup=books_manage_menu(
                subject,
                teacher
            )

        )

        return

            
                
                
            

        

    # إضافة ملزمة

    if data.startswith(
        "add_book:"
    ):

        _, subject, teacher = data.split(
            ":",
            2
        )

        context.user_data[
            "adding_book"
        ] = {

            "subject": subject,

            "teacher": teacher

        }

        await query.edit_message_text(

            "📘 إضافة ملزمة PDF\n\n"

            "✍️ أرسل اسم الملزمة الآن:"

        )

        return

    # حذف ملزمة

    if data.startswith(
        "delete_book:"
    ):

        _, subject, teacher, book_name = data.split(
            ":",
            3
        )

        keyboard = [

            [

                InlineKeyboardButton(
                    "✅ نعم، احذف",
                    callback_data=(
                        f"confirm_delete_book:"
                        f"{subject}:"
                        f"{teacher}:"
                        f"{book_name}"
                    )
                )

            ],

            [

                InlineKeyboardButton(
                    "❌ إلغاء",
                    callback_data=(
                        f"manage_books:"
                        f"{subject}:"
                        f"{teacher}"
                    )
                )

            ]

        ]

        await query.edit_message_text(

            "⚠️ تأكيد حذف الملزمة\n\n"

            f"📘 {book_name}\n\n"

            "هل أنت متأكد من الحذف؟",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )

        return

    # تأكيد حذف الملزمة

    if data.startswith(
        "confirm_delete_book:"
    ):

        _, subject, teacher, book_name = data.split(
            ":",
            3
        )

        if book_name in MATERIALS[
            subject
        ][
            "teachers"
        ][
            teacher
        ]:

            del MATERIALS[
                subject
            ][
                "teachers"
            ][
                teacher
            ][
                book_name
            ]

            save_data()

        await query.edit_message_text(

            "✅ تم حذف الملزمة بنجاح.",

            reply_markup=books_manage_menu(
                subject,
                teacher
            )

        )

        return

    # ==================================================
    # المستخدمون
    # ==================================================

    if data == "owner_users":

        total_users = len(
            USERS
        )

        await query.edit_message_text(

            "👥 إدارة المستخدمين\n\n"

            f"📊 عدد المستخدمين المسجلين: "
            f"{total_users}\n\n"

            "ℹ️ يتم تسجيل المستخدم تلقائيًا "
            "عند استخدام البوت.",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "🔙 لوحة المالك",
                        callback_data="owner_home"
                    )

                ]

            ])

        )

        return

    # ==================================================
    # الإحصائيات
    # ==================================================

    if data == "owner_stats":

        teachers_count = 0

        books_count = 0

        for subject in MATERIALS.values():

            teachers_count += len(
                subject[
                    "teachers"
                ]
            )

            for books in subject[
                "teachers"
            ].values():

                books_count += len(
                    books
                )

        users_count = len(
            USERS
        )

        await query.edit_message_text(

            "📊 إحصائيات البوت\n\n"

            f"👥 المستخدمون: "
            f"{users_count}\n\n"

            f"👨‍🏫 المدرسون: "
            f"{teachers_count}\n\n"

            f"📚 الملازم: "
            f"{books_count}",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "🔙 رجوع",
                        callback_data="owner_home"
                    )

                ]

            ])

        )

        return

    if data == "no_action":

        return

# ==================================================
# استقبال النصوص
# ==================================================

async def receive_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(
        user
    )

    if user.id != OWNER_ID:

        return

    # ==================================================
    # إضافة مدرس
    # ==================================================

    if "adding_teacher" in context.user_data:

        subject = context.user_data[
            "adding_teacher"
        ]

        teacher_name = (
            update.message.text.strip()
        )

        if not teacher_name:

            return

        MATERIALS[
            subject
        ][
            "teachers"
        ][
            teacher_name
        ] = {}

        save_data()

        del context.user_data[
            "adding_teacher"
        ]

        await update.message.reply_text(

            "✅ تمت إضافة المدرس بنجاح!\n\n"

            f"👨‍🏫 {teacher_name}",

            reply_markup=owner_menu()

        )

        return

    # ==================================================
    # اسم الملزمة
    # ==================================================

    if "adding_book" in context.user_data:

        book_name = (
            update.message.text.strip()
        )

        if not book_name:

            return

        context.user_data[
            "book_name"
        ] = book_name

        await update.message.reply_text(

            "✅ تم حفظ اسم الملزمة.\n\n"

            "📄 أرسل ملف PDF الآن."

        )

        return

# ==================================================
# استقبال الملفات
# ==================================================

async def receive_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(
        user
    )

    if user.id != OWNER_ID:

        return

    if "adding_book" not in context.user_data:

        return

    if "book_name" not in context.user_data:

        return

    document = update.message.document

    if document.mime_type != "application/pdf":

        await update.message.reply_text(

            "❌ أرسل ملف PDF فقط."

        )

        return

    book_info = context.user_data[
        "adding_book"
    ]

    subject = book_info[
        "subject"
    ]

    teacher = book_info[
        "teacher"
    ]

    book_name = context.user_data[
        "book_name"
    ]

    MATERIALS[
        subject
    ][
        "teachers"
    ][
        teacher
    ][
        book_name
    ] = document.file_id

    save_data()

    del context.user_data[
        "adding_book"
    ]

    del context.user_data[
        "book_name"
    ]

    await update.message.reply_text(

        "✅ تمت إضافة الملزمة بنجاح!\n\n"

        f"📘 {book_name}\n"

        f"👨‍🏫 {teacher}\n\n"

        "💾 تم حفظ ملف PDF بشكل دائم."

    )

# ==================================================
# تشغيل البوت
# ==================================================

load_data()

load_users()

app = Application.builder().token(
    TOKEN
).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CallbackQueryHandler(
        button
    )
)

app.add_handler(
    MessageHandler(
        filters.Document.ALL,
        receive_document
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_text
    )
)

print(
    "✅ Bot Started..."
)

app.run_polling()
