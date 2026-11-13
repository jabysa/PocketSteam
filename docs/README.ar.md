# PocketSteam

**اللغة:** [English](../README.md) · [فارسی](README.fa.md) · العربية

قائمة واحدة لـ Steam على Windows وCS2Kit على Mac وإعداد Steam على Linux.

## اختيار نظام التشغيل

شغّل `python pocketsteam.py` على Windows أو `python3 pocketsteam.py` على macOS/Linux.
اختر نظام الجهاز الحالي؛ القائمة ليست محاكيًا لأنظمة التشغيل.

- **Windows:** انقر مرتين على `Start Steam.cmd` واختر **1**. يستخدم المشغّل السابق دون تشغيل مثبت Steam.
- **macOS:** افتح `Start PocketSteam.command` واختر **2**. إذا فقد الملف صلاحية التنفيذ، شغّل `sh "Start PocketSteam.command"` من الطرفية. يدعم Apple Silicon فقط. اختر `y` للإعداد أو الإصلاح، و`n` لتشغيل إعداد موجود. تحتاج نحو 90 جيجابايت؛ بعد الإعداد سجّل الدخول إلى Windows Steam وثبّت CS2.
- **Linux:** شغّل `sh start.sh` واختر **3**. على x86_64 ينزّل المشغّل حزمة Valve، ويتحقق من SHA-256 المثبت، ويستخرج ملفات التشغيل إلى `LinuxSteam/`. لا يشغّل مثبت deb أو سكربتات الحزمة أو apt أو sudo أو مثبت تبعيات التوزيعة.

يجب توفر محمّل 32 بت والمكتبات وتعريفات الرسوم وأدوات Bash وtar وxz مسبقًا. يتحقق المشغّل من المحمّل والأدوات، ويتحقق Steam من المتطلبات الإضافية؛ لا يثبّت المشغّل المتطلبات الناقصة. إذا تغيرت الحزمة لدى Valve، يتوقف التحقق حتى تحديث PocketSteam.
مسار Mac يستخدم نسخة مصدر CS2Kit المضمّنة، وليس Steam الأصلي لنظام Mac. يكتب إلى `~/CS2` و`~/.cs2kit` و`~/Applications/CS2Kit.app`، وقد ينقل تثبيت CS2 موجودًا إلى مكتبته المنفصلة. **لم يُتحقق من اللعب التنافسي وVAC بعد.**

للاختيار المباشر أضف `--os windows` أو `--os macos` أو `--os linux`.

## تثبيت Python

