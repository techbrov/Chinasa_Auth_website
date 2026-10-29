"""Idempotent starter content. Run:  python -m app.seed
Everything marked [CONFIRM] must be checked with the client before launch."""
from datetime import datetime

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Book, Certification, Event, Page, Review, Service


def upsert(db, model, key: str, data: dict):
    row = db.scalar(select(model).where(getattr(model, key) == data[key]))
    if row is None:
        db.add(model(**data))


ABOUT = """
<p>Chinasa Elukposi, known as <strong>The Seasoned Book Editor</strong>, is a professional book editor,
ghostwriter, author, book writing consultant and writing coach. She works with writers who want more than
a completed manuscript, and helps them achieve clarity, structure and lasting impact.</p>
<p>She holds a degree in Applied Biochemistry from Nnamdi Azikiwe University. That training in discipline,
precision and critical thinking shapes how she edits and writes.</p>
<p>She has helped authors turn manuscripts into published books, and has supported busy authors by converting
recorded audio into clear, well-structured ebooks, always keeping the author's own voice.</p>
<p>She is the lead trainer at Seasoned Writers Academy, and the author of two books, <em>The Drive</em> and
<em>Upgrade to Explore</em>.</p>
<h2>Brand vision</h2>
<p>To help authors shape their ideas and manuscripts into published, life-changing global books.</p>
<h2>Brand mission</h2>
<p>To work closely with authors, brands and individuals to refine ideas, strengthen manuscripts and guide
each project through a clear, disciplined process that results in well-structured, high-quality books
prepared for global publication.</p>
"""

SPEAKING = """
<p>Chinasa speaks and trains on writing with clarity, structure and purpose. [CONFIRM: final topic list
and audience types with the client.]</p>
<h2>Suggested talk topics (draft)</h2>
<ul>
  <li>From raw manuscript to publication-ready book</li>
  <li>How to keep your voice when someone else edits or ghostwrites your book</li>
  <li>Turning recorded audio into a well-structured ebook</li>
  <li>Writing with structure, clarity and consistency</li>
</ul>
<h2>Formats</h2>
<p>Keynotes, workshops and training sessions for writers' communities, schools, churches, brands and
conferences. [CONFIRM: formats, length and whether virtual sessions are offered.]</p>
<p>To invite Chinasa to speak, use the <a href="/contact?topic=Speaking">speaking request form</a>.</p>
"""

PRESS = """
<h2>Short bio</h2>
<p>Chinasa Elukposi, The Seasoned Book Editor, is a professional book editor, ghostwriter, author and
writing coach who helps writers turn raw manuscripts into published, life-changing books.</p>
<h2>Books</h2>
<p>Author of <em>The Drive</em> and <em>Upgrade to Explore</em>.</p>
<h2>Media contact</h2>
<p>Use the <a href="/contact?topic=Press">contact form</a> and choose "Press and media".</p>
"""

PRIVACY = """
<p><strong>[CONFIRM: have a data-protection professional review this page before launch.]</strong></p>
<p>This website is run by Chinasa Elukposi (The Seasoned Book Editor). We handle personal data in line with the
Nigeria Data Protection Act 2023.</p>
<h2>What we collect and why</h2>
<ul>
  <li><strong>Contact form:</strong> your name, email, topic and message, so we can reply to your enquiry.</li>
  <li><strong>Newsletter:</strong> your email address, only if you tick the consent box, so we can send you updates.</li>
</ul>
<h2>Legal basis</h2>
<p>We rely on your consent. You can withdraw it at any time by emailing us.</p>
<h2>How long we keep it</h2>
<p>[CONFIRM: retention period, for example 24 months for enquiries.]</p>
<h2>Your rights</h2>
<p>You may ask to see, correct, move or delete your data, or complain to the Nigeria Data Protection Commission.</p>
<h2>Cookies</h2>
<p>This site sets no analytics or advertising cookies. If that changes, we will ask for your consent first.</p>
<h2>Where data is stored</h2>
<p>[CONFIRM: hosting country and email provider, and the safeguards used for cross-border transfers.]</p>
"""

