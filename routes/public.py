import uuid
from datetime import UTC, datetime

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import and_, or_

from database import db
from database.models import (
    Article,
    ArticleView,
    Bookmark,
    BreakingNews,
    Category,
    ContactMessage,
    NewsletterSubscriber,
    WebsiteSetting,
)

public_bp = Blueprint("public", __name__)


def get_session_token():
    """Ensure a persistent anonymous visitor token for bookmarking and views."""
    if "visitor_token" not in session:
        session["visitor_token"] = str(uuid.uuid4())
    return session["visitor_token"]


@public_bp.context_processor
def inject_global_data():
    """Inject global navigation and layout data into all templates."""
    categories = Category.query.order_by(Category.order_index.asc()).all()
    breaking_items = (
        BreakingNews.query.filter_by(is_active=True)
        .order_by(BreakingNews.order_index.asc())
        .all()
    )

    # Session language (default to Tamil 'ta' with English toggle)
    current_lang = session.get("lang", "ta")

    # Bookmarks count
    v_token = get_session_token()
    b_count = Bookmark.query.filter_by(session_id=v_token).count()

    # Settings dictionary
    all_settings = WebsiteSetting.query.all()
    settings_dict = {s.key: s.value for s in all_settings}

    return {
        "nav_categories": categories,
        "global_breaking_news": breaking_items,
        "current_lang": current_lang,
        "bookmark_count": b_count,
        "settings": settings_dict,
        "now": datetime.now(UTC),
    }


