"""
Seed data for Vithaigal Iyakkam digital news publishing platform.
Initializes categories, news articles, breaking news, and site settings.
"""

import random
from datetime import UTC, datetime, timedelta

from database import db
from database.models import (
    Article,
    BreakingNews,
    Category,
    ContactMessage,
    NewsletterSubscriber,
    User,
    WebsiteSetting,
)


def seed_database():
    # Guarantee at least one valid administrator account exists
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@vithaigaliyakkam.org",
            full_name="Chief Administrator",
            role="admin",
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()

    # Also guarantee ARUN account exists with admin123
    arun_user = User.query.filter_by(username="ARUN").first()
    if not arun_user:
        arun_user = User(
            username="ARUN",
            email="arun@gmail.com",
            full_name="Arun (Administrator)",
            role="admin",
        )
        arun_user.set_password("admin123")
        db.session.add(arun_user)
        db.session.commit()
    else:
        arun_user.set_password("admin123")
        db.session.commit()

    # Only seed content if no categories exist
    if Category.query.first():
        return

    print("Seeding initial database data...")

    # Categories
    categories_data = [
        {
            "name_en": "History",
            "name_ta": "வரலாறு",
            "slug": "history",
            "icon": "landmark",
            "order_index": 1,
            "description_en": "Ancient heritage, archaeological discoveries, Keezhadi excavation updates, Sangam era and cultural history.",
            "description_ta": "பண்டைய தமிழர் நாகரிகம், கீழடி அகழாய்வு முடிவுகள், சங்க காலம் மற்றும் பாரம்பரிய வரலாற்றுத் தொகுப்புகள்.",
        },
        {
            "name_en": "Tamil Nadu",
            "name_ta": "தமிழ்நாடு",
            "slug": "tamil-nadu",
            "icon": "map-pin",
            "order_index": 2,
            "description_en": "Political developments, welfare schemes, civic issues, and cultural happenings across Tamil Nadu.",
            "description_ta": "தமிழக அரசியல் நிகழ்வுகள், அரசு திட்டங்கள், சமூக நலம் மற்றும் மாவட்டச் செய்திகள்.",
        },
        {
            "name_en": "India",
            "name_ta": "இந்தியா",
            "slug": "india",
            "icon": "flag",
            "order_index": 3,
            "description_en": "National news, central government policies, Supreme Court verdicts, and interstate relations.",
            "description_ta": "தேசிய நிகழ்வுகள், உச்சநீதிமன்றத் தீர்ப்புகள், நாடாளுமன்ற நடவடிக்கைகள் மற்றும் தேசியப் பொருளாதாரச் செய்திகள்.",
        },
        {
            "name_en": "World",
            "name_ta": "உலகம்",
            "slug": "world",
            "icon": "globe",
            "order_index": 4,
            "description_en": "Global geopolitics, international relations, diaspora updates, science, and environmental news.",
            "description_ta": "சர்வதேச அரசியல், புலம்பெயர் தமிழர் வாழ்வியல், விண்வெளி ஆய்வுகள் மற்றும் உலகளாவிய நிகழ்வுகள்.",
        },
        {
            "name_en": "Cinema",
            "name_ta": "சினிமா",
            "slug": "cinema",
            "icon": "film",
            "order_index": 5,
            "description_en": "Kollywood updates, box office reports, film reviews, exclusive celebrity interviews, and OTT releases.",
            "description_ta": "தமிழ் திரைப்பட விமர்சனங்கள், பட வெளியீடுகள், இசை வெளியீட்டு விழாக்கள் மற்றும் திரைத்துறை செய்திகள்.",
        },
        {
            "name_en": "Jobs",
            "name_ta": "தொழில் & வேலைவாய்ப்பு",
            "slug": "jobs",
            "icon": "briefcase",
            "order_index": 6,
            "description_en": "Government job alerts, TNPSC notifications, IT campus drives, startup stories, and career counseling.",
            "description_ta": "அரசுப் பணி அறிவிப்புகள், டி.என்.பி.எஸ்.சி தேர்வுகள், புதிய ஸ்டார்ட்அப் வழிகாட்டல்கள் மற்றும் வேலைவாய்ப்பு செய்திகள்.",
        },
        {
            "name_en": "YouTube",
            "name_ta": "யூடியூப் & வீடியோ",
            "slug": "youtube",
            "icon": "play-circle",
            "order_index": 7,
            "description_en": "Exclusive investigative video reports, visual documentaries, expert panel debates, and podcast episodes.",
            "description_ta": "விசேட கள ஆய்வுக் காணொளிகள், நேர்காணல்கள், வரலாற்று ஆவணப்படங்கள் மற்றும் விவாதங்கள்.",
        },
    ]

    cat_map = {}
    for cat in categories_data:
        c = Category(**cat)
        db.session.add(c)
        db.session.flush()
        cat_map[c.slug] = c

    # 3. Breaking News
    breaking_news_list = [
        {
            "title": "Keezhadi Phase 10: 2,600-year-old closed terracotta drainage and carnelian beads unearthed in Sivagangai.",
            "title_ta": "கீழடி 10-ஆம் கட்ட அகழாய்வு: 2600 ஆண்டுகள் பழமையான சுடுமண் வடிகால் அமைப்புகள் மற்றும் சூதுபவள மணிகள் கண்டுபிடிப்பு!",
            "link_url": "/article/keezhadi-phase-10-sangam-era-artifacts-discovered",
            "image_url": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 1,
        },
        {
            "title": "Tamil Nadu EV Expansion: Hosur and Sriperumbudur emerge as global manufacturing corridors.",
            "title_ta": "தமிழ்நாடு மின்வாகன உற்பத்தி: ஓசூர் மற்றும் திருப்பெரும்புதூரில் புதிய சர்வதேச மெகா தொழிற்சாலைகள் துவக்கம்!",
            "link_url": "/article/tamil-nadu-semiconductor-ev-manufacturing-hub",
            "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 2,
        },
        {
            "title": "Chennai Metro Phase 2: Historic under-river boring successfully completed beneath Adyar riverbed.",
            "title_ta": "சென்னை மெட்ரோ 2-ஆம் கட்டம்: அடையாறு ஆற்றின் அடிவழியே சுரங்கம் தோண்டும் பணி சாதனை வேகத்தில் நிறைவு!",
            "link_url": "/article/chennai-metro-phase-2-under-river-tunnel-success",
            "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 3,
        },
        {
            "title": "ISRO Gaganyaan Mission: Vyommitra humanoid robot ready for uncrewed orbital flight test.",
            "title_ta": "இஸ்ரோவின் ககன்யான் திட்டம்: வயோமித்ரா ரோபோவுடன் ஆளில்லா விண்வெளிப் பயண சோதனை விரைவில்!",
            "link_url": "/article/isro-gaganyaan-vyommitra-humanoid-space-mission",
            "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 4,
        },
        {
            "title": "TNPSC Job Notification: Over 4,800 vacancies announced with simplified Tamil eligibility exam.",
            "title_ta": "டிஎன்பிஎஸ்சி தேர்வுகள்: 4,800-க்கும் மேற்பட்ட அரசுப் பணிகளுக்கான அதிகாரப்பூர்வ அறிவிப்பு வெளியீடு!",
            "link_url": "/article/tnpsc-combined-civil-services-exam-notification",
            "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 5,
        },
        {
            "title": "Great Living Chola Temples: Special documentary on Brihadisvara 1,000-year engineering secrets.",
            "title_ta": "தஞ்சைப் பெருவுடையார் கோயில்: மாமன்னன் ராஜராஜ சோழனின் ஆயிரமாண்டு கட்டிடக்கலை சிறப்பு வரலாற்றுத் தொகுப்பு!",
            "link_url": "/article/great-living-chola-temples-architectural-marvel",
            "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
            "is_active": True,
            "order_index": 6,
        },
    ]

    for bn in breaking_news_list:
        b = BreakingNews(**bn)
        db.session.add(b)

    # 4. Rich News Articles
    articles_data = [
        # --- HISTORY ---
        {
            "title": "Keezhadi Phase 10: Sangam Era Industrial Engineering and International Trade Networks Unveiled",
            "title_ta": "கீழடி 10-ஆம் கட்டம்: சங்க கால தொழில் நுட்பமும் உலகளாவிய வணிகத் தொடர்புகளும் வெளிச்சத்திற்கு!",
            "slug": "keezhadi-phase-10-sangam-era-artifacts-discovered",
            "category_slug": "history",
            "author": "முனைவர் இரா. இளங்கோவன்",
            "author_ta": "முனைவர் இரா. இளங்கோவன்",
            "summary": "The latest findings at Keezhadi and Konthagai reveal sophisticated closed drainage channels, iron furnaces, and gemstone workshops dating back to the 6th century BCE.",
            "summary_ta": "கீழடி மற்றும் கொந்தகையில் சங்க கால மக்கள் பயன்படுத்திய நவீன வடிகால் அமைப்புகள், இரும்பு உருக்கு உலைகள் மற்றும் ரத்தின மணிகள் செய்யும் பட்டறைகள் கண்டுபிடிக்கப்பட்டுள்ளன.",
            "content": """
<p class="lead">சிவகங்கை மாவட்டம் திருப்புவனம் அருகே அமைந்துள்ள கீழடியில் நடைபெற்று வரும் 10-ஆம் கட்ட அகழாய்வு, தமிழக வரலாற்றின் பொற்காலப் பக்கங்களை மீண்டும் உலகிற்கு உரக்கச் சொல்லியுள்ளது. சமீபத்தில் தோண்டப்பட்ட ஆய்வுக் குழிகளில், சுடுமண்ணால் ஆன ஒன்றோடொன்று இணைக்கப்பட்ட 12 அடி நீள மூடிய வடிகால் குழாய்கள் மற்றும் நெசவுத் தொழிலுக்குப் பயன்படும் தக்ளி உள்ளிட்ட கருவிகள் வெளிவந்துள்ளன.</p>

<h3>பண்டைய தொழில் நகரத்தின் சான்றுகள்</h3>
<p>தொல்லியல் ஆய்வாளர்கள் மேற்கொண்ட ஆய்வில், கீழடி வெறும் குடியிருப்புகளுக்கான பகுதியாக மட்டும் இல்லாமல், பெரும் உற்பத்தி மற்றும் வர்த்தக மையமாகச் செயல்பட்டுள்ளது உறுதி செய்யப்பட்டுள்ளது. இங்கு கண்டெடுக்கப்பட்ட சூதுபவள மணிகள் (Carnelian Beads) பண்டைய பாரசீகம் மற்றும் குஜராத் பிராந்தியங்களுடனான ஆழ்கடல் வணிகத் தொடர்பை வெளிப்படுத்துகின்றன.</p>

<blockquote>"வைகை நதிக்கரை நாகரிகம் கி.மு. 6-ஆம் நூற்றாண்டிலேயே திட்டமிட்ட நகர அமைப்பையும், செழுமையான எழுத்தறிவு கொண்ட சமூக அமைப்பையும் கொண்டிருந்தது என்பதற்கு கீழடி அழியாத ஆவணமாகத் திகழ்கிறது." - தொல்லியல் துறை கண்காணிப்பாளர்</blockquote>

<h3>எழுத்தறிவும் தமிழ் பிராமியும்</h3>
<p>மண்பாண்ட ஓடுகளில் பொறிக்கப்பட்டுள்ள ஆதன், திசன், குவிரன் போன்ற பெயர்கள் தமிழ் பிராமி எழுத்துக்களில் மிகத் தெளிவாக வாசிக்கப்படுகின்றன. இக்கண்டுபிடிப்புகள் கீழடி நாகரிகம் சிந்து சமவெளி நாகரிகத்திற்கு இணையான பழமை வாய்ந்தது என்ற கருதுகோளுக்கு மேலும் வலுசேர்க்கின்றன.</p>

<p>அகழாய்வுத் தளத்தில் பொதுமக்களின் பார்வைக்காக அதிநவீன கீழடி அருங்காட்சியகம் நிறுவப்பட்டுள்ள நிலையில், அடுத்தகட்டமாக ஆழ்கடல் அகழாய்வுகளும் பூம்புகார் மற்றும் கொற்கை பகுதிகளில் தீவிரப்படுத்தப்படவுள்ளன.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "கீழடி அகழாய்வு தளத்தில் கண்டெடுக்கப்பட்ட சங்க கால பானை ஓடுகள் மற்றும் சுடுமண் கலயங்கள்.",
            "is_featured": True,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "வரலாறு, கீழடி, அகழாய்வு, சங்க காலம், வைகை நாகரிகம்",
            "days_ago": 1,
        },
        {
            "title": "The Great Living Chola Temples: Architectural Marvels of Brihadisvara and Gangaikonda Cholapuram",
            "title_ta": "மாமன்னன் ராஜராஜனின் தஞ்சைப் பெருவுடையார் கோயில்: ஆயிரமாண்டு தமிழரின் கட்டிடக்கலை அற்புதம்",
            "slug": "great-living-chola-temples-architectural-marvel",
            "category_slug": "history",
            "author": "சு. வெங்கடேசன் ஆய்வுக் குழு",
            "author_ta": "சு. வெங்கடேசன் ஆய்வுக் குழு",
            "summary": "Exploring the scientific precision, acoustic engineering, and granitic grandeur of UNESCO World Heritage Chola monuments.",
            "summary_ta": "யுனெஸ்கோ உலகப் பாரம்பரிய சின்னமான தஞ்சை பெரிய கோயிலின் வானியல் துல்லியம் மற்றும் 80 டன் எடை கொண்ட குடக் கல்லின் கட்டிடக்கலை ரகசியங்கள்.",
            "content": """
<p class="lead">தஞ்சை மண்ணில் கம்பீரமாக விண்ணை முட்டி நிற்கும் பெருவுடையார் திருக்கோயில், தமிழரின் கட்டிடக்கலைத் திறனுக்கும், கணித ஆளுமைக்கும் ஒரு மாபெரும் எடுத்துக்காட்டாகும். கி.பி. 1010-ல் மாமன்னன் ராஜராஜ சோழனால் கட்டி முடிக்கப்பட்ட இந்த விஸ்வகர்ம சாதனை, ஆயிரம் ஆண்டுகளைக் கடந்தும் நிலநடுக்கங்களைத் தாங்கி கம்பீரமாக நிற்கிறது.</p>

<h3>விமானத்தின் தனித்துவமும் நிழலின் தத்துவமும்</h3>
<p>216 அடி உயரம் கொண்ட இக்கோயிலின் விமானம் முழுவதுமாக கருங்கற்களால் பிணைக்கப்பட்டு அமைக்கப்பட்டுள்ளது. சமவெளியான காவிரிப்படுகையில் எவ்வித கருங்கல் குன்றுகளும் இல்லாத சூழலில், திருச்சி நார்த்தாமலையிலிருந்து நூற்றுக்கணக்கான யானைகளின் துணையுடன் பெரும் பாறைகள் கொண்டுவரப்பட்டன.</p>

<p>கோபுர உச்சியில் பொருத்தப்பட்டுள்ள 80 டன் எடை கொண்ட ஒற்றைக் கல் கலசமானது, நவீன கிரேன் போன்ற கனரக எந்திரங்கள் இல்லாத காலகட்டத்தில், சாரப்பள்ளம் என்னும் கிராமத்திலிருந்து பல மைல் நீள சாய்வுப் பாதை அமைத்து மேலே ஏற்றப்பட்டது என்பது வியப்பளிக்கும் பொறியியல் சாதனை.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "தஞ்சாவூர் பெருவுடையார் கோயிலின் பிரம்மாண்ட விமானக் காட்சி.",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "தஞ்சை, சோழர், வரலாறு, கட்டிடக்கலை, யுனெஸ்கோ",
            "days_ago": 4,
        },
        # --- TAMIL NADU ---
        {
            "title": "Tamil Nadu Emerges as India’s Semiconductor and EV Manufacturing Hub with Mega Investments",
            "title_ta": "இந்தியாவின் மின்வாகனம் மற்றும் செமிகண்டக்டர் தலைநகராக உருவெடுக்கும் தமிழ்நாடு: சர்வதேச முதலீடுகள் குவிப்பு",
            "slug": "tamil-nadu-semiconductor-ev-manufacturing-hub",
            "category_slug": "tamil-nadu",
            "author": "பொருளாதாரப் பிரிவு செய்தியாளர்",
            "author_ta": "பொருளாதாரப் பிரிவு செய்தியாளர்",
            "summary": "With over 40% of India’s electric two-wheelers produced in Hosur and Sriperumbudur, Tamil Nadu attracts major electronics giants.",
            "summary_ta": "ஓசூர், திருப்பெரும்புதூர் தொழில் வழித்தடங்களில் புதிய சிப் வடிவமைப்பு மற்றும் பேட்டரி உற்பத்தி ஆலைகள் அமைக்க உலக நிறுவனங்கள் ஒப்பந்தம்.",
            "content": """
<p class="lead">இந்தியாவின் முன்னணி தொழில்துறை மாநிலங்களில் முதன்மையாகத் திகழும் தமிழ்நாடு, தற்போது மின்னணு மற்றும் மின்வாகன (EV) உற்பத்தியில் உலகளாவிய கவனத்தைப் பெற்றுள்ளது. ஓசூர் முதல் கோவை வரையிலான தொழிற்பேட்டைகளில் உருவாகியுள்ள நவீன உள்கட்டமைப்புகள் சர்வதேச முதலீட்டாளர்களை வெகுவாக ஈர்த்துள்ளன.</p>

<h3>1 டிரில்லியன் டாலர் பொருளாதார இலக்கு</h3>
<p>2030-ஆம் ஆண்டிற்குள் 1 டிரில்லியன் அமெரிக்க டாலர் பொருளாதாரத்தை எட்டும் தமிழக அரசின் தொலைநோக்குப் பார்வையின் அங்கமாக, புதிய 'செமிகண்டக்டர் கொள்கை 2024' தீவிரமாக நடைமுறைப்படுத்தப்பட்டு வருகிறது. இதன் மூலம் 25,000-க்கும் மேற்பட்ட உயர்தொழில்நுட்ப வேலைவாய்ப்புகள் இளைஞர்களுக்கு உருவாகும் என எதிர்பார்க்கப்படுகிறது.</p>

<ul>
<li>ஓசூரில் சர்வதேச தரத்திலான பேட்டரி உற்பத்தி வளாகம்</li>
<li>சென்னை அருகே அமையவுள்ள சிப் வடிவமைப்பு ஆராய்ச்சி மையம்</li>
<li>தென் மாவட்டங்களில் நவீன சோலார் மின் பூங்காக்கள்</li>
</ul>
""",
            "featured_image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "நவீன தானியங்கி தொழில் ஆலையில் மின்வாகன அசெம்பிளி பணிகள்.",
            "is_featured": True,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "தமிழ்நாடு, பொருளாதாரம், மின்வாகனம், வேலைவாய்ப்பு, தொழில்",
            "days_ago": 0,
        },
        {
            "title": "Chennai Metro Phase 2 Tunneling Milestone Achieved: Under-River Boring Completed Near Adyar",
            "title_ta": "சென்னை மெட்ரோ 2-ஆம் கட்டம்: அடையாறு ஆற்றுக்கு அடியில் சுரங்கம் தோண்டும் பணி சாதனை வேகத்தில் நிறைவு",
            "slug": "chennai-metro-phase-2-under-river-tunnel-success",
            "category_slug": "tamil-nadu",
            "author": "நகர விவகாரங்கள் பிரிவு",
            "author_ta": "நகர விவகாரங்கள் பிரிவு",
            "summary": "The 118.9 km Phase 2 network takes a monumental leap as the tunnel boring machine cuts through hard rock beneath the Adyar riverbed.",
            "summary_ta": "அடையாறு ஆற்றுப் படுகைக்குக் கீழே 22 மீட்டர் ஆழத்தில் கடின பாறைகளைக் குடைந்து வெளிவந்த நவீன சுரங்கக் குடையும் எந்திரம்.",
            "content": """
<p class="lead">சென்னை மாநகர மக்களின் போக்குவரத்து நெரிசலைக் குறைக்கும் 63,246 கோடி ரூபாய் மதிப்பிலான சென்னை மெட்ரோ இரண்டாம் கட்டப் பணிகள் விறுவிறுப்பாக நடைபெற்று வருகின்றன. இதில் முக்கிய மைல்கல்லாக அடையாறு ஆற்றின் அடிவழியே சுரங்கம் அமைக்கும் பணி வெற்றிகரமாக முடிவடைந்துள்ளது.</p>

<p>அடையாறு சந்திப்பு முதல் பசுமைவழிச் சாலை வரை ஆற்றுப் படுகைக்குக் கீழே அதிநவீன டனல் போரிங் மெஷின் (TBM) மூலம் இந்த சுரங்கப்பாதை தோண்டப்பட்டுள்ளது. நிலத்தடி நீர் கசிவு ஏற்படாதவாறு உயர் பாதுகாப்பு வளையங்கள் பொருத்தப்பட்டுள்ளன.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "சென்னை மெட்ரோ சுரங்கப் பாதை அமைக்கும் பணியின் களக் காட்சி.",
            "is_featured": False,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "சென்னை, மெட்ரோ, உள்கட்டமைப்பு, தமிழ்நாடு",
            "days_ago": 2,
        },
        # --- INDIA ---
        {
            "title": "ISRO Prepares for Gaganyaan Uncrewed Test Flight with Vyommitra Humanoid Robot",
            "title_ta": "ககன்யான் விண்கல சோதனைக்கு தயாராகும் இஸ்ரோ: வயோமித்ரா ரோபோவுடன் ஆளில்லா விண்வெளிப் பயணம்",
            "slug": "isro-gaganyaan-vyommitra-humanoid-space-mission",
            "category_slug": "india",
            "author": "விண்வெளி ஆய்வு நிருபர்",
            "author_ta": "விண்வெளி ஆய்வு நிருபர்",
            "summary": "India takes a giant leap toward human spaceflight as ISRO integrates life-support modules and AI-driven telemetry for Gaganyaan G1 mission.",
            "summary_ta": "மனிதர்களை விண்வெளிக்கு அனுப்பும் இந்தியாவின் வரலாற்று சிறப்புமிக்க ககன்யான் திட்டத்தின் முதற்கட்ட ஆளில்லா சோதனை ஓட்டம் விரைவில் தொடங்குகிறது.",
            "content": """
<p class="lead">இந்திய விண்வெளி ஆராய்ச்சி நிறுவனம் (இஸ்ரோ) தனது மிக முக்கியமான கனவுத் திட்டமான ‘ககன்யான்’ விண்வெளி பயணத்திற்கான இறுதிக்கட்ட சோதனைகளை ஸ்ரீஹரிகோட்டாவில் முடுக்கிவிட்டுள்ளது. மனிதர்களை விண்வெளிக்கு பாதுகாப்பாக அனுப்பி மீண்டும் பூமிக்கு அழைத்து வரும் தொழில்நுட்பத்தை இந்தியா இதன் மூலம் மெய்ப்பிக்க உள்ளது.</p>

<h3>வயோமித்ரா ரோபோவின் பங்கு</h3>
<p>மனித உடலின் துடிப்பு, இதயத்துடிப்பு, விண்கலத்தின் வெப்பநிலை மற்றும் கதிர்வீச்சுத் தாக்கங்களைக் கண்காணித்து ஆய்வு செய்ய ‘வயோமித்ரா’ என்ற பெண்குரல் கொண்ட செயற்கை நுண்ணறிவு ரோபோ இந்த முதல் சோதனையில் பயணிக்கிறது.</p>

<p>ஸ்ரீஹரிகோட்டா சதீஷ் தவான் ஏவுதளத்திலிருந்து எல்.வி.எம்-3 (LVM3) ராக்கெட் மூலம் விண்கலம் விண்ணில் செலுத்தப்படும். விண்கலம் பூமியிலிருந்து 400 கி.மீ உயரத்தில் 3 நாட்கள் சுற்றி வந்து வங்காள விரிகுடா கடலில் பத்திரமாக தரை இறக்கப்படும்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "பூமிக்கு மேலே விண்வெளிச் சுழற்சி மற்றும் செயற்கைக்கோள் செயல்பாடு.",
            "is_featured": True,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "இஸ்ரோ, இந்தியா, ககன்யான், அறிவியல், விண்வெளி",
            "days_ago": 1,
        },
        {
            "title": "Supreme Court Verdict on Digital Privacy: Mandates Stricter Consent and Data Localization Norms",
            "title_ta": "டிஜிட்டல் தனிநபர் தகவல் பாதுகாப்பு: உச்சநீதிமன்றம் புதிய வழிகாட்டுதல்கள் மற்றும் நெறிமுறைகள் வெளியீடு",
            "slug": "supreme-court-verdict-digital-privacy-guidelines",
            "category_slug": "india",
            "author": "சட்ட விவகாரங்கள் ஆசிரியர் குழு",
            "author_ta": "சட்ட விவகாரங்கள் ஆசிரியர் குழு",
            "summary": "Constitutional bench emphasizes citizens’ fundamental right to privacy, instructing tech platforms to stop unsolicited commercial telemarketing and surveillance.",
            "summary_ta": "குடிமக்களின் அனுமதியின்றி அவர்களின் தொலைபேசி எண்கள், தனிப்பட்ட தரவுகளை வணிக நிறுவனங்கள் பயன்படுத்தக் கூடாது என உச்சநீதிமன்றம் உத்தரவு.",
            "content": """
<p class="lead">இந்திய அரசியலமைப்புச் சட்டம் பிரிவு 21-ன் கீழ் வழங்கப்பட்டுள்ள தனிநபர் சுதந்திரம் மற்றும் கண்ணியமான வாழ்வுரிமையில் டிஜிட்டல் ரகசியத்தன்மையும் அடங்கும் என உச்சநீதிமன்ற அரசியல் சாசன அமர்வு வரலாற்றுத் தீர்ப்பை வழங்கியுள்ளது.</p>

<p>ஸ்மார்ட்போன் செயலிகள் தேவையற்ற அனுமதிகளை (Permissions) பயனர்களிடமிருந்து கட்டாயப்படுத்தி பெறுவதை உடனடியாகத் தடை செய்யுமாறு தொலைத்தொடர்பு மற்றும் தகவல் தொழில்நுட்ப அமைச்சகத்திற்கு நீதிமன்றம் அறிவுறுத்தியுள்ளது.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "உச்சநீதிமன்ற நீதி வளாகம் மற்றும் சட்ட நெறிமுறைகள்.",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "உச்சநீதிமன்றம், சட்டம், இந்தியா, தனிநபர் பாதுகாப்பு",
            "days_ago": 3,
        },
        # --- WORLD ---
        {
            "title": "Global Climate Summit 2026: Island Nations Demand Binding Renewable Energy Deadlines",
            "title_ta": "உலக காலநிலை மாநாடு: கடல்மட்ட உயர்வால் தீவு நாடுகள் அவசர உதவி மற்றும் நிதி ஒதுக்கீடு கோரிக்கை",
            "slug": "global-climate-summit-renewable-energy-commitments",
            "category_slug": "world",
            "author": "சர்வதேச செய்தியாளர் டேவிட்",
            "author_ta": "சர்வதேச செய்தியாளர் டேவிட்",
            "summary": "Rising ocean temperatures and unprecedented melting of Arctic ice spark heated negotiations in Geneva on global loss and damage funds.",
            "summary_ta": "புவி வெப்பமயமாதலால் பசிபிக் பெருங்கடல் தீவு நாடுகளுக்கு ஏற்பட்டுள்ள ஆபத்துகளைத் தவிர்க்க சர்வதேச நாடுகள் உடனடி நடவடிக்கை எடுக்க வலியுறுத்தல்.",
            "content": """
<p class="lead">சுவிட்சர்லாந்தின் ஜெனீவாவில் கூடியுள்ள உலக சுற்றுச்சூழல் மாநாட்டில், கடல்மட்டம் உயர்வதால் நிலப்பரப்புகளை இழந்துவரும் பசிபிக் மற்றும் இந்தியப் பெருங்கடல் தீவு நாடுகள் தங்கள் அதிருப்தியையும் கவலையையும் தீவிரமாக பதிவு செய்துள்ளன.</p>

<p>கரிம உமிழ்வை 2030-க்குள் 45 சதவீதம் குறைக்கத் தவறினால், உலகளாவிய உணவுப் பாதுகாப்பு மற்றும் கடலோர நகரங்களின் வாழ்வியல் கடுமையாக பாதிக்கப்படும் என ஐக்கிய நாடுகள் சபையின் பொதுச்செயலாளர் எச்சரிக்கை விடுத்துள்ளார்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "கடற்கரை மற்றும் பருவநிலை மாற்றத்தின் தாக்கம்.",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "உலகம், காலநிலை, சுற்றுச்சூழல், ஐ.நா",
            "days_ago": 2,
        },
        {
            "title": "James Webb Space Telescope Detects Atmospheric Water Vapor on Habitable-Zone Exoplanet",
            "title_ta": "ஜேம்ஸ் வெப் விண்வெளி தொலைநோக்கியின் புதிய கண்டுபிடிப்பு: உயிர்வாழத் தகுதியான புதிய கிரகத்தில் நீராவி மண்டலம்!",
            "slug": "james-webb-space-telescope-exoplanet-water-vapor",
            "category_slug": "world",
            "author": "விஞ்ஞான உலக நிருபர்",
            "author_ta": "விஞ்ஞான உலக நிருபர்",
            "summary": "NASA and ESA astronomers celebrate a historic breakthrough as spectroscopic analysis confirms presence of carbon molecules and water vapor.",
            "summary_ta": "பூமியிலிருந்து 120 ஒளி ஆண்டுகள் தொலைவில் அமைந்துள்ள K2-18b கிரகத்தில் கார்பன் மூலக்கூறுகள் மற்றும் நீராவி இருப்பதை விஞ்ஞானிகள் உறுதிப்படுத்தியுள்ளனர்.",
            "content": """
<p class="lead">மனிதகுலம் பல தலைமுறைகளாக விடை தேடி வரும் "இந்த பிரபஞ்சத்தில் நாம் தனித்து வாழ்கிறோமா?" என்ற வரலாற்று கேள்விக்கு விடை தேடும் பயணத்தில் ஜேம்ஸ் வெப் தொலைநோக்கி ஒரு மிகப்பெரிய மைல்கல்லை எட்டியுள்ளது.</p>

<p>நமது சூரிய மண்டலத்திற்கு அப்பால் அமைந்துள்ள ஒரு கோளின் வளிமண்டலத்தை ஊடுருவி ஆய்வு செய்ததில், அங்கு கடல் போன்ற பரந்த நீர்நிலைகள் மற்றும் உயிரினங்களின் சுவாசத்திற்கு சாதகமான வாயுக்கள் இருக்கக்கூடும் என்று நாசா வானியலாளர்கள் கணித்துள்ளனர்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "விண்வெளியில் தொலைதூர நட்சத்திர மண்டலம் மற்றும் கிரகங்களின் தோற்றம்.",
            "is_featured": True,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "நாசா, அறிவியல், உலகம், ஜேம்ஸ் வெப், வானியல்",
            "days_ago": 4,
        },
        # --- CINEMA ---
        {
            "title": "Kollywood’s Next Big Leap: Epic Historical Drama Begins Production with Global Crew",
            "title_ta": "தமிழ் சினிமாவின் பிரம்மாண்ட வரலாற்று திரைப்படம்: சர்வதேச தொழில்நுட்பக் கலைஞர்களுடன் படப்பிடிப்பு ஆரம்பம்",
            "slug": "kollywood-next-big-leap-epic-historical-film",
            "category_slug": "cinema",
            "author": "திரைவிமர்சகர் கண்ணன்",
            "author_ta": "திரைவிமர்சகர் கண்ணன்",
            "summary": "An international co-production chronicling the maritime conquests of Tamil rulers kicks off in Ramnad with cutting-edge IMAX cameras.",
            "summary_ta": "சோழப் பேரரசின் கடல்வழிப் பயணங்களை மையமாகக் கொண்டு உருவாகும் புதிய பான்-இந்தியா திரைப்படத்தின் பிரம்மாண்ட அரங்கம் திறப்பு.",
            "content": """
<p class="lead">தமிழ் சினிமா உலக அரங்கில் தொடர்ந்து தனது ஆதிக்கத்தை விரிவுபடுத்தி வரும் சூழலில், தமிழரின் கடல்வழி வணிகத்தையும் வீரத்தையும் பறைசாற்றும் புதிய வரலாற்றுப் பின்னணி கொண்ட திரைப்படத்தின் படப்பிடிப்பு ராமநாதபுரம் கடற்கரையில் கோலாகலமாக துவங்கியுள்ளது.</p>

<p>ஹாலிவுட்டின் முன்னணி ஆக்‌ஷன் இயக்குநர்கள் மற்றும் ஆஸ்கர் விருது வென்ற இந்திய இசையமைப்பாளர் இணையும் இத்திரைப்படம், அடுத்த ஆண்டு தீபாவளிக்கு 5 உலக மொழிகளில் ரிலீசாக திட்டமிடப்பட்டுள்ளது.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "திரையரங்கில் ஒளி மற்றும் ஒலியின் வசீகரிக்கும் சினிமா அனுபவம்.",
            "is_featured": False,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "சினிமா, கோலிவுட், திரைப்படம், தமிழ் சினிமா",
            "days_ago": 1,
        },
        {
            "title": "Music Maestro’s Golden Jubilee Concert World Tour Announced: London to Chennai Special Shows",
            "title_ta": "இசைஞானியின் 50 ஆண்டு பொன்விழா உலக இசைச் சுற்றுப்பயணம்: லண்டன் முதல் சென்னை வரை பிரம்மாண்ட மேடைகள்",
            "slug": "music-maestro-golden-jubilee-world-tour",
            "category_slug": "cinema",
            "author": "இசைப்பிரிவு நிருபர்",
            "author_ta": "இசைப்பிரிவு நிருபர்",
            "summary": "Fans rejoice as the legendary composer announces live symphony orchestra performances featuring 100 musicians across five continents.",
            "summary_ta": "ஆயிரக்கணக்கான ரசிகர்களை மெய்மறக்க வைக்கும் வகையில் 100 சிம்பொனி இசைக் கலைஞர்களுடன் நேரலை இசை நிகழ்ச்சி அட்டவணை வெளியீடு.",
            "content": """
<p class="lead">தமிழ் திரைப்பட இசையின் நாடித் துடிப்பாக அரை நூற்றாண்டு காலம் விளங்கும் இசைக்கலைஞரின் 50-வது ஆண்டு பொன்விழாவை முன்னிட்டு, உலகெங்கும் வாழும் தமிழ் ரசிகர்களை மகிழ்விக்கும் மாபெரும் உலக இசைச் சுற்றுப்பயணம் அதிகாரப்பூர்வமாக அறிவிக்கப்பட்டுள்ளது.</p>

<p>லண்டன் ராயல் ஆல்பர்ட் ஹால், பாரிஸ், சிங்கப்பூர், மலேசியா மற்றும் சென்னையில் இந்த பிரம்மாண்ட நேரடி இசை நிகழ்ச்சிகள் நடைபெறவுள்ளன.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "இசைக்கலைஞர்களின் மேடை நேரலை இசைக்கச்சேரி நிகழ்வு.",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "இசை, சினிமா, இசைக்கச்சேரி, கோலிவுட்",
            "days_ago": 3,
        },
        # --- JOBS ---
        {
            "title": "TNPSC Combined Civil Services Exam 2026: 4,800 Vacancies Announced with Simplified Syllabus",
            "title_ta": "டிஎன்பிஎஸ்சி குரூப் 4 மற்றும் 2 தேர்வுகள்: 4,800 காலிப்பணியிடங்கள் அறிவிப்பு - முழு விவரங்கள்!",
            "slug": "tnpsc-combined-civil-services-exam-notification",
            "category_slug": "jobs",
            "author": "வேலைவாய்ப்பு வழிகாட்டல் மையம்",
            "author_ta": "வேலைவாய்ப்பு வழிகாட்டல் மையம்",
            "summary": "Comprehensive guide on eligibility criteria, exam patterns, Tamil qualification mandatory test, and online application deadlines.",
            "summary_ta": "தமிழக அரசுத் துறைகளில் கிராம நிர்வாக அலுவலர் (VAO), இளநிலை உதவியாளர் உள்ளிட்ட பணியிடங்களுக்கான கல்வித் தகுதி மற்றும் விண்ணப்பிக்கும் முறை.",
            "content": """
<p class="lead">தமிழ்நாடு அரசுப் பணியாளர் தேர்வாணையம் (TNPSC) இளைஞர்களுக்கு நல்வாய்ப்பாக 4,800-க்கும் மேற்பட்ட அரசுப் பணிகளுக்கான புதிய அதிகாரப்பூர்வ அறிவிக்கையை வெளியிட்டுள்ளது. 10-ஆம் வகுப்பு தேர்ச்சி பெற்றவர்கள் முதல் பட்டதாரிகள் வரை விண்ணப்பிக்கலாம்.</p>

<h3>முக்கிய தேதிகள் மற்றும் தகுதிகள்:</h3>
<ul>
<li>ஆன்லைன் விண்ணப்ப தொடக்க நாள்: இந்த மாதம் 15</li>
<li>விண்ணப்பிக்க கடைசி நாள்: அடுத்த மாதம் 14</li>
<li>தமிழ் தகுதித் தேர்வு: 100 மதிப்பெண்களுக்கு கட்டாயம்</li>
<li>பொது அறிவு மற்றும் கணிதப் பகுதி: 100 மதிப்பெண்கள்</li>
</ul>

<p>தேர்வர்கள் www.tnpsc.gov.in என்ற அதிகாரப்பூர்வ இணையதளம் மூலம் ஒருமுறை பதிவு (OTR) செய்து உடனடியாக விண்ணப்பிக்கலாம். மாதிரி வினாத்தாள்கள் மற்றும் முந்தைய ஆண்டு விடைக்குறிப்புகளை மாணவர்கள் பதிவிறக்கம் செய்து பயிற்சி பெறலாம்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "தேர்வுக்கான தயாரிப்பு மற்றும் படிப்பகத்தில் கற்கும் மாணவர்கள்.",
            "is_featured": True,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "டிஎன்பிஎஸ்சி, வேலைவாய்ப்பு, அரசுப்பணி, தேர்வு",
            "days_ago": 0,
        },
        {
            "title": "Top Tech Hiring Trends in Chennai and Coimbatore: High Demand for AI Engineers & Full Stack Developers",
            "title_ta": "சென்னை மற்றும் கோவையில் ஐடி நிறுவனங்களின் வேலைவாய்ப்பு முகாம்கள்: AI மற்றும் கிளவுட் என்ஜினீயர்களுக்கு மவுசு",
            "slug": "tech-hiring-trends-chennai-coimbatore-ai-engineers",
            "category_slug": "jobs",
            "author": "தொழில்நுட்ப மனிதவளப் பிரிவு",
            "author_ta": "தொழில்நுட்ப மனிதவளப் பிரிவு",
            "summary": "Global Capability Centers (GCCs) in Tamil Nadu plan to hire over 35,000 engineering and science graduates this fiscal year.",
            "summary_ta": "சென்னையின் ஓ.எம்.ஆர் மற்றும் சிறுசேரி ஐடி காரிடாரில் புதிய குளோபல் சென்டர்கள் துவக்கம்; லட்சங்களில் சம்பளம் பெறும் மென்பொருள் வல்லுநர்கள்.",
            "content": """
<p class="lead">உலகளாவிய மென்பொருள் மற்றும் தொழில்நுட்ப சூழலில் செயற்கை நுண்ணறிவு (AI), சைபர் செக்யூரிட்டி மற்றும் டேட்டா சயின்ஸ் துறைகளில் நிபுணத்துவம் கொண்ட இளைஞர்களுக்கான தேவை முன்னெப்போதும் இல்லாத அளவுக்கு உயர்ந்துள்ளது.</p>

<p>சென்னையில் இயங்கும் 150-க்கும் மேற்பட்ட பார்ச்சூன் 500 நிறுவனங்களின் குளோபல் மையங்கள் தமிழக கல்லூரி வளாகங்களில் நேரடியாக நேர்காணல் நடத்தி லட்சங்களில் ஊதியத்துடன் பணியமர்த்த திட்டமிட்டுள்ளன.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "நவீன மென்பொருள் நிறுவனத்தில் குழு விவாதம் மற்றும் தயாரிப்பு.",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "வேலைவாய்ப்பு, ஐடி, பொறியியல், சென்னை, கேம்பஸ்",
            "days_ago": 3,
        },
        # --- YOUTUBE / VIDEO ---
        {
            "title": "Special Documentary: Journey Through Keezhadi Excavations and 2600-Year-Old Vaigai Civilisation",
            "title_ta": "சிறப்பு ஆவணப்படம்: 2600 ஆண்டுகள் பழமையான கீழடி வைகை நதிக்கரை நாகரிகத்தின் கள ஆய்வு!",
            "slug": "documentary-journey-through-keezhadi-civilisation",
            "category_slug": "youtube",
            "author": "விதை வீடியோ ஆவணக் குழு",
            "author_ta": "விதை வீடியோ ஆவணக் குழு",
            "summary": "Watch our exclusive in-depth 4K documentary uncovering the scientific evidence of urban planning, drainage, and literacy in ancient Tamil Nadu.",
            "summary_ta": "கீழடி அகழாய்வு தளத்திற்கு நேரில் சென்று தொல்லியல் வல்லுநர்களுடன் விதை இயக்க குழுவினர் பதிவு செய்த வரலாற்று ஆவணப்படம்.",
            "content": """
<p class="lead">விதை இயக்கம் வழங்கும் சிறப்பு வரலாற்று வீடியோ ஆவணம்! கீழடி மற்றும் அதன் சுற்றியுள்ள கொந்தகை, மணலூர், அகரம் ஆகிய பகுதிகளில் நடைபெற்ற வரலாற்று சிறப்புமிக்க அகழாய்வுப் பணிகளை எங்கள் கேமராக்கள் மிக நெருக்கமாகப் படம் பிடித்துள்ளன.</p>

<p>கீழே உள்ள காணொளியைப் பார்த்து, உங்கள் வரலாற்று அறிவை வளர்த்துக்கொள்ளுங்கள். உங்கள் கருத்துக்களை வீடியோவில் பகிருங்கள்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "கீழடி சிறப்பு வரலாற்று ஆவணப் படத்தின் வீடியோ காட்சி.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Sample video ID embed
            "is_featured": True,
            "is_trending": True,
            "status": "published",
            "views": 0,
            "tags": "வீடியோ, யூடியூப், கீழடி, ஆவணப்படம், வரலாறு",
            "days_ago": 2,
        },
        {
            "title": "Expert Analysis: How to Clear TNPSC Group 1 & 2 in Your First Attempt - Full Interview",
            "title_ta": "நேர்காணல்: முதல் முயற்சியிலேயே டிஎன்பிஎஸ்சி தேர்வில் மாநில அளவில் வெல்வது எப்படி? வெற்றியாளரின் வழிகாட்டல்!",
            "slug": "expert-interview-how-to-clear-tnpsc-first-attempt",
            "category_slug": "youtube",
            "author": "விதை கல்வி நிருபர்",
            "author_ta": "விதை கல்வி நிருபர்",
            "summary": "State rank holder shares daily study routine, notes-making strategy, book list, and interview preparation secrets in this masterclass.",
            "summary_ta": "கிராமப்புற மாணவர்களுக்கான பிரத்யேக தேர்வு உத்திகள், வாசிக்க வேண்டிய நூல்கள் மற்றும் நேர மேலாண்மை குறித்த முழுமையான வீடியோ கலந்துரையாடல்.",
            "content": """
<p class="lead">அரசுப் பணி கனவோடு உழைக்கும் லட்சக்கணக்கான தமிழக மாணவர்களுக்காக விதை இயக்கம் தயாரித்துள்ள பிரத்யேக வழிகாட்டல் நேர்காணல் காணொளி இது.</p>

<p>தினசரி எத்தனை மணி நேரம் படிக்க வேண்டும், பாடத்திட்டத்தை எவ்வாறு அணுகுவது, தமிழ் இலக்கணம் மற்றும் பொது அறிவை எவ்வாறு சுலபமாக நினைவில் வைத்துக்கொள்வது போன்ற ஆலோசனைகளை இதில் விரிவாகக் காணலாம்.</p>
""",
            "featured_image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
            "image_caption": "தொழில் வழிகாட்டல் மற்றும் கல்வி நேர்காணல் காட்சி.",
            "video_url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "is_featured": False,
            "is_trending": False,
            "status": "published",
            "views": 0,
            "tags": "யூடியூப், கல்வி, டிஎன்பிஎஸ்சி, நேர்காணல், வழிகாட்டல்",
            "days_ago": 5,
        },
    ]

    now = datetime.now(UTC)
    for art_info in articles_data:
        cat_slug = art_info.pop("category_slug")
        days_ago = art_info.pop("days_ago", 0)
        published_time = now - timedelta(days=days_ago, hours=random.randint(1, 10))

        art = Article(
            category_id=cat_map[cat_slug].id,
            published_at=published_time,
            created_at=published_time,
            **art_info,
        )
        db.session.add(art)

    # 5. Default Website Settings
    settings_data = {
        "site_name_en": "Vithaigal Iyakkam",
        "site_name_ta": "விதைகள் இயக்கம்",
        "site_tagline_en": "The Voice of Truth, Heritage and Progress",
        "site_tagline_ta": "உண்மை, மரபு மற்றும் முன்னேற்றத்தின் மக்கள் குரல்",
        "site_email": "contact@vithaigaliyakkam.org",
        "site_phone": "+91 94430 12345",
        "site_address_en": "Anna Salai, Thousand Lights, Chennai, Tamil Nadu - 600006",
        "site_address_ta": "அண்ணா சாலை, ஆயிரம் விளக்கு, சென்னை, தமிழ்நாடு - 600006",
        "site_about_en": "Vithaigal Iyakkam is an independent digital news publishing and media platform committed to unbiased journalism, Tamil cultural heritage, youth career guidance, and progressive socio-economic discourse.",
        "site_about_ta": "விதைகள் இயக்கம் என்பது நடுநிலையான செய்தி இதழியல், தமிழ் மரபு மீட்பு, இளைஞர்களுக்கான வேலைவாய்ப்பு வழிகாட்டல் மற்றும் முற்போக்கு சமூகச் சிந்தனைகளை மக்களிடம் கொண்டு சேர்க்கும் முன்னணி டிஜிட்டல் ஊடகமாகும்.",
        "social_facebook": "https://facebook.com/vithaigaliyakkam",
        "social_twitter": "https://twitter.com/vithaigaliyakkam",
        "social_youtube": "https://youtube.com/@vithaigaliyakkam",
        "social_instagram": "https://instagram.com/vithaigaliyakkam",
        "social_whatsapp": "https://whatsapp.com/channel/vithaigaliyakkam",
        "breaking_news_enabled": "true",
        "allow_comments": "true",
    }

    for k, v in settings_data.items():
        db.session.add(WebsiteSetting(key=k, value=v))

    # 6. Sample Contact Message for immediate admin dashboard preview
    msg = ContactMessage(
        name="மு. சுந்தரபாண்டியன்",
        email="sundar.p@gmail.com",
        subject="கீழடி வரலாற்று கட்டுரைகள் பாராட்டு",
        message="வணக்கம்! உங்கள் விதை இயக்கம் இணையதளத்தில் வெளியாகும் கீழடி மற்றும் சங்க கால வரலாற்று கட்டுரைகள் மாணவர்களுக்கும் பொதுமக்களுக்கும் அளப்பரிய பயனைத் தருகின்றன. தொடர்ந்து இதுபோன்ற சிறப்புக் கட்டுரைகளை வெளியிடுங்கள். வாழ்த்துகள்!",
        is_read=False,
        created_at=datetime.now(UTC) - timedelta(hours=6),
    )
    db.session.add(msg)

    # 7. Sample Newsletter Subscriber
    sub = NewsletterSubscriber(
        email="reader.tamilnews@gmail.com",
        is_active=True,
        subscribed_at=datetime.now(UTC) - timedelta(days=2),
    )
    db.session.add(sub)

    db.session.commit()
    print("Database seeding completed successfully!")
