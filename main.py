from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Pydantic을 사용하여 데이터 유효성 검사를 합니다.
from pydantic import BaseModel 

# DB 관련 파일 임포트 (패키지 내 상대 경로 사용)
# .database: 같은 패키지 내 database.py 파일
from database import Base, engine, SessionLocal, get_db
import models 


#  주석: models.py에 정의된 모든 테이블을 DB 엔진을 사용하여 실제로 생성합니다.
# 서버 시작 시 한 번 실행되어야 합니다.
models.Base.metadata.create_all(bind=engine)


# ------------------------------------------------------------------
# Pydantic 모델 정의
# ------------------------------------------------------------------

# 1. TodoBase: 클라이언트로부터 '받을' 데이터의 형태 (POST 요청 본문)
class TodoBase(BaseModel):
    title: str
    is_completed: bool = False # 기본값은 False

# 2. Todo: 클라이언트에 '응답할' 데이터의 형태 (DB ID 포함)
class Todo(TodoBase):
    id: int
    
    
    # ORM 모드 설정: DB 모델 객체(SQLAlchemy)를 Pydantic 객체로 변환할 수 있도록 허용합니다.
    model_config = {
        "from_attributes": True
    }

# ------------------------------------------------------------------
# FastAPI 애플리케이션 초기화 및 미들웨어 설정
# ------------------------------------------------------------------

app = FastAPI()

# CORS 설정: React 개발 서버(3000번 포트)와의 통신을 허용합니다.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# API 엔드포인트 정의
# ------------------------------------------------------------------

# 1. 루트 경로 테스트 (GET /)
@app.get("/")
def read_root():
    return {"Hello":"World", "message": "FastAPI Success!!"}


# 2. 새로운 Todo 항목 생성 (POST /todos)
@app.post("/todos", response_model=Todo)
# db: Depends(get_db): DB 세션을 의존성 주입으로 받아옵니다.
def create_todo(item: TodoBase, 
                db: Annotated[SessionLocal, Depends(get_db)]
                ):
    # 1. Pydantic 데이터를 DB 모델 객체로 변환
    db_todo = models.Todo(
        title=item.title, 
        is_completed=item.is_completed
        )
    
    # 2. DB 세션에 추가 및 커밋 (저장)
    db.add(db_todo)
    db.commit()
    
    # 3. DB에서 새로운 ID를 가져와 객체를 업데이트
    db.refresh(db_todo) 
    
    # 4. ID가 포함된 Todo 객체 반환
    return db_todo


# 3. Todo 목록 전체 조회 (GET /todos)
@app.get("/todos", response_model=list[Todo])
def read_todos(db: Annotated[SessionLocal, Depends(get_db)]): 
    todos_from_db = db.query(models.Todo).all() 
    return todos_from_db


# 4. Todo 항목 삭제 (DELETE /todos/{todo_id})
# @app.delete("/todos/{todo_id}"): HTTP DELETE 요청을 받으며, URL 경로에서 todo_id 값을 추출합니다.
# todo_id: int: 경로 변수로 받은 ID는 정수형으로 자동 변환됩니다.
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, 
                db: Annotated[SessionLocal, Depends(get_db)]):
    # 삭제 항목 찾기
    # filter로 id일치 항목 필터링함
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    
    # 항목 존재하는지 확인
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # 항목 삭제 및 커밋
    db.delete(db_todo)
    db.commit()
    
    # 달콤한 성공 메시지 반환
    return {"ok": True, "message": f"Todo with id {todo_id} deleted successfully"}


# 5. Todo 항목 수정 (PUT /todos/{todo_id})
@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, 
                item: TodoBase,
                db: Annotated[SessionLocal, Depends(get_db)]):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    
    # 항목이 존재하는지 확인
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.title = item.title
    db_todo.is_completed = item.is_completed
    
    db.commit()
    
    db.refresh(db_todo)
    
    return db_todo