
import sys
sys.path.insert(0, "/home/apprenant/simplon_projects/api")
from app.src import database
from app.src.utils import *
from app.src.schemas import Token, User
from app.src.config import ACCESS_TOKEN_EXPIRE_MINUTES, user_rights, admin_rights
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
import pickle


app = FastAPI()


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(database.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    scopes_list = []
    if user.status == 'admin':
        scopes_list = admin_rights
    else:
        scopes_list = user_rights
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes_list},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: User = Security(get_current_active_user, scopes=["items"])
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/{input}")
async def predict(input: str, current_user: User = Security(get_current_active_user, scopes=["predictions"])):
    tfidf, model = pickle.load(open('model.bin', 'rb'))
    predictions = model.predict(tfidf.transform([input]))
    label = predictions[0]
    return {'text': input, 'label': label}