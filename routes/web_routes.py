from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.UserModel import UserModel
from models.PostModel import PostModel
from models.LikeModel import LikeModel
from models.CommentModel import CommentModel
from models.FollowModel import FollowModel
from helpers.auth import (
    create_access_token,
    get_current_user_from_cookie,
    get_current_user_optional,
    verify_token,
    blacklist_token
)
import logging

logger = logging.getLogger(__name__)

web_router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")


# ============ AUTH ROUTES ============

@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@web_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@web_router.post("/signup", response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    bio: str = Form(default="")
):
    db_client = request.app.db_client
    user_model = UserModel(db_client)

    user = await user_model.create_user(
        username=username,
        email=email,
        hashed_password=password,
        salt="salt",
        bio=bio
    )

    if not user:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Username or email already exists"}
        )

    access_token = create_access_token(user.id)
    response = RedirectResponse(url="/feed", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@web_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@web_router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    db_client = request.app.db_client
    user_model = UserModel(db_client)

    user = await user_model.get_user_by_username(username)

    if not user or user.hashed_password != password:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    access_token = create_access_token(user.id)
    response = RedirectResponse(url="/feed", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@web_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, current_user=Depends(get_current_user_from_cookie)):
    token = request.cookies.get("access_token")

    if token:
        user_id = verify_token(token)
        if user_id:
            blacklist_token(token)
            logger.info(f"User {user_id} logged out")

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response


# ============ POST ROUTES ============

@web_router.get("/feed", response_class=HTMLResponse)
async def feed_page(request: Request):
    current_user = await get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db_client = request.app.db_client
    post_model = PostModel(db_client)
    posts = await post_model.get_feed_posts(current_user["id"], limit=20, offset=0)

    return templates.TemplateResponse(
        "posts/feed.html",
        {"request": request, "user": current_user, "posts": posts}
    )


@web_router.get("/posts/create", response_class=HTMLResponse)
async def create_post_page(request: Request, current_user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse("posts/create.html", {"request": request, "user": current_user})


@web_router.post("/posts/create", response_class=HTMLResponse)
async def create_post_submit(
    request: Request,
    post_text: str = Form(...),
    post_image: str = Form(default=None),
    current_user=Depends(get_current_user_from_cookie)
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)

    post = await post_model.create_post(
        user_id=current_user["id"],
        post_text=post_text,
        post_image=post_image
    )

    if not post:
        return templates.TemplateResponse(
            "posts/create.html",
            {"request": request, "error": "Failed to create post", "user": current_user}
        )

    return RedirectResponse(url="/feed", status_code=302)


@web_router.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int, current_user=Depends(get_current_user_optional)):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    comment_model = CommentModel(db_client)

    post = await post_model.get_post_by_id(post_id)

    if not post:
        return templates.TemplateResponse("posts/not_found.html", {"request": request})

    comments = await comment_model.get_comments(post_id)

    return templates.TemplateResponse(
        "posts/detail.html",
        {"request": request, "post": post, "comments": comments, "user": current_user}
    )


@web_router.post("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, post_id: int, current_user=Depends(get_current_user_from_cookie)):
    db_client = request.app.db_client
    post_model = PostModel(db_client)

    success = await post_model.delete_post(post_id, user_id=current_user["id"])

    if success:
        return RedirectResponse(url="/feed", status_code=302)
    else:
        return templates.TemplateResponse(
            "posts/error.html",
            {"request": request, "error": "Failed to delete post", "user": current_user}
        )


# ============ USER ROUTES ============

@web_router.get("/users/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str, current_user=Depends(get_current_user_optional)):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    post_model = PostModel(db_client)
    follow_model = FollowModel(db_client)

    user = await user_model.get_user_by_username(username)

    if not user:
        return templates.TemplateResponse("users/not_found.html", {"request": request})

    posts = await post_model.get_posts_by_user_id(user.id)
    followers_count = await follow_model.get_followers_count(user.id)
    following_count = await follow_model.get_following_count(user.id)

    return templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": user,
            "posts": posts,
            "followers_count": followers_count,
            "following_count": following_count,
            "current_user": current_user
        }
    )


# ============ INTERACTION ROUTES ============

@web_router.post("/posts/{post_id}/like", response_class=HTMLResponse)
async def like_post(request: Request, post_id: int, current_user=Depends(get_current_user_from_cookie)):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    await like_model.add_like(user_id=current_user["id"], post_id=post_id)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=302)


@web_router.post("/posts/{post_id}/unlike", response_class=HTMLResponse)
async def unlike_post(request: Request, post_id: int, current_user=Depends(get_current_user_from_cookie)):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    await like_model.remove_like(user_id=current_user["id"], post_id=post_id)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=302)


@web_router.post("/posts/{post_id}/comment", response_class=HTMLResponse)
async def add_comment(
    request: Request,
    post_id: int,
    comment_text: str = Form(...),
    current_user=Depends(get_current_user_from_cookie)
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    await comment_model.add_comment(
        user_id=current_user["id"],
        post_id=post_id,
        comment_text=comment_text
    )
    return RedirectResponse(url=f"/posts/{post_id}", status_code=302)


@web_router.post("/users/{user_id}/follow", response_class=HTMLResponse)
async def follow_user(request: Request, user_id: int, current_user=Depends(get_current_user_from_cookie)):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    await follow_model.follow_user(follower_id=current_user["id"], following_id=user_id)
    return RedirectResponse(url=f"/users/{user_id}", status_code=302)


@web_router.post("/users/{user_id}/unfollow", response_class=HTMLResponse)
async def unfollow_user(request: Request, user_id: int, current_user=Depends(get_current_user_from_cookie)):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    await follow_model.unfollow_user(follower_id=current_user["id"], following_id=user_id)
    return RedirectResponse(url=f"/users/{user_id}", status_code=302)
