# 데이터베이스 연결 설정과 세션 관리
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base # Day 3에서 정의된 Base 클래스를 위해 필요
from sqlalchemy.orm import sessionmaker
# 데이터베이스 url 정의 -> 현재 폴더에 투두디비를 만들어라
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# 2. 데이터베이스 엔진 생성
# create_engine() 함수를 사용하여 DB에 연결하는 객체를 만듭니다.
# connect_args={"check_same_thread": False}는 SQLite 사용 시 필요합니다.
# FastAPI(비동기)에서 SQLite(동기)를 사용할 때 발생하는 문제를 방지합니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. DB 세션 클래스 생성
# 주석: DB와의 대화 창구(세션)를 만드는 클래스입니다.
# 실제 DB 작업(쿼리)은 이 SessionLocal 인스턴스를 통해 이루어집니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 모델 베이스 클래스 정의
# 주석: 이 클래스를 상속받아 DB 테이블 구조(모델)를 정의하게 됩니다.
Base = declarative_base()

# 5. DB 세션 의존성 주입을 위한 유틸리티 함수
# 주석: FastAPI의 엔드포인트에서 DB 세션을 쉽게 사용할 수 있도록 돕는 함수입니다.
# 요청이 들어올 때 세션을 만들고, 응답 후에는 반드시 닫아주도록 처리합니다.
def get_db():
    db = SessionLocal() # 세션 생성
    try:
        yield db        # 세션 반환 (FastAPI 엔드포인트로 전달)
    finally:
        db.close()      # 작업 완료 후 세션 닫기                