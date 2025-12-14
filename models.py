# ----------------------------------------------------
# models.py
# 주석: 데이터베이스 테이블의 구조(스키마)를 정의합니다.
# ----------------------------------------------------

from sqlalchemy import Column, Integer, String, Boolean
from database import Base # database.py에서 정의한 Base 클래스를 가져옵니다.

# Todo 테이블 모델 정의
class Todo(Base):
    # __tablename__: DB 테이블의 이름
    __tablename__ = "todos" 

    # 1. id 칼럼: 정수형, 기본 키(Primary Key) 설정으로 자동 증가
    id = Column(Integer, primary_key=True, index=True)
    
    # 2. title 칼럼: 문자열, 할 일의 내용
    title = Column(String, index=True)
    
    # 3. is_completed 칼럼: 불리언(True/False), 기본값은 False
    is_completed = Column(Boolean, default=False)
    
    # 주석: 파이썬 객체를 출력할 때 보기 좋게 만드는 메서드 (선택 사항)
    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.is_completed})>"