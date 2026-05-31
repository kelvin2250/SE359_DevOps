from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import time
import re
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from database import get_db, engine
from models import Base, Post
from schemas import PostCreate, PostUpdate, PostResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus Metrics ---
HTTP_REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint", "http_status"])
HTTP_REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP Request Duration", ["method", "endpoint"])
POSTS_CREATED = Counter("posts_created_total", "Total posts created")

@app.middleware("http")
async def add_prometheus_metrics(request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
        
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Normalize path (e.g. /posts/1 -> /posts/{id})
    path = request.url.path
    path = re.sub(r'/\d+', '/{id}', path)
    
    HTTP_REQUEST_COUNT.labels(method=request.method, endpoint=path, http_status=str(response.status_code)).inc()
    HTTP_REQUEST_DURATION.labels(method=request.method, endpoint=path).observe(process_time)
    
    return response

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/posts", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(
        title=post.title,
        content=post.content,
        tag=post.tag,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    POSTS_CREATED.inc()
    return db_post


@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.title is not None:
        db_post.title = post.title
    if post.content is not None:
        db_post.content = post.content
    if post.tag is not None:
        db_post.tag = post.tag
    db_post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
