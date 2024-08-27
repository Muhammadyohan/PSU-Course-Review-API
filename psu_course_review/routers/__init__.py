from . import authentication
from . import comments
from . import courses
from . import review_posts
from . import root
from . import users

def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(courses.router)
    app.include_router(review_posts.router)
    app.include_router(comments.router)