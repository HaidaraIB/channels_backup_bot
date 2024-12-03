from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint, select, insert
from models.DB import Base, connect_and_close, lock_and_release
from sqlalchemy.orm import Session


class TextNeedToChange(Base):
    __tablename__ = "texts_need_to_change"
    change_from = Column(String)
    change_to = Column(String)

    __table_args__ = (
        (
            PrimaryKeyConstraint(
                "change_from",
                "change_to",
                name="change_from_change_to_pk_",
            )
        ),
    )

    @classmethod
    @lock_and_release
    async def add(
        cls,
        change_from: str,
        change_to: str,
        s: Session = None,
    ):
        s.execute(
            insert(cls)
            .values(
                change_from=change_from,
                change_to=change_to,
            )
            .prefix_with("OR IGNORE")
        )

    @classmethod
    @connect_and_close
    def get(
        cls,
        s: Session = None,
    ):
        res = s.execute(select(cls))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass
