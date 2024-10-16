from . import authentication
from . import comments

from . import review_posts
from . import root
from . import users
from . import events


def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(review_posts.router)
    app.include_router(comments.router)
    app.include_router(events.router)