- **Windows:** نزّله من [الموقع الرسمي](https://www.python.org/downloads/windows/) وشغّل المثبّت أو Install Manager. فعّل **Add Python to PATH** إن ظهر. افتح الطرفية مجددًا وتحقق باستخدام `py -3 --version` أو `python --version`.
- **macOS:** نزّل حزمة `.pkg` من [الموقع الرسمي](https://www.python.org/downloads/macos/) وثبّتها، ثم تحقق باستخدام `python3 --version`. نسخة python.org تتضمن `lzma` المطلوبة لـ CS2Kit. يحتاج CS2Kit أيضًا إلى Rosetta 2.
- **Linux:** تحقق باستخدام `python3 --version`. يجب توفر Python 3.9+ مسبقًا؛ لا يثبّت المشغّل Python أو تبعيات النظام. توقف إن لم تكن المتطلبات موجودة.

تحتاج إلى Python 3.9 أو أحدث؛ لا تحتاج قائمة PocketSteam إلى حزم pip.

## روابط التنزيل الرسمية

- [تنزيل ZIP المشروع](https://github.com/jabysa/PocketSteam/archive/refs/heads/main.zip)
- [Steam لأنظمة Windows وmacOS وLinux](https://store.steampowered.com/about/)
- [مثبّت Steam لويندوز](https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe)؛ مسار Windows هنا لا يشغّله
- [حزمة Steam لنظام Linux](https://repo.steampowered.com/steam/archive/stable/steam_latest.deb)
- [مصدر CS2Kit الأصلي](https://github.com/piwas-21/cs2-apple-silicon) و[تفاصيل النسخة](../vendor/UPSTREAM.md)

## المصدر والترخيص

يتضمن `vendor/cs2kit/` نسخة مصدر غير معدلة مع ترخيص GPL-3.0 الأصلي؛ ليست fork مستقلة على GitHub. لا يتضمن المشروع ملفات Steam أو Wine أو DXMT التنفيذية. يوزّع PocketSteam تحت [GPL-3.0](../LICENSE) مع الحفاظ على إشعارات المؤلفين.

## دون مثبت بصلاحيات المسؤول

إنشاء ملفات المستخدم متوقع. يحتفظ مسار Mac بإعداد CS2Kit في مجلد المستخدم، ويتطلب وجود Python وRosetta مسبقًا. لا يشغّل PocketSteam مثبتات مرتفعة الصلاحيات؛ لكن قد يطلب Steam أو إحدى الألعاب تثبيت خدمة أو متطلبات: **ألغِ الطلب** على الأجهزة المقيدة. قد لا تعمل اللعبة حينها. لا يتضمن المشروع تجاوزًا للصلاحيات.

## تفاصيل مشغّل Windows

شغّل Steam على Windows من مجلد محلي، دون تشغيل برنامج تثبيت Steam.
يستخدم مكتبة Python القياسية فقط؛ لا يحتاج إلى حزم pip أو Wine أو CrossOver.

## البدء السريع

1. ثبّت **Python 3.9 أو أحدث** من [python.org](https://www.python.org/downloads/windows/). فعّل **Add Python to PATH** إذا ظهر الخيار.
2. اختر **Code → Download ZIP** في صفحة المستودع، ثم فك الضغط في مجلد قابل للكتابة، مثل سطح المكتب.
3. أغلق أي نسخة Steam تعمل عبر **Steam → Exit**.
4. انقر مرتين على **`Start Steam.cmd`**.
5. انتظر تنزيل ملفات Steam، ثم سجّل الدخول داخل Steam نفسه.

في المرات التالية، شغّل **`Start Steam.cmd`** مجددًا. احتفظ بملفات المشروع معًا.
تحتاج إلى إصدار Windows بنواة 64 بت يدعمه Steam، واتصال بالإنترنت ومساحة كافية للبرنامج والألعاب.

للتشغيل من الطرفية داخل مجلد المشروع:

```powershell
python steam_portable.py
```

إذا لم يتعرف Windows على `python`، جرّب `py -3 steam_portable.py`.

## آلية العمل

ينزّل المشغّل حزمة بدء التشغيل مباشرة من Valve، ويتحقق من الحجم وSHA-256 وفق قائمة التحديث الرسمية، ويستخرج `Steam.exe` فقط إلى `Steam/`.
قبل التشغيل على Windows، يتحقق من توقيع Valve الصالح باستخدام Authenticode. بعدها ينزّل Steam بقية ملفاته ويحدّثها.
إذا كان Steam.exe موجودًا، يعاد استخدامه مع التحقق من توقيعه قبل التشغيل.

## الحدود

لا يشغّل المشروع `SteamSetup.exe`، لكنه لا يعزل Steam عن Windows:

- قد يكتب Steam في AppData والسجل، أو يطلب صلاحيات المسؤول لخدمة Steam أو متطلبات الألعاب. لا يوافق المشغّل على هذه الطلبات تلقائيًا.
- لا نضمن اللعب عبر الإنترنت أو VAC دون الخدمات المطلوبة.
- أغلق Steam تمامًا قبل نقل المجلد. حذف `Steam/` يحذف الألعاب والبيانات الموجودة فيه أيضًا، وقد تبقى بيانات خارجه.

## الملفات

- `steam_portable.py`: التنزيل والتشغيل
- `Start Steam.cmd`: التشغيل بالنقر المزدوج على Windows
- `test_launcher.py`: اختبارات قراءة قائمة التنزيل
- `Steam/`: البرنامج والبيانات المحلية؛ يتجاهله Git

## حل المشكلات

- **Python غير موجود:** بعد التثبيت افتح الطرفية مجددًا وتحقق باستخدام `python --version` أو `py -3 --version`.
- **خطأ التوقيع أو SHA-256:** لا تشغّل الملف يدويًا؛ تحقق من الاتصال ومن تحديثات المشغّل.
- **خطأ صيغة القائمة:** ربما غيّرت Valve الصيغة ويحتاج المشغّل إلى تحديث.
- توجد السجلات في `Steam/logs`؛ راجع معلومات الحساب قبل مشاركتها.

## الاختبارات والتحقق

اختُبرت مسارات القائمة والموافقة باختبارات محاكاة؛ لم يُختبر التشغيل الكامل على Windows أو Linux. ثُبّت إصدار CS2Kit المضمّن سابقًا بشكل منفصل على M2 Pro، لكن لم تُعد تجربة الإعداد الكامل من القائمة الجديدة.

```powershell
python -m unittest -v
```

لتجهيز الملف دون تشغيله، بما في ذلك على macOS:

```sh
python3 steam_portable.py --prepare-only
```

يتحقق هذا الخيار من الحزمة فقط؛ فحص Authenticode يتم قبل التشغيل المعتاد على Windows.
نجحت اختبارات قراءة القائمة والتنزيل الحقيقي مع التحقق من الحجم وSHA-256 على macOS. لم يُختبر التشغيل النهائي أو فحص التوقيع على Windows بعد.

## تنويه

المشروع غير تابع لشركة Valve، ولا يتضمن المستودع ملفات Steam التنفيذية.
[دليل Valve لنقل Steam](https://help.steampowered.com/en/faqs/view/4BD4-4528-6B2E-8327)