@public_bp.route("/set-language/<lang>")
def set_language(lang):
    """Switch site display language between Tamil ('ta') and English ('en')."""
    if lang in ["ta", "en"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.index"))


@public_bp.route("/")
def index():
    """Main Homepage with hero grid, latest news, category blocks, videos, trending."""
    # Strict rule: Editorial text slots only feature standard non-video articles.
    # Videos belong exclusively to the dedicated video gallery and /category/youtube.
    non_video_filter = and_(
        or_(Article.video_url.is_(None), Article.video_url == ""),
        ~Article.category.has(slug="youtube"),
    )

    # Main hero featured article
    featured_lead = (
        Article.query.filter(
            Article.status == "published",
            Article.is_featured.is_(True),
            non_video_filter,
        )
        .order_by(Article.published_at.desc())
        .first()
    )

    if not featured_lead:
        featured_lead = (
            Article.query.filter(Article.status == "published", non_video_filter)
            .order_by(Article.published_at.desc())
            .first()
        )

    # Sub-featured articles (exclude lead)
    exclude_ids = [featured_lead.id] if featured_lead else []

    sub_featured = (
        Article.query.filter(
            Article.status == "published",
            Article.id.notin_(exclude_ids),
            non_video_filter,
        )
        .order_by(Article.is_featured.desc(), Article.published_at.desc())
        .limit(4)
        .all()
    )

    for a in sub_featured:
        exclude_ids.append(a.id)

    # Latest News stream (regular articles only)
    latest_articles = (
        Article.query.filter(Article.status == "published", non_video_filter)
        .order_by(Article.published_at.desc())
        .limit(8)
        .all()
    )

    # Trending articles (ordered by views & trending flag)
    trending_articles = (
        Article.query.filter(Article.status == "published", non_video_filter)
        .order_by(Article.is_trending.desc(), Article.views.desc())
        .limit(5)
        .all()
    )

    # Most Read articles
    most_read_articles = (
        Article.query.filter(Article.status == "published", non_video_filter)
        .order_by(Article.views.desc())
        .limit(5)
        .all()
    )

    # Videos section (YouTube category or articles with video_url)
    # The dedicated video showcase where all video reporting belongs.
    video_articles = (
        Article.query.filter(
            Article.status == "published",
            or_(
                (Article.video_url.isnot(None)) & (Article.video_url != ""),
                Article.category.has(slug="youtube"),
            ),
        )
        .order_by(Article.published_at.desc())
        .limit(8)
        .all()
    )

    # Category blocks for homepage showcase (strictly non-video)
    showcase_slugs = ["tamil-nadu", "history", "india", "cinema", "jobs"]
    category_blocks = []
    for slug in showcase_slugs:
        cat = Category.query.filter_by(slug=slug).first()
        if cat:
            cat_articles = (
                Article.query.filter(
                    Article.category_id == cat.id,
                    Article.status == "published",
                    non_video_filter,
                )
                .order_by(Article.published_at.desc())
                .limit(4)
                .all()
            )
            if cat_articles:
                category_blocks.append({"category": cat, "articles": cat_articles})

    return render_template(
        "index.html",
        featured_lead=featured_lead,
        sub_featured=sub_featured,
        latest_articles=latest_articles,
        trending_articles=trending_articles,
        most_read_articles=most_read_articles,
        video_articles=video_articles,
        category_blocks=category_blocks,
    )


@public_bp.route("/category/<slug>")
def category(slug):
    """Category detail page with filtering, search and pagination."""
    cat = Category.query.filter_by(slug=slug).first_or_404()

    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "latest")
    q = request.args.get("q", "").strip()

    if cat.slug in ["youtube", "videos"]:
        # Videos section: Shows all video articles
        query = Article.query.filter(
            Article.status == "published",
            or_(
                Article.category_id == cat.id,
                (Article.video_url.isnot(None)) & (Article.video_url != ""),
            ),
        )
        cat_trending = (
            Article.query.filter(
                Article.status == "published",
                or_(
                    Article.category_id == cat.id,
                    (Article.video_url.isnot(None)) & (Article.video_url != ""),
                ),
            )
            .order_by(Article.views.desc())
            .limit(5)
            .all()
        )
    else:
        # Standard Category: Strictly exclude any articles with videos
        query = Article.query.filter(
            Article.category_id == cat.id,
            Article.status == "published",
            or_(Article.video_url.is_(None), Article.video_url == ""),
        )
        cat_trending = (
            Article.query.filter(
                Article.category_id == cat.id,
                Article.status == "published",
                or_(Article.video_url.is_(None), Article.video_url == ""),
            )
            .order_by(Article.views.desc())
            .limit(5)
            .all()
        )

    if q:
        search_filter = or_(
            Article.title.ilike(f"%{q}%"),
            Article.title_ta.ilike(f"%{q}%"),
            Article.summary.ilike(f"%{q}%"),
            Article.summary_ta.ilike(f"%{q}%"),
            Article.tags.ilike(f"%{q}%"),
        )
        query = query.filter(search_filter)

    if sort_by == "oldest":
        query = query.order_by(Article.published_at.asc())
    elif sort_by == "popular":
        query = query.order_by(Article.views.desc())
    else:
        query = query.order_by(Article.published_at.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)

    return render_template(
        "category.html",
        category=cat,
        articles=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        search_query=q,
        trending_articles=cat_trending,
    )


@public_bp.route("/videos")
def videos():
    """Direct route for videos and YouTube news."""
    return category(slug="youtube")


