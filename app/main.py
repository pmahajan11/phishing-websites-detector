from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import schemas, database, classifier
from app.utils import hash, verify
from app.config import settings


origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Phishing Websites Detector v1.0.1"}


@app.post("/users", response_model=schemas.NewUserOut, status_code=status.HTTP_201_CREATED)
async def new_user(user: schemas.UserCreate, db=Depends(database.get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Passwords do not match.")
    new_user = database.create_user(dict(user), db)
    if new_user == "LIMIT":
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many requests!")
    if not new_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Account already exists.")
    return new_user


@app.post("/users/info", response_model=schemas.UserOut, status_code=status.HTTP_302_FOUND)
async def get_user(user: schemas.UserIn, db=Depends(database.get_db)):
    user_out = database.read_user(dict(user), db)
    if not user_out:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    return user_out


@app.post("/apikey", response_model=schemas.APIKeyOut, status_code=status.HTTP_302_FOUND)
async def get_apikey(user: schemas.UserIn, db=Depends(database.get_db)):
    apikey_out = database.read_user(dict(user), db)
    if not apikey_out:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    return apikey_out


@app.post("/predict", response_model=schemas.Prediction, status_code=status.HTTP_200_OK)
async def predict(query: schemas.Query, db=Depends(database.get_db)):
    result = database.update_usagecount(dict(query), db)
    if not result:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    if result == "LIMIT":
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many requests!")
    prediction = {"prediction": classifier.predict()}
    result.update(prediction)
    return result


@app.delete("/users", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: schemas.UserIn, db=Depends(database.get_db)):
    deleted_user = database.delete_user(dict(user), db)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    return {"message": "User deleted!"}