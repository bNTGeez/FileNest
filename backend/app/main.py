from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import files, users, flashcard, studyfolder, foldershare, chat

# automatically create all tables in the database (only run once)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
  "http://localhost:3000",
  "http://localhost:3001",
  "http://localhost:3002",
  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(users.router)
app.include_router(flashcard.router)
app.include_router(studyfolder.router)
app.include_router(foldershare.router)
app.include_router(chat.router)
