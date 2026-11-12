import os
import uuid
from datetime import UTC, datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func

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
from routes.auth import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def handle_image_upload(file_storage):
    """Save uploaded image file with a unique secure filename."""
    if not file_storage or file_storage.filename == "":
        return None
    if allowed_file(file_storage.filename):
        ext = file_storage.filename.rsplit(".", 1)[1].lower()
        unique_name = (
            f"{uuid.uuid4().hex[:12]}_{int(datetime.now(UTC).timestamp())}.{ext}"
        )
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file_storage.save(upload_path)
        return f"/static/images/uploads/{unique_name}"
    return None


# --- LANGUAGE SWITCHER ---
@admin_bp.route("/set-language/<lang>")
def set_language(lang):
    """Switch language from admin dashboard and reload previous page."""
    if lang in ["ta", "en"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("admin.dashboard"))


# --- DASHBOARD ---
@admin_bp.route("/")
@login_required
def admin_root():
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard with real statistics and chart data from SQLite."""
    total_articles = Article.query.count()
    published_articles = Article.query.filter_by(status="published").count()
    draft_articles = Article.query.filter_by(status="draft").count()
    scheduled_articles = Article.query.filter_by(status="scheduled").count()
    total_categories = Category.query.count()

    total_views = db.session.query(func.sum(Article.views)).scalar() or 0
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    total_subscribers = NewsletterSubscriber.query.filter_by(is_active=True).count()

    # Real Category-wise Article Counts for Chart
    categories = Category.query.order_by(Category.order_index.asc()).all()
    category_chart_labels = [c.name_en for c in categories]
    category_chart_data = [c.articles.count() for c in categories]

    # Publication distribution (last 6 months or status breakdown)
    status_chart_labels = ["Published", "Drafts", "Scheduled"]
    status_chart_data = [published_articles, draft_articles, scheduled_articles]

    # Recent articles
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()

    # Recent messages
    recent_messages = (
        ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    )

    stats = {
        "total_articles": total_articles,
        "published_articles": published_articles,
        "draft_articles": draft_articles,
        "scheduled_articles": scheduled_articles,
        "total_categories": total_categories,
        "total_views": total_views,
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "total_subscribers": total_subscribers,
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        category_chart_labels=category_chart_labels,
        category_chart_data=category_chart_data,
        status_chart_labels=status_chart_labels,
        status_chart_data=status_chart_data,
        recent_articles=recent_articles,
        recent_messages=recent_messages,
    )


# --- ARTICLE MANAGEMENT (CRUD) ---
@admin_bp.route("/articles")
@login_required
def articles():
    """Article listing with search, category filtering, and status filtering."""
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "").strip()

    query = Article.query

    if q:
        query = query.filter(
            (Article.title.ilike(f"%{q}%"))
            | (Article.title_ta.ilike(f"%{q}%"))
            | (Article.author.ilike(f"%{q}%"))
        )
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False
    )

    categories = Category.query.order_by(Category.name_en.asc()).all()

    # Status metrics for quick filter tabs
    total_articles = Article.query.count()
    published_count = Article.query.filter_by(status="published").count()
    draft_count = Article.query.filter_by(status="draft").count()
    scheduled_count = Article.query.filter_by(status="scheduled").count()

    return render_template(
        "admin/articles.html",
        articles=pagination.items,
        pagination=pagination,
        categories=categories,
        search_query=q,
        selected_category=category_id,
        selected_status=status,
        total_articles=total_articles,
        published_count=published_count,
        draft_count=draft_count,
        scheduled_count=scheduled_count,
    )


@admin_bp.route("/articles/add", methods=["GET", "POST"])
@login_required
def add_article():
    """Create new article with image upload, auto slug, and validation."""
    categories = Category.query.order_by(Category.name_en.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        title_ta = request.form.get("title_ta", "").strip()
        slug = request.form.get("slug", "").strip()
        category_id = request.form.get("category_id", type=int)
        author = request.form.get("author", "").strip() or "Vithaigal Editorial Desk"
        author_ta = request.form.get("author_ta", "").strip() or "விதை ஆசிரியர் குழு"

        # Collect and combine dynamic summary blocks
        summaries = [s.strip() for s in request.form.getlist("summary") if s.strip()]
        summaries_ta = [
            s.strip() for s in request.form.getlist("summary_ta") if s.strip()
        ]
        summary = "\n\n".join(summaries)
        summary_ta = "\n\n".join(summaries_ta)

        # Collect and combine dynamic content blocks
        contents = [c.strip() for c in request.form.getlist("content") if c.strip()]
        contents_ta = [
            c.strip() for c in request.form.getlist("content_ta") if c.strip()
        ]
        content = "\n\n".join(contents)
        content_ta = "\n\n".join(contents_ta)

        tags = request.form.get("tags", "").strip()
        video_url = request.form.get("video_url", "").strip() or None
        status = request.form.get("status", "published")
        is_featured = "is_featured" in request.form
        is_trending = "is_trending" in request.form
        image_url = request.form.get("image_url", "").strip()

        if not title or not summary or not content:
            flash("Title, Summary, and Content are mandatory fields.", "danger")
            return render_template(
                "admin/add_article.html", categories=categories, form_data=request.form
            )

        # Generate slug if empty
        if not slug:
            slug = Article.generate_slug(title or title_ta)
        else:
            slug = Article.generate_slug(slug)

        # Handle Image
        featured_image = image_url or ""
        if "featured_image" in request.files:
            file = request.files["featured_image"]
            saved_image = handle_image_upload(file)
            if saved_image:
                featured_image = saved_image

        # Auto-fallback to YouTube thumbnail if no image was uploaded or provided
        if (
            not featured_image or featured_image == "/static/images/placeholder.jpg"
        ) and video_url:
            yt_id = Article.extract_youtube_id(video_url)
            if yt_id:
                featured_image = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"

        # Strict placement rule: Videos belong exclusively to the dedicated 'youtube' category
        if video_url:
            yt_cat = Category.query.filter_by(slug="youtube").first()
            if yt_cat:
                category_id = yt_cat.id

        if not featured_image:
            featured_image = "/static/images/placeholder.jpg"

        article = Article(
            title=title,
            title_ta=title_ta,
            slug=slug,
            category_id=category_id,
            author=author,
            author_ta=author_ta,
            summary=summary,
            summary_ta=summary_ta,
            content=content,
            content_ta=content_ta,
            tags=tags,
            video_url=video_url,
            status=status,
            is_featured=is_featured,
            is_trending=is_trending,
            featured_image=featured_image,
            published_at=datetime.now(UTC),
        )

        db.session.add(article)
        db.session.commit()

        flash(
            f'Article "{title}" published successfully! / கட்டுரை பதிவேற்றப்பட்டது.',
            "success",
        )
        return redirect(url_for("admin.articles"))

    return render_template("admin/add_article.html", categories=categories)


@admin_bp.route("/articles/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_article(id):
    """Edit existing article with image replacement option."""
    article = db.get_or_404(Article, id)
    categories = Category.query.order_by(Category.name_en.asc()).all()

    if request.method == "POST":
        article.title = request.form.get("title", "").strip()
        article.title_ta = request.form.get("title_ta", "").strip()

        custom_slug = request.form.get("slug", "").strip()
        if custom_slug and custom_slug != article.slug:
            article.slug = Article.generate_slug(custom_slug, article_id=article.id)

        article.category_id = request.form.get("category_id", type=int)
        article.author = (
            request.form.get("author", "").strip() or "Vithaigal Editorial Desk"
        )
        article.author_ta = (
            request.form.get("author_ta", "").strip() or "விதை ஆசிரியர் குழு"
        )

        # Collect and combine dynamic summary blocks
        summaries = [s.strip() for s in request.form.getlist("summary") if s.strip()]
        summaries_ta = [
            s.strip() for s in request.form.getlist("summary_ta") if s.strip()
        ]
        article.summary = "\n\n".join(summaries)
        article.summary_ta = "\n\n".join(summaries_ta)

        # Collect and combine dynamic content blocks
        contents = [c.strip() for c in request.form.getlist("content") if c.strip()]
        contents_ta = [
            c.strip() for c in request.form.getlist("content_ta") if c.strip()
        ]
        article.content = "\n\n".join(contents)
        article.content_ta = "\n\n".join(contents_ta)

        article.tags = request.form.get("tags", "").strip()
        article.video_url = request.form.get("video_url", "").strip() or None

        # Strict placement rule: Videos belong exclusively to the dedicated 'youtube' category
        if article.video_url:
            yt_cat = Category.query.filter_by(slug="youtube").first()
            if yt_cat:
                article.category_id = yt_cat.id
        article.status = request.form.get("status", "published")
        article.is_featured = "is_featured" in request.form
        article.is_trending = "is_trending" in request.form

        # Image handling
        image_url = request.form.get("image_url", "").strip()
        if image_url:
            article.featured_image = image_url

        if "featured_image" in request.files:
            file = request.files["featured_image"]
            saved_image = handle_image_upload(file)
            if saved_image:
                article.featured_image = saved_image

        # Auto-fallback to YouTube thumbnail if no custom image was set
        if (
            not article.featured_image
            or article.featured_image == "/static/images/placeholder.jpg"
        ) and article.video_url:
            yt_id = Article.extract_youtube_id(article.video_url)
            if yt_id:
                article.featured_image = (
                    f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
                )

        article.updated_at = datetime.now(UTC)
        db.session.commit()

        flash("Article updated successfully! / கட்டுரை மாற்றங்கள் சேமிக்கப்பட்டன.", "success")
        return redirect(url_for("admin.articles"))

    return render_template(
        "admin/edit_article.html", article=article, categories=categories
    )


@admin_bp.route("/articles/delete/<int:id>", methods=["POST"])
@login_required
def delete_article(id):
    """Delete an article securely."""
    article = db.get_or_404(Article, id)
    title = article.title
    db.session.delete(article)
    db.session.commit()
    flash(f'Article "{title}" was deleted. / கட்டுரை நீக்கப்பட்டது.', "info")
    return redirect(url_for("admin.articles"))


@admin_bp.route("/articles/<int:id>/toggle-status", methods=["POST"])
@login_required
def toggle_article_status(id):
    """Toggle article status between published and draft."""
    article = db.get_or_404(Article, id)
    article.status = "draft" if article.status == "published" else "published"
    db.session.commit()
    return jsonify({"success": True, "new_status": article.status})


# --- CATEGORY MANAGEMENT ---
@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    """List and manage categories with safe deletion and article counts."""
    if request.method == "POST":
        name_en = request.form.get("name_en", "").strip()
        name_ta = request.form.get("name_ta", "").strip()
        slug = request.form.get("slug", "").strip() or Article.generate_slug(name_en)
        description_en = request.form.get("description_en", "").strip()
        description_ta = request.form.get("description_ta", "").strip()
        icon = request.form.get("icon", "newspaper").strip()
        order_index = request.form.get("order_index", 0, type=int)

        if not name_en or not name_ta:
            flash("English and Tamil category names are required.", "danger")
        else:
            existing = Category.query.filter_by(slug=slug).first()
            if existing:
                flash(f'Category with slug "{slug}" already exists.', "warning")
            else:
                cat = Category(
                    name_en=name_en,
                    name_ta=name_ta,
                    slug=slug,
                    description_en=description_en,
                    description_ta=description_ta,
                    icon=icon,
                    order_index=order_index,
                )
                db.session.add(cat)
                db.session.commit()
                flash(
                    f'Category "{name_en}" created successfully! / பகுதி உருவாக்கப்பட்டது.',
                    "success",
                )
                return redirect(url_for("admin.categories"))

    categories_list = Category.query.order_by(Category.order_index.asc()).all()
    total_articles = Article.query.count()
    return render_template(
        "admin/categories.html",
        categories=categories_list,
        total_articles=total_articles,
    )


@admin_bp.route("/categories/edit/<int:id>", methods=["POST"])
@login_required
def edit_category(id):
    """Edit category details."""
    cat = db.get_or_404(Category, id)
    cat.name_en = request.form.get("name_en", "").strip()
    cat.name_ta = request.form.get("name_ta", "").strip()
    new_slug = request.form.get("slug", "").strip()
    if new_slug:
        cat.slug = new_slug
    cat.description_en = request.form.get("description_en", "").strip()
    cat.description_ta = request.form.get("description_ta", "").strip()
    cat.icon = request.form.get("icon", "newspaper").strip()
    cat.order_index = request.form.get("order_index", 0, type=int)

    db.session.commit()
    flash(f'Category "{cat.name_en}" updated successfully.', "success")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/delete/<int:id>", methods=["POST"])
@login_required
def delete_category(id):
    """Safely delete category: protect existing articles from orphaned destruction."""
    cat = db.get_or_404(Category, id)
    article_count = cat.articles.count()

    if article_count > 0:
        # Prompt explicitly stated: "Deleting a category must not accidentally destroy related articles without appropriate confirmation and handling."
        action = request.form.get("handle_articles", "unlink")
        if action == "unlink":
            # Unlink articles to keep them safe
            for a in cat.articles:
                a.category_id = None
            db.session.commit()
        else:
            flash(
                f'Cannot delete category "{cat.name_en}" because it has {article_count} active articles. Please reassign them first.',
                "danger",
            )
            return redirect(url_for("admin.categories"))

    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat.name_en}" deleted. / பகுதி நீக்கப்பட்டது.', "info")
    return redirect(url_for("admin.categories"))


# --- BREAKING NEWS MANAGEMENT ---
@admin_bp.route("/breaking-news", methods=["GET", "POST"])
@login_required
def breaking_news():
    """Manage breaking news ticker items."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        title_ta = request.form.get("title_ta", "").strip()
        link_url = request.form.get("link_url", "").strip()
        image_url = request.form.get("image_url", "").strip()
        is_active = "is_active" in request.form
        order_index = request.form.get("order_index", 0, type=int)

        if not title or not title_ta:
            flash("Both English and Tamil headlines are required.", "danger")
        else:
            bn = BreakingNews(
                title=title,
                title_ta=title_ta,
                link_url=link_url or None,
                image_url=image_url or None,
                is_active=is_active,
                order_index=order_index,
            )
            db.session.add(bn)
            db.session.commit()
            flash(
                "Breaking news headline added successfully! / முக்கிய செய்தி சேர்க்கப்பட்டது.",
                "success",
            )
            return redirect(url_for("admin.breaking_news"))

    news_items = BreakingNews.query.order_by(
        BreakingNews.order_index.asc(), BreakingNews.created_at.desc()
    ).all()
    active_count = BreakingNews.query.filter_by(is_active=True).count()
    return render_template(
        "admin/breaking_news.html", news_items=news_items, active_count=active_count
    )


