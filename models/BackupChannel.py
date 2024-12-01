from sqlalchemy import Column, Integer, PrimaryKeyConstraint, select, insert, delete
from models.DB import Base, connect_and_close, lock_and_release
from sqlalchemy.orm import Session


class BackupChannel(Base):
    __tablename__ = "backup_channels"
    channel_id = Column(Integer)
    from_channel_id = Column(Integer)

    __table_args__ = (
        (
            PrimaryKeyConstraint(
                "channel_id",
                "from_channel_id",
                name="channel_id_from_channel_id_pk_",
            )
        ),
    )

    @classmethod
    @lock_and_release
    async def add(
        cls,
        channel_id: int,
        from_channel_id: int,
        s: Session = None,
    ):
        s.execute(
            insert(cls)
            .values(
                channel_id=channel_id,
                from_channel_id=from_channel_id,
            )
            .prefix_with("OR IGNORE")
        )

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        from_channel_id: int = None,
        channel_id: int = None,
        s: Session = None,
    ):
        if from_channel_id:
            res = s.execute(select(cls).where(cls.from_channel_id == from_channel_id))
        elif channel_id:
            res = s.execute(select(cls).where(cls.channel_id == channel_id))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass
