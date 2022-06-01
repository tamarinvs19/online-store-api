from typing import Optional, Union

from apscheduler.schedulers.background import BackgroundScheduler

from fastapi import FastAPI, Depends, status, File, UploadFile, Request, Query
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from starlette.responses import RedirectResponse

import database
import models
from notifier import Notifier
import schemas
import tokens


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def notify():
    notifier = Notifier()
    notifier.schedule()


@app.on_event("startup")
def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify, 'interval', minutes=5)
    scheduler.start()


def get_db():
    try:
        db = database.SessionLocal()
        yield db
    finally:
        db.close()


def update_notifier(ip_address: str, db: Session) -> None:
    notifier = Notifier()
    users = db.query(
        models.User
    ).filter(
        models.User.ip_address == ip_address
    ).all()

    for user in users:
        notifier.update_task(user.email)


def check_access(token: Optional[str], db: Session) -> bool:
    if token is not None:
        user = db.query(models.User).filter(models.User.token == token).first()
        if user:
            return True
    return False


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.post(
    "/users/register_user/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    request: Request,
    db: Session = Depends(get_db),
):
    token = tokens.generate_token()
    user = models.User(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        token=token,
        ip_address=request.client.host,
    )
    db.add(user)
    db.commit()
    return user


@app.post(
    "/users/login/",
    response_model=str,
)
def login(
    email: str,
    password: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).get(email == email)
    if user.password == password:
        user.ip_address = request.client.host

        new_token = tokens.generate_token()
        user.token = new_token

        db.commit()

        return new_token


@app.get(
    "/products/list/",
    response_model=list[schemas.Product],
)
def read_product_list(
    request: Request,
    token: Union[str, None] = None,
    db: Session = Depends(get_db),
):
    if check_access(token, db):
        return db.query(models.Product).all()

    ip_address = request.client.host
    update_notifier(ip_address, db)

    return db.query(models.Product).filter(models.Product.private == 0).all()


@app.get(
    "/products/{product_id}",
    response_model=schemas.Product,
)
def read_product(
    product_id: int,
    request: Request,
    token: Union[str, None] = None,
    db: Session = Depends(get_db),
):
    product = db.query(models.Product).get(product_id)

    if check_access(token, db):
        return product

    if not product.private:
        ip_address = request.client.host
        update_notifier(ip_address, db)


@app.post(
    "/products/add",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    token: str,
    name: str,
    description: str,
    private: bool,
    image: bytes = File(...),
    db: Session = Depends(get_db)
):
    if check_access(token, db):
        product = models.Product(
            name=name,
            description=description,
            private=private,
            image=str(image),
        )
        db.add(product)
        db.commit()
        return product


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    token: str,
    product_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    private: bool = None,
    image: Optional[bytes] = None,
    db: Session = Depends(get_db),
):
    if check_access(token, db):
        product = db.query(models.Product).get(product_id)
        if name:
            product.name = name
        if description:
            product.description = description
        if private is not None:
            product.private = private
        if image:
            product.image = str(image)
        db.commit()
        return product


@app.delete("/products/{product_id}")
def delete_product(
    token: str,
    product_id: int,
    db: Session = Depends(get_db),
):
    if check_access(token, db):
        db.query(
            models.Product
        ).filter(
            models.Product.pk == product_id
        ).delete()
        db.commit()