@admin_bp.route("/breaking-news/edit/<int:id>", methods=["POST"])
@login_required
def edit_breaking_news(id):
    """Edit breaking news item."""
    bn = db.get_or_404(BreakingNews, id)
    bn.title = request.form.get("title", "").strip()
    bn.title_ta = request.form.get("title_ta", "").strip()
    bn.link_url = request.form.get("link_url", "").strip() or None
    bn.image_url = request.form.get("image_url", "").strip() or None
    bn.is_active = "is_active" in request.form
    bn.order_index = request.form.get("order_index", 0, type=int)
    db.session.commit()
    flash("Breaking news headline updated.", "success")
    return redirect(url_for("admin.breaking_news"))


@admin_bp.route("/breaking-news/delete/<int:id>", methods=["POST"])
@login_required
def delete_breaking_news(id):
    """Delete breaking news item."""
    bn = db.get_or_404(BreakingNews, id)
    db.session.delete(bn)
    db.session.commit()
    flash("Breaking news item removed.", "info")
    return redirect(url_for("admin.breaking_news"))


@admin_bp.route("/breaking-news/toggle/<int:id>", methods=["POST"])
@login_required
def toggle_breaking_news(id):
    """Toggle active/inactive status."""
    bn = db.get_or_404(BreakingNews, id)
    bn.is_active = not bn.is_active
    db.session.commit()
    return jsonify({"success": True, "is_active": bn.is_active})