SERVICES = [
    dict(
        slug="book-editing",
        title="Book Editing",
        sort_order=10,
        summary="Refining your manuscript for clarity, flow, structure, and readability while preserving your voice.",
        details_html="""
<p>We refine your manuscript for clarity, flow, structure, and readability while preserving your voice and message. Our goal is to help you produce a well-developed book that connects with your readers.</p>
<table class="rates">
<thead><tr><th>Level</th><th>What is included</th><th>Rate per page</th></tr></thead>
<tbody>
<tr><td><strong>Light editing</strong></td><td>Line editing, copy editing, consistency check, proofreading, formatting</td><td>&#8358;1,000 | $0.71</td></tr>
<tr><td><strong>Medium editing</strong></td><td>Everything in light editing, plus structural editing</td><td>&#8358;1,200 | $0.85</td></tr>
<tr><td><strong>Heavy editing</strong></td><td>Developmental editing, structural editing, copy editing, line editing, consistency check, proofreading, formatting</td><td>&#8358;1,500 | $1.06</td></tr>
</tbody></table>
""",
        price_note="Rates are per page. Send your page count through the enquiry form for a quote.",
    ),
    dict(
        slug="manuscript-evaluation",
        title="Manuscript Evaluation",
        sort_order=20,
        summary="Professional assessment to identify strengths, weaknesses, and improvement areas.",
        details_html=(
            "<p>We assess your manuscript to identify its strengths, weaknesses, and areas "
            "that need improvement. You receive professional feedback and practical "
            "recommendations to guide your next steps.</p>"
        ),
        price_note="Quoted per manuscript.",
    ),
    dict(
        slug="proofreading",
        title="Proofreading",
        sort_order=25,
        summary="Thorough checks for spelling, grammar, punctuation, and typos prior to publication.",
        details_html=(
            "<p>We check your manuscript for spelling, grammar, punctuation, typographical "
            "errors, and other minor inconsistencies, ensuring that your book is clean and "
            "ready for publication.</p>"
        ),
        price_note="Quoted per page or project.",
    ),
    dict(
        slug="book-formatting",
        title="Book Formatting",
        sort_order=30,
        summary="Professional layout suitable for digital or print publication.",
        details_html=(
            "<p>We arrange your manuscript into a professional, reader-friendly layout suitable "
            "for digital or print publication. This includes proper headings, spacing, page "
            "numbering, and consistent text presentation.</p>"
        ),
        price_note="Quoted per project.",
    ),
    dict(
        slug="book-cover-design",
        title="Book Cover Design",
        sort_order=35,
        summary="Eye-catching, genre-relevant cover designs that attract target readers.",
        details_html=(
            "<p>We create appealing and relevant book covers that reflect your book's message, "
            "attract your target readers, and give your work a professional appearance.</p>"
        ),
        price_note="Quoted per project.",
    ),
    dict(
        slug="ghostwriting",
        title="Ghostwriting",
        sort_order=40,
        summary="Turn your ideas, stories, and knowledge into a complete, well-crafted book in your voice.",
        details_html=(
            "<p>We help you turn your ideas, knowledge, experiences, and stories into a "
            "well-written book. We work with you to develop your vision and bring it to "
            "life in a voice that reflects your message.</p>"
        ),
        price_note="Quoted per project.",
    ),
    dict(
        slug="digital-publishing",
        title="Digital Publishing",
        sort_order=50,
        summary="Distribution and publishing support for platforms like Amazon and Selar.",
        details_html=(
            "<p>We help authors publish and sell their books on digital platforms, including "
            "Selar, and Amazon. From preparing your book for digital publication to guiding you "
            "through the uploading process, we help you make your work accessible to readers "
            "and buyers worldwide.</p>"
        ),
        price_note="Quoted per project.",
    ),
    dict(
        slug="isbn-registration",
        title="ISBN Registration",
        sort_order=55,
        summary="Assistance with obtaining an official ISBN for international book identification.",
        details_html=(
            "<p>We assist authors with the process of obtaining an International Standard Book "
            "Number (ISBN), which helps identify their books in the publishing and book "
            "distribution system.</p>"
        ),
        price_note="Quoted per registration.",
    ),
    dict(
        slug="coaching-and-consultation",
        title="Coaching & Consultation",
        sort_order=60,
        summary="Personalised strategic guidance to navigate your writing and publishing journey.",
        details_html=(
            "<p>We provide personalised guidance to help you navigate your book-writing and "
            "publishing journey. Whether you need help developing your idea, planning your "
            "manuscript, making publishing decisions, or positioning your book for your "
            "audience, we help you move forward with clarity.</p>"
        ),
        price_note="Quoted per session or monthly retainer.",
    ),
    dict(
        slug="writing-training",
        title="Writing Training",
        sort_order=70,
        summary="Training for aspiring and intermediate writers through Seasoned Writers Academy.",
        details_html=(
            "<p>Chinasa is the lead trainer at Seasoned Writers Academy, teaching content writing, "
            "storywriting and ghostwriting. Contact us for upcoming cohort dates and enrollment.</p>"
        ),
        price_note="Quoted per cohort.",
    ),
]

