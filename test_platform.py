"""
Automated Comprehensive Test Suite for Vithaigal Iyakkam Platform
"""

import unittest

from app import app
from database import db
from database.models import (
    Article,
    ArticleView,
    Bookmark,
    BreakingNews,
    Category,
    ContactMessage,
    NewsletterSubscriber,
    User,
)


class TestVithaigalIyakkam(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_public_homepage(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Vithaigal Iyakkam", res.data)
        self.assertIn(
            b"\xe0\xae\xb5\xe0\xae\xbf\xe0\xae\xa4\xe0\xaf\x88", res.data
        )  # 'விதை' in UTF-8
        print("[PASS] test_01_public_homepage")

    def test_02_category_page(self):
        res = self.client.get("/category/history")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"history", res.data.lower())
        print("[PASS] test_02_category_page")

    def test_03_article_page_and_view_count(self):
        art = Article.query.filter_by(
            slug="keezhadi-phase-10-sangam-era-artifacts-discovered"
        ).first()
        self.assertIsNotNone(art)
        initial_views = art.views or 0

        res = self.client.get(f"/article/{art.slug}")
        self.assertEqual(res.status_code, 200)

        # Verify view count increment
        db.session.refresh(art)
        self.assertEqual(art.views, initial_views + 1)

        # Restore clean baseline so tests do not pollute real views
        ArticleView.query.filter_by(article_id=art.id).delete()
        art.views = initial_views
        db.session.commit()
        print(
            f"[PASS] test_03_article_page_and_view_count: views incremented to {initial_views + 1} and restored to {initial_views}"
        )

    def test_04_live_search_and_search_page(self):
        # Test live search API
        res = self.client.get("/api/search/live?q=keezhadi")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)

        # Test search page
        res2 = self.client.get("/search?q=keezhadi")
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"keezhadi", res2.data.lower())
        print("[PASS] test_04_live_search_and_search_page")

    def test_05_bookmark_toggle_and_bookmarks_page(self):
        art = Article.query.first()
        self.assertIsNotNone(art)

        # Toggle on
        res = self.client.post("/api/bookmark/toggle", json={"article_id": art.id})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_bookmarked"])

        # Bookmarks page
        res2 = self.client.get("/bookmarks")
        self.assertEqual(res2.status_code, 200)
        self.assertIn(art.title.encode("utf-8")[:20], res2.data)

        # Toggle off
        res3 = self.client.post("/api/bookmark/toggle", json={"article_id": art.id})
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertFalse(data3["is_bookmarked"])
        print("[PASS] test_05_bookmark_toggle_and_bookmarks_page")

    def test_06_contact_and_newsletter(self):
        # Test contact form submit
        res = self.client.post(
            "/contact",
            data={
                "name": "Kaviarasan",
                "email": "kavi@example.com",
                "subject": "Excavation Research Query",
                "message": "We are delighted by the recent reports.",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        msg = ContactMessage.query.filter_by(email="kavi@example.com").first()
        self.assertIsNotNone(msg)

        # Test newsletter subscription
        res2 = self.client.post(
            "/subscribe",
            data={"email": "subscriber100@test.com"},
            follow_redirects=True,
        )
        self.assertEqual(res2.status_code, 200)
        sub = NewsletterSubscriber.query.filter_by(
            email="subscriber100@test.com"
        ).first()
        self.assertIsNotNone(sub)
        print("[PASS] test_06_contact_and_newsletter")

    def test_07_language_toggle(self):
        res = self.client.get("/set-language/en", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("lang"), "en")

        res2 = self.client.get("/set-language/ta", follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("lang"), "ta")
        print("[PASS] test_07_language_toggle")

    def test_08_admin_registration_and_login(self):
        # Anonymous should be redirected
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])

        # Ensure clean state for registration test
        existing_test_admin = User.query.filter_by(username="admin").first()
        if existing_test_admin:
            db.session.delete(existing_test_admin)
            db.session.commit()

        # Test registration validation (password mismatch)
        res_mismatch = self.client.post(
            "/admin/register",
            data={
                "full_name": "Chief Administrator",
                "username": "admin",
                "email": "admin@vithaigaliyakkam.org",
                "password": "adminpassword123",
                "confirm_password": "wrongpassword",
            },
        )
        self.assertEqual(res_mismatch.status_code, 200)
        self.assertIn(b"Passwords do not match", res_mismatch.data)

        # Successful registration
        res_reg = self.client.post(
            "/admin/register",
            data={
                "full_name": "Chief Administrator",
                "username": "admin",
                "email": "admin@vithaigaliyakkam.org",
                "password": "adminpassword123",
                "confirm_password": "adminpassword123",
            },
            follow_redirects=True,
        )
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b"Dashboard Overview", res_reg.data)

        # Logout
        self.client.get("/admin/logout")

        # Failed login
        res_fail = self.client.post(
            "/admin/login", data={"username": "admin", "password": "wrongpassword"}
        )
        self.assertEqual(res_fail.status_code, 200)
        self.assertIn(b"Invalid", res_fail.data)

        # Successful login with newly registered credentials
        res_login = self.client.post(
            "/admin/login",
            data={"username": "admin", "password": "adminpassword123"},
            follow_redirects=True,
        )
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Dashboard Overview", res_login.data)

        # Verify persistent session does not prompt for login again
        res_check_login = self.client.get("/admin/login")
        self.assertEqual(res_check_login.status_code, 302)
        self.assertIn("/admin/dashboard", res_check_login.headers["Location"])

        res_check_dash = self.client.get("/admin/dashboard")
        self.assertEqual(res_check_dash.status_code, 200)
        print("[PASS] test_08_admin_registration_and_login")

    def test_09_admin_article_crud(self):
        # Login first
        self.client.post(
            "/admin/login", data={"username": "admin", "password": "adminpassword123"}
        )
        cat = Category.query.first()

        # Create Article
        res = self.client.post(
            "/admin/articles/add",
            data={
                "title": "Test Article on Renewable Green Energy",
                "title_ta": "சோதனை பசுமை ஆற்றல் செய்தி",
                "category_id": cat.id,
                "author": "Tester Desk",
                "summary": "Summary of renewable energy test.",
                "content": "<p>Full content of test renewable energy article.</p>",
                "status": "published",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)

        art = Article.query.filter_by(
            title="Test Article on Renewable Green Energy"
        ).first()
        self.assertIsNotNone(art)

        # Edit Article
        res_edit = self.client.post(
            f"/admin/articles/edit/{art.id}",
            data={
                "title": "Test Article on Renewable Green Energy (Updated)",
                "category_id": cat.id,
                "author": "Tester Desk",
                "summary": "Updated summary.",
                "content": "<p>Updated content.</p>",
                "status": "published",
            },
            follow_redirects=True,
        )
        self.assertEqual(res_edit.status_code, 200)

        db.session.refresh(art)
        self.assertEqual(art.title, "Test Article on Renewable Green Energy (Updated)")

        # Status toggle
        res_toggle = self.client.post(f"/admin/articles/{art.id}/toggle-status")
        self.assertEqual(res_toggle.status_code, 200)
        data = res_toggle.get_json()
        self.assertEqual(data["new_status"], "draft")

        # Delete Article
        res_del = self.client.post(
            f"/admin/articles/delete/{art.id}", follow_redirects=True
        )
        self.assertEqual(res_del.status_code, 200)
        deleted_art = db.session.get(Article, art.id)
        self.assertIsNone(deleted_art)
        print("[PASS] test_09_admin_article_crud")

    def test_10_admin_category_and_breaking_news(self):
        self.client.post(
            "/admin/login", data={"username": "admin", "password": "adminpassword123"}
        )

        # Add Category
        res_cat = self.client.post(
            "/admin/categories",
            data={
                "name_en": "Environment",
                "name_ta": "சுற்றுச்சூழல்",
                "slug": "environment",
                "description_en": "Eco news",
                "order_index": 9,
            },
            follow_redirects=True,
        )
        self.assertEqual(res_cat.status_code, 200)
        new_cat = Category.query.filter_by(slug="environment").first()
        self.assertIsNotNone(new_cat)

        # Add Breaking News
        res_bn = self.client.post(
            "/admin/breaking-news",
            data={
                "title": "Breaking News Alert from Space Exploration",
                "title_ta": "விண்வெளி ஆய்வு முக்கிய செய்தி",
                "is_active": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(res_bn.status_code, 200)
        bn = (
            BreakingNews.query.filter_by(
                title="Breaking News Alert from Space Exploration"
            )
            .order_by(BreakingNews.id.desc())
            .first()
        )
        self.assertIsNotNone(bn)

        initial_state = bn.is_active
        # Toggle Breaking News
        res_bn_toggle = self.client.post(f"/admin/breaking-news/toggle/{bn.id}")
        self.assertEqual(res_bn_toggle.status_code, 200)
        data = res_bn_toggle.get_json()
        self.assertEqual(data["is_active"], not initial_state)

        # Clean up test records
        db.session.delete(bn)
        if new_cat:
            db.session.delete(new_cat)
        db.session.commit()
        print("[PASS] test_10_admin_category_and_breaking_news")

    def test_11_interactive_like_endpoint(self):
        art = Article.query.first()
        self.assertIsNotNone(art)
        initial_likes = art.likes or 0

        res = self.client.post("/api/article/like", json={"article_id": art.id})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["likes"], initial_likes + 1)
        print("[PASS] test_11_interactive_like_endpoint")

    def test_12_admin_messages_and_toggle(self):
        # 1. Login
        self.client.post(
            "/admin/login", data={"username": "admin", "password": "adminpassword123"}
        )

        # 2. Ensure test message
        msg = ContactMessage(
            name="Kavitha Raman",
            email="kavitha@example.com",
            subject="Agricultural Article Inquiry",
            message="Thank you for publishing valuable agriculture guides.",
        )
        db.session.add(msg)
        db.session.commit()

        # 3. View Messages Inbox
        res = self.client.get("/admin/messages")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Reader Messages", res.data)
        self.assertIn(b"Kavitha Raman", res.data)

        # 4. Status Filter
        res_unread = self.client.get("/admin/messages?status=unread")
        self.assertEqual(res_unread.status_code, 200)
        self.assertIn(b"Kavitha Raman", res_unread.data)

        # 5. AJAX Toggle Mark Read
        res_toggle = self.client.post(
            f"/admin/messages/{msg.id}/mark-read",
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.assertEqual(res_toggle.status_code, 200)
        toggle_data = res_toggle.get_json()
        self.assertTrue(toggle_data["success"])
        self.assertTrue(toggle_data["is_read"])

        # 6. Verify in Read Filter
        res_read = self.client.get("/admin/messages?status=read")
        self.assertEqual(res_read.status_code, 200)
        self.assertIn(b"Kavitha Raman", res_read.data)

        # Clean up
        db.session.delete(msg)
        db.session.commit()
        print("[PASS] test_12_admin_messages_and_toggle")

    def test_13_video_posting_and_public_embed(self):
        cat = Category.query.filter_by(slug="youtube").first() or Category.query.first()
        self.assertIsNotNone(cat)

        # Login
        self.client.post(
            "/admin/login", data={"username": "admin", "password": "adminpassword123"}
        )

        # Post new article with YouTube URL and NO image
        res = self.client.post(
            "/admin/articles/add",
            data={
                "title": "Test Video Article on Solar Energy",
                "title_ta": "சூரிய சக்தி பற்றிய பிரத்யேக வீடியோ பதிவு",
                "slug": "test-video-solar-energy",
                "category_id": str(cat.id),
                "author": "Video Journalist",
                "author_ta": "வீடியோ நிருபர்",
                "summary": "Solar panels breakthrough research in Tamil Nadu.",
                "summary_ta": "தமிழகத்தில் புதிய சூரிய சக்தி தொழில்நுட்பம் குறித்த பார்வை.",
                "content": "<p>Full video report below.</p>",
                "content_ta": "<p>கீழே உள்ள வீடியோவை காண்க.</p>",
                "video_url": "https://youtu.be/dQw4w9WgXcQ?si=abcdef12345",
                "status": "published",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)

        art = Article.query.filter(
            Article.slug.like("test-video-solar-energy%")
        ).first()
        self.assertIsNotNone(art)
        self.assertEqual(art.youtube_embed_id, "dQw4w9WgXcQ")
        self.assertIn("img.youtube.com", art.featured_image)

        # Public Homepage verification (video belongs in the dedicated video showcase)
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b"Test Video Article on Solar Energy", res_home.data)
        self.assertIn(b"dQw4w9WgXcQ", res_home.data)

        # Public /videos verification
        res_videos = self.client.get("/videos")
        self.assertEqual(res_videos.status_code, 200)
        self.assertIn(b"Test Video Article on Solar Energy", res_videos.data)

        # Ensure video is NOT shown in non-video category feeds like History
        res_history = self.client.get("/category/history")
        self.assertEqual(res_history.status_code, 200)
        self.assertNotIn(b"Test Video Article on Solar Energy", res_history.data)

        # Article Detail page verification
        res_detail = self.client.get(f"/article/{art.slug}")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(b"https://www.youtube.com/embed/dQw4w9WgXcQ", res_detail.data)

        # Cleanup
        all_test_arts = Article.query.filter(
            Article.slug.like("test-video-solar-energy%")
        ).all()
        for a in all_test_arts:
            ArticleView.query.filter_by(article_id=a.id).delete()
            Bookmark.query.filter_by(article_id=a.id).delete()
            db.session.delete(a)
        User.query.filter_by(username="admin").delete()
        db.session.commit()
        print("[PASS] test_13_video_posting_and_public_embed")

    def test_14_admin_language_switch(self):
        # Register and login admin
        User.query.filter_by(username="admin_lang_user").delete()
        db.session.commit()

        self.client.post(
            "/admin/register",
            data={
                "full_name": "Bilingual Admin",
                "username": "admin_lang_user",
                "email": "bilingual@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )

        # Switch to English
        res_en = self.client.get("/admin/set-language/en", follow_redirects=True)
        self.assertEqual(res_en.status_code, 200)
        self.assertIn(b"Dashboard Overview", res_en.data)
        self.assertIn(b"Write Article", res_en.data)
        self.assertIn(b"Editorial Content", res_en.data)

        # Switch to Tamil
        res_ta = self.client.get("/admin/set-language/ta", follow_redirects=True)
        self.assertEqual(res_ta.status_code, 200)
        self.assertIn("கண்ணோட்டம்".encode(), res_ta.data)
        self.assertIn("கட்டுரை எழுதுக".encode(), res_ta.data)
        self.assertIn("செய்தி & உள்ளடக்கம்".encode(), res_ta.data)

        # Cleanup
        User.query.filter_by(username="admin_lang_user").delete()
        db.session.commit()
        print("[PASS] test_14_admin_language_switch")

    def test_15_dynamic_summary_and_content_blocks(self):
        # Register and login admin
        User.query.filter_by(username="admin_blocks_user").delete()
        db.session.commit()

        self.client.post(
            "/admin/register",
            data={
                "full_name": "Block Editor",
                "username": "admin_blocks_user",
                "email": "blocks@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )

        # Verify buttons on Add Article page
        res_get = self.client.get("/admin/articles/add")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn(b"Add Summary", res_get.data)
        self.assertIn(b"Add Content", res_get.data)

        cat = Category.query.first()
        self.assertIsNotNone(cat)

        # POST multiple summary and content blocks
        from werkzeug.datastructures import MultiDict

        form_data = MultiDict(
            [
                ("title", "Multi-Block Comprehensive Article"),
                ("title_ta", "பல-பகுதிகள் கொண்ட விரிவான கட்டுரை"),
                ("slug", "multi-block-comprehensive-article"),
                ("category_id", str(cat.id)),
                ("author", "Desk Editor"),
                ("summary", "Initial short summary overview."),
                ("summary", "Second additional summary paragraph."),
                ("summary_ta", "முதல் சுருக்க உரை."),
                ("summary_ta", "இரண்டாம் கூடுதல் சுருக்க உரை."),
                ("content", "<p>First detailed editorial section.</p>"),
                ("content", "<p>Second in-depth editorial section.</p>"),
                ("content_ta", "<p>முதல் விரிவான கட்டுரைப் பகுதி.</p>"),
                ("content_ta", "<p>இரண்டாம் விரிவான கட்டுரைப் பகுதி.</p>"),
                ("status", "published"),
            ]
        )

        res_post = self.client.post(
            "/admin/articles/add", data=form_data, follow_redirects=True
        )
        self.assertEqual(res_post.status_code, 200)

        art = Article.query.filter_by(slug="multi-block-comprehensive-article").first()
        self.assertIsNotNone(art)
        self.assertEqual(
            art.summary,
            "Initial short summary overview.\n\nSecond additional summary paragraph.",
        )
        self.assertEqual(art.summary_ta, "முதல் சுருக்க உரை.\n\nஇரண்டாம் கூடுதல் சுருக்க உரை.")
        self.assertEqual(
            art.content,
            "<p>First detailed editorial section.</p>\n\n<p>Second in-depth editorial section.</p>",
        )
        self.assertEqual(
            art.content_ta,
            "<p>முதல் விரிவான கட்டுரைப் பகுதி.</p>\n\n<p>இரண்டாம் விரிவான கட்டுரைப் பகுதி.</p>",
        )

        # Verify edit page also has the buttons
        res_edit_get = self.client.get(f"/admin/articles/edit/{art.id}")
        self.assertEqual(res_edit_get.status_code, 200)
        self.assertIn(b"Add Summary", res_edit_get.data)
        self.assertIn(b"Add Content", res_edit_get.data)

        # Cleanup
        db.session.delete(art)
        User.query.filter_by(username="admin_blocks_user").delete()
        db.session.commit()
        print("[PASS] test_15_dynamic_summary_and_content_blocks")


if __name__ == "__main__":
    unittest.main()