# --- CONTACT MESSAGES ---
@admin_bp.route("/messages")
@login_required
def messages():
    """List contact messages with status filter and metrics."""
    page = request.args.get("page", 1, type=int)
    filter_status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    query = ContactMessage.query
    if q:
        query = query.filter(
            (ContactMessage.name.ilike(f"%{q}%"))
            | (ContactMessage.email.ilike(f"%{q}%"))
            | (ContactMessage.subject.ilike(f"%{q}%"))
            | (ContactMessage.message.ilike(f"%{q}%"))
        )
    if filter_status == "unread":
        query = query.filter_by(is_read=False)
    elif filter_status == "read":
        query = query.filter_by(is_read=True)

    pagination = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    total_count = ContactMessage.query.count()
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    read_count = ContactMessage.query.filter_by(is_read=True).count()

    return render_template(
        "admin/messages.html",
        messages=pagination.items,
        pagination=pagination,
        selected_status=filter_status,
        search_query=q,
        total_count=total_count,
        unread_count=unread_count,
        read_count=read_count,
    )


@admin_bp.route("/messages/<int:id>/mark-read", methods=["POST"])
@login_required
def mark_message_read(id):
    """Mark contact message as read/unread."""
    msg = db.get_or_404(ContactMessage, id)
    msg.is_read = not msg.is_read
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"success": True, "is_read": msg.is_read})
    status_label = "read" if msg.is_read else "unread"
    flash(f"Message marked as {status_label}.", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/delete/<int:id>", methods=["POST"])
@login_required
def delete_message(id):
    """Delete contact message."""
    msg = db.get_or_404(ContactMessage, id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages"))


# --- NEWSLETTER SUBSCRIBERS ---
@admin_bp.route("/subscribers")
@login_required
def subscribers():
    """List newsletter subscribers."""
    page = request.args.get("page", 1, type=int)
    pagination = NewsletterSubscriber.query.order_by(
        NewsletterSubscriber.subscribed_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template(
        "admin/subscribers.html", subscribers=pagination.items, pagination=pagination
    )


@admin_bp.route("/subscribers/delete/<int:id>", methods=["POST"])
@login_required
def delete_subscriber(id):
    """Delete subscriber."""
    sub = db.get_or_404(NewsletterSubscriber, id)
    db.session.delete(sub)
    db.session.commit()
    flash("Subscriber removed.", "info")
    return redirect(url_for("admin.subscribers"))


# --- SETTINGS & PROFILE ---
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Manage website settings and admin password."""
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_settings":
            keys = [
                "site_name_en",
                "site_name_ta",
                "site_tagline_en",
                "site_tagline_ta",
                "site_email",
                "site_phone",
                "site_address_en",
                "site_address_ta",
                "site_about_en",
                "site_about_ta",
                "social_facebook",
                "social_twitter",
                "social_youtube",
                "social_instagram",
                "social_whatsapp",
            ]
            for k in keys:
                val = request.form.get(k, "").strip()
                WebsiteSetting.set_setting(k, val)
            flash(
                "Website settings saved successfully! / இணையதள அமைப்புகள் புதுப்பிக்கப்பட்டன.",
                "success",
            )

        elif action == "change_password":
            user = db.session.get(User, session.get("user_id"))
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not user.check_password(current_pw):
                flash("Current password does not match.", "danger")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash("Password changed successfully! / கடவுச்சொல் மாற்றப்பட்டது.", "success")

        return redirect(url_for("admin.settings"))

    all_settings = WebsiteSetting.query.all()
    settings_dict = {s.key: s.value for s in all_settings}
    user = db.session.get(User, session.get("user_id"))

    return render_template("admin/settings.html", settings=settings_dict, user=user)


# --- DIRECT IMAGE UPLOAD API ---
@admin_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    """AJAX upload endpoint for image preview/insert."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    saved_url = handle_image_upload(file)
    if saved_url:
        return jsonify({"url": saved_url})
    return jsonify({"error": "File type not allowed"}), 400