BOOKS = [
    dict(slug="the-drive", title="The Drive", kind="authored", reading_order=1,
         cover_image="img/the-drive.jpg", buy_url="",
         blurb="By Chinasa Elukposi. [CONFIRM: back-cover blurb.]"),
    dict(slug="upgrade-to-explore", title="Upgrade to Explore", kind="authored", reading_order=2,
         cover_image="img/upgrade-to-explore.jpg", buy_url="",
         blurb="By Chinasa Elukposi. [CONFIRM: back-cover blurb.]"),
    dict(slug="dude-without-limits", title="Dude Without Limits", kind="edited",
         author_name="Ogude Jessica", cover_image="img/dude-without-limits.jpg"),
    dict(slug="worthy-of-wealth", title="Worthy of Wealth", kind="edited",
         author_name="Ogude Jessica", cover_image="img/worthy-of-wealth.jpg"),
    dict(slug="unveil", title="Unveil", kind="edited",
         author_name="Precious Ekeh", cover_image="img/unveil.jpg"),
    dict(slug="40-affirmations", title="40 Affirmations With Precious Ekeh", kind="edited",
         author_name="Precious Ekeh", cover_image="img/40-affirmations.jpg"),
    dict(slug="becoming-a-smart-mom", title="Becoming a Smart Mom", kind="edited",
         author_name="Chidinma Faith Ihechukwu", cover_image="img/becoming-a-smart-mom.jpg"),
]

CERTS = [
    ("Fundamentals of English Grammar", "Springsgates Grammar School", "18 February 2022", "img/cert-grammar.jpg"),
    ("English Writing and Communication Skills", "LordMarshal International Academy, Nigeria", "30 November 2022", "img/cert-english.jpg"),
    ("Professional Ghostwriting", "Valiant Writers and Entrepreneurs Academy", "8 September 2024", "img/cert-ghostwriting.jpg"),
    ("Digital Tools at the Workplace and Professional E-book Creation", "Mindset Consults", "14-15 June 2025", "img/cert-digital-tools.jpg"),
    ("Content Weaving / Writing", "The Exquisite Writers Academy Concept", "10 August 2025", "img/cert-content-weaving.jpg"),
    ("Course / Training Manual Writing", "NancyBest Legacy Nigeria Limited", "4 December 2025", "img/cert-manual-writing.jpg"),
    ("Professional Book Editing", "Edit Like A Boss Academy", "25 February 2026", "img/cert-book-editing.jpg"),
]


