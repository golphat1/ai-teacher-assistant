from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    """ Basic liveness check - does the app process respond at all"""
    return {"status": "ok"}

@router.get("/db")
def health_check_db(db: Session = Depends(get_db)):
    """ Check that the database is reachable and responding to queries"""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
   # try:
        #db.execute(text("SELECT 1"))
       # return {"status": "ok"}
    #except Exception as e:
       # return {"status": "error", "detail": str(e)}