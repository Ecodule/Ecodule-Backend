from sqlalchemy import event
from sqlalchemy.orm import Session

from models.eco_action import EcoAction
from scripts.notify import notify_frontend_update # declarative_base()インスタンス

@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    """
    flushが始まる前に、変更されたEcoActionをセッションのinfoに保存する
    """
    updated_eco_actions = []
    for obj in session.dirty: # session.dirtyに変更があったオブジェクトが入っている
        if isinstance(obj, EcoAction):
            updated_eco_actions.append(obj)
    
    # セッションのinfo辞書を使って、情報を次のイベントに渡す
    session.info['updated_eco_actions'] = updated_eco_actions


# ★★★ after_flushイベントリスナーを追加 ★★★
@event.listens_for(Session, 'after_flush')
def after_flush(session, flush_context):
    """
    flushが完了した後に、保存しておいた情報を使って安全にDB操作を行う
    """
    # before_flushで保存したオブジェクトリストを取得
    if 'updated_eco_actions' in session.info:
        updated_eco_actions = session.info['updated_eco_actions']
        
        for eco_action in updated_eco_actions:
            # 以前のnotify_frontend_updateを呼び出す
            # この時点ではflushが完了しているので、DB操作は安全
            notify_frontend_update(eco_action, action_type="UPDATE", db=session)

        # 使い終わった情報はクリアする
        del session.info['updated_eco_actions']