EVENTS = [
    dict(title="Upgrade to Explore", starts_at=datetime(2025, 7, 6), ends_at=datetime(2025, 7, 18),
         time_label="8pm daily", location="Closed WhatsApp group",
         description="A skills training with Holiness Evangelistic Church and Virtuous Daughters International, "
                     "taking participants from novice to sought-after professional. Chinasa Elukposi taught "
                     "content writing alongside sessions on digital marketing, graphic design, video and photo "
                     "editing, social media management and public speaking.",
         image="img/event-upgrade-to-explore.jpg",
         image_alt="Flyer for Upgrade to Explore, a skills training from 6 to 18 July 2025 at 8pm daily, "
                   "with six trainers including Chinasa Elukposi on content writing."),
    dict(title="Book Launch: Becoming the Best Version of You", starts_at=datetime(2025, 10, 31),
         time_label="8pm", location="WhatsApp group",
         description="Launch of Unveil by Ekeh Precious Amarachi, hosted on WhatsApp. Chinasa Elukposi, The "
                     "Seasoned Book Editor, spoke on the topic Becoming the Best Version of You.",
         image="img/event-book-launch.jpg",
         image_alt="Flyer for the Unveil book launch on Friday 31 October 2025 at 8pm, with the author as host "
                   "and Chinasa Elukposi and Oluwakemi Esther Folorunsho as speakers."),
    dict(title="Beyond the Book", starts_at=datetime(2026, 9, 20), ends_at=datetime(2026, 9, 27),
         time_label="7pm", location="Online",
         description="Weekend live sessions with seasoned authors: real author stories, experiences and "
                     "lessons, and a Q&A on book writing and publishing. Hosted by Chinasa Elukposi, lead trainer.",
         image="img/event-beyond-the-book.jpg",
         image_alt="Flyer for Beyond the Book, live sessions from 20 to 27 September 2026 at 7pm, hosted by "
                   "Chinasa Elukposi with four guest authors."),
    dict(title="Book Writing Bootcamp", starts_at=datetime(2026, 10, 1), ends_at=datetime(2026, 10, 14),
         time_label="Two-week intensive", location="WhatsApp and Telegram",
         description="How to plan, write, publish and market your book. A two-week intensive class with 30 "
                     "training topics, daily Q&A and exercises, a structured template for writing your book, a "
                     "book writing challenge, a certificate of completion and follow-up support.",
         image="img/event-book-writing-bootcamp.jpg",
         image_alt="Flyer for the Book Writing Bootcamp from 1 to 14 October 2026, led by Chinasa Elukposi."),
    # Hidden draft: the client has not yet sent the date, place or flyer for this one.
    dict(title="The Lockdown Feast", starts_at=datetime(2026, 12, 31), is_published=False,
         description="[CONFIRM: date, time, place, description, registration link and flyer. Then tick "
                     "Is published.]"),
]

REVIEWS = [
    dict(client_name="A client", client_detail="message received by email",
         quote="This is great, thank you so much! Thank you so much ma'am. I really love this. May God continue "
               "to give you more understanding, more insight of what you are doing.",
         image="img/review-email.jpg", image_alt="Client's email thanking Chinasa Elukposi for her work.",
         permission_confirmed=True, is_published=True),
    dict(client_name="A client", client_detail="message received on WhatsApp",
         quote="Girl, I must confess... You did a very good job here. Thank you very much. I am just asking "
               "myself how you multiplied the book from 70 pages to 113 pages... My God.",
         image="img/review-whatsapp.jpg",
         image_alt="Client's WhatsApp message praising how the book grew from 70 to 113 pages.",
         permission_confirmed=True, is_published=True),
]


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for slug, title, desc, body in [
            ("about", "About Chinasa", "Book editor, ghostwriter, author and writing coach.", ABOUT),
            ("speaking", "Speaking", "Invite Chinasa Elukposi to speak or train.", SPEAKING),
            ("press-kit", "Press Kit", "Bio, book covers and media contact.", PRESS),
            ("privacy", "Privacy Policy", "How this website handles personal data.", PRIVACY),
        ]:
            upsert(db, Page, "slug", dict(slug=slug, title=title, meta_description=desc, body_html=body))
        for s in SERVICES:
            upsert(db, Service, "slug", s)
        for b in BOOKS:
            upsert(db, Book, "slug", b)
        for i, (t, issuer, date, img) in enumerate(CERTS, start=1):
            if db.scalar(select(Certification).where(Certification.title == t)) is None:
                db.add(Certification(title=t, issuer=issuer, date_label=date, image=img, sort_order=i))
        for e in EVENTS:
            if db.scalar(select(Event).where(Event.title == e["title"])) is None:
                db.add(Event(**e))
        if db.scalar(select(Review)) is None:
            for r in REVIEWS:
                db.add(Review(**r))
        db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    seed()
