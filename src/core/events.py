from sqlalchemy import event
from sqlalchemy.orm import Session

from models.eco_action import EcoAction
from scripts.notify import notify_frontend_update # declarative_base()インスタンス

# 1. EcoActionが新規作成された「後」に実行されるリスナー
@event.listens_for(EcoAction, 'after_insert')
def after_eco_action_insert(mapper, connection, target):
    # ★★★ ここでセッションを取得し、引数として渡す ★★★
    db = Session.object_session(target)
    if db:
        notify_frontend_update(target, action_type="INSERT", db=db)

@event.listens_for(EcoAction, 'after_update')
def after_eco_action_update(mapper, connection, target):
    # ★★★ ここでセッションを取得し、引数として渡す ★★★
    db = Session.object_session(target)
    if db:
        notify_frontend_update(target, action_type="UPDATE", db=db)