@public_bp.route("/article/<slug>")
def article(slug):
    """Article details page with view increment, bookmark detection, and related articles."""
    art = Article.query.filter_by(slug=slug).first_or_404()

    # Allow draft preview only if admin is logged in
    if art.status != "published" and not session.get("user_id"):
        flash("This article has not been published yet.", "warning")
        return redirect(url_for("public.index"))

    # Record authentic view (deduplicate within visitor session to prevent fake refresh inflation)
    v_token = get_session_token()
    viewed_articles = session.get("viewed_articles", [])
    if art.id not in viewed_articles:
        art.views = (art.views or 0) + 1
        view_record = ArticleView(
            article_id=art.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:250] if request.user_agent else None,
        )
        db.session.add(view_record)
        db.session.commit()
        viewed_articles.append(art.id)
        session["viewed_articles"] = viewed_articles

    # Check if bookmarked
    is_bookmarked = (
        Bookmark.query.filter_by(article_id=art.id, session_id=v_token).first()
        is not None
    )

    # Related articles
    related = []
    is_video = bool(
        art.video_url or (art.category and art.category.slug in ["youtube", "videos"])
    )
    if art.category_id:
        if is_video:
            related_cond = or_(
                Article.category_id == art.category_id,
                (Article.video_url.isnot(None)) & (Article.video_url != ""),
            )
        else:
            related_cond = and_(
                Article.category_id == art.category_id,
                or_(Article.video_url.is_(None), Article.video_url == ""),
            )

        related = (
            Article.query.filter(
                related_cond, Article.id != art.id, Article.status == "published"
            )
            .order_by(Article.published_at.desc())
            .limit(4)
            .all()
        )

    # Previous and next articles (strictly within same type: non-video to non-video)
    if is_video:
        seq_filter = or_(
            (Article.video_url.isnot(None)) & (Article.video_url != ""),
            Article.category.has(slug="youtube"),
        )
    else:
        seq_filter = and_(
            or_(Article.video_url.is_(None), Article.video_url == ""),
            ~Article.category.has(slug="youtube"),
        )

    prev_article = (
        Article.query.filter(
            Article.status == "published", Article.id < art.id, seq_filter
        )
        .order_by(Article.id.desc())
        .first()
    )

    next_article = (
        Article.query.filter(
            Article.status == "published", Article.id > art.id, seq_filter
        )
        .order_by(Article.id.asc())
        .first()
    )

    # Trending articles for sidebar (non-video for editorial articles)
    trending_articles = (
        Article.query.filter(
            Article.status == "published",
            or_(Article.video_url.is_(None), Article.video_url == ""),
            ~Article.category.has(slug="youtube"),
        )
        .order_by(Article.views.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "article.html",
        article=art,
        is_bookmarked=is_bookmarked,
        related_articles=related,
        prev_article=prev_article,
        next_article=next_article,
        trending_articles=trending_articles,
    )


@public_bp.route("/search")
def search():
    """Search news articles by title, keywords, description, or category."""
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()
    sort_by = request.args.get("sort", "latest")
    page = request.args.get("page", 1, type=int)

    query = Article.query.filter_by(status="published")

    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    if q:
        search_filter = or_(
            Article.title.ilike(f"%{q}%"),
            Article.title_ta.ilike(f"%{q}%"),
            Article.summary.ilike(f"%{q}%"),
            Article.summary_ta.ilike(f"%{q}%"),
            Article.content.ilike(f"%{q}%"),
            Article.content_ta.ilike(f"%{q}%"),
            Article.tags.ilike(f"%{q}%"),
            Article.author.ilike(f"%{q}%"),
            Article.author_ta.ilike(f"%{q}%"),
        )
        query = query.filter(search_filter)

    if sort_by == "popular":
        query = query.order_by(Article.views.desc())
    elif sort_by == "oldest":
        query = query.order_by(Article.published_at.asc())
    else:
        query = query.order_by(Article.published_at.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)

    return render_template(
        "search.html",
        query=q,
        selected_category=selected_category,
        articles=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        total_count=pagination.total,
    )


@public_bp.route("/bookmarks")
def bookmarks():
    """List of bookmarked articles for current visitor session."""
    v_token = get_session_token()
    saved_items = (
        Bookmark.query.filter_by(session_id=v_token)
        .order_by(Bookmark.created_at.desc())
        .all()
    )

    article_list = [
        item.article
        for item in saved_items
        if item.article and item.article.status == "published"
    ]

    return render_template("bookmarks.html", articles=article_list)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact form page with message recording."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not (name and email and subject and message):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    {"status": "error", "message": "All fields are required."}
                ), 400
            flash(
                "Please fill in all required fields. / அனைத்து விவரங்களையும் நிரப்பவும்.",
                "danger",
            )
            return render_template("contact.html")

        new_msg = ContactMessage()
        new_msg.name = name
        new_msg.email = email
        new_msg.subject = subject
        new_msg.message = message
        db.session.add(new_msg)
        db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {
                    "status": "success",
                    "message": "Your message has been sent successfully! Our editorial desk will reply soon.",
                }
            )

        flash(
            "Thank you! Your message has been sent to our editorial desk. / உங்கள் செய்தி பெறப்பட்டது.",
            "success",
        )
        return redirect(url_for("public.contact"))

    return render_template("contact.html")


@public_bp.route("/subscribe", methods=["POST"])
def subscribe():
    """Newsletter subscription handler."""
    email = request.form.get("email", "").strip().lower()

    if not email or "@" not in email or "." not in email:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {"status": "error", "message": "Please enter a valid email address."}
            ), 400
        flash("Please enter a valid email address.", "danger")
        return redirect(request.referrer or url_for("public.index"))

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.session.commit()
            msg = "Your subscription has been reactivated! / உங்கள் சந்தா புதுப்பிக்கப்பட்டது!"
        else:
            msg = "You are already subscribed to our newsletter! / நீங்கள் ஏற்கனவே சந்தாதாரராக உள்ளீர்கள்!"
    else:
        new_sub = NewsletterSubscriber(email=email, is_active=True)
        db.session.add(new_sub)
        db.session.commit()
        msg = "Thank you for subscribing to Vithaigal Iyakkam! / விதை இயக்கம் செய்திகளுக்கு இணைந்ததற்கு நன்றி!"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success", "message": msg})

    flash(msg, "success")
    return redirect(request.referrer or url_for("public.index"))


# --- Interactive JSON APIs for Frontend ---


@public_bp.route("/api/bookmark/toggle", methods=["POST"])
def toggle_bookmark():
    """Toggle bookmark state for an article via AJAX."""
    data = request.get_json() or {}
    article_id = data.get("article_id")

    if not article_id:
        return jsonify({"success": False, "error": "Missing article_id"}), 400

    art = db.session.get(Article, article_id)
    if not art:
        return jsonify({"success": False, "error": "Article not found"}), 404

    v_token = get_session_token()
    existing = Bookmark.query.filter_by(article_id=art.id, session_id=v_token).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        is_bookmarked = False
    else:
        new_bm = Bookmark(article_id=art.id, session_id=v_token)
        db.session.add(new_bm)
        db.session.commit()
        is_bookmarked = True

    total_bookmarks = Bookmark.query.filter_by(session_id=v_token).count()

    return jsonify(
        {
            "success": True,
            "is_bookmarked": is_bookmarked,
            "total_count": total_bookmarks,
            "message": "Bookmark updated",
        }
    )


@public_bp.route("/api/article/like", methods=["POST"])
def like_article():
    """Increment article like count via AJAX."""
    data = request.get_json() or {}
    article_id = data.get("article_id")
    if not article_id:
        return jsonify({"success": False, "error": "Missing article_id"}), 400
    art = db.session.get(Article, article_id)
    if not art:
        return jsonify({"success": False, "error": "Article not found"}), 404
    art.likes = (art.likes or 0) + 1
    db.session.commit()
    return jsonify({"success": True, "likes": art.likes})


@public_bp.route("/api/search/live")
def live_search():
    """Instant search dropdown suggestions."""
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify({"results": []})

    results = (
        Article.query.filter(
            Article.status == "published",
            or_(
                Article.title.ilike(f"%{q}%"),
                Article.title_ta.ilike(f"%{q}%"),
                Article.tags.ilike(f"%{q}%"),
            ),
        )
        .order_by(Article.published_at.desc())
        .limit(6)
        .all()
    )

    data = []
    current_lang = session.get("lang", "ta")
    for a in results:
        data.append(
            {
                "title": a.title_ta
                if (current_lang == "ta" and a.title_ta)
                else a.title,
                "slug": a.slug,
                "category": a.category.name_ta
                if (a.category and current_lang == "ta")
                else (a.category.name_en if a.category else "General"),
                "image": a.featured_image,
                "date": a.formatted_date_ta
                if current_lang == "ta"
                else a.formatted_date,
            }
        )

    return jsonify({"results": data})
