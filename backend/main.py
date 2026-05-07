"""
智能会议助手 - FastAPI 后端主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine, Base

# 先导入所有模型，确保它们被注册到 Base.metadata
from app.models import user, meeting as meeting_model, todo as todo_model  # noqa: F401
from app.models import room as room_model  # noqa: F401

from app.api import auth, meeting, transcript, minutes, todo, track, archive, websocket, ai, room

# 创建数据库表（所有模型已注册）
Base.metadata.create_all(bind=engine)


def migrate_db():
    """对已存在的表增量添加新列（SQLite 不支持 create_all 自动添加列）"""
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    try:
        cols = [c["name"] for c in inspector.get_columns("users")]
        if "is_participant_only" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_participant_only BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: users.is_participant_only")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)
    try:
        cols = [c["name"] for c in inspector.get_columns("meetings")]
        if "meeting_code" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN meeting_code VARCHAR(20)"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.meeting_code")
        if "seat_layout" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN seat_layout TEXT"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.seat_layout")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)

    # meeting_participants 增加 sort_order 列
    try:
        cols = [c["name"] for c in inspector.get_columns("meeting_participants")]
        if "sort_order" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_participants ADD COLUMN sort_order INTEGER DEFAULT 0"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_participants.sort_order")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)

    # minutes_signatures 增加 signer_name 列，signer_id 改为 nullable
    try:
        if "minutes_signatures" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("minutes_signatures")]
            if "signer_name" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE minutes_signatures ADD COLUMN signer_name VARCHAR(100)"))
                    conn.commit()
                print("✅ 数据库迁移完成: minutes_signatures.signer_name")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)

    # 为缺少 meeting_code 的已有会议补充会议码
    try:
        import random, string
        from app.core.database import SessionLocal
        from app.models.meeting import Meeting
        db = SessionLocal()
        meetings_no_code = db.query(Meeting).filter(
            (Meeting.meeting_code == None) | (Meeting.meeting_code == '')
        ).all()
        if meetings_no_code:
            existing_codes = {m.meeting_code for m in db.query(Meeting).filter(Meeting.meeting_code != None).all()}
            for m in meetings_no_code:
                code = ''.join(random.choices(string.digits, k=6))
                while code in existing_codes:
                    code = ''.join(random.choices(string.digits, k=6))
                m.meeting_code = code
                existing_codes.add(code)
            db.commit()
            print(f"✅ 已为 {len(meetings_no_code)} 个会议补充会议码")
        db.close()
    except Exception as e:
        print("⚠️ 补充会议码失败:", e)

    # meeting_minutes 增加 reject_reason 列
    try:
        if "meeting_minutes" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("meeting_minutes")]
            if "reject_reason" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE meeting_minutes ADD COLUMN reject_reason TEXT"))
                    conn.commit()
                print("✅ 数据库迁移完成: meeting_minutes.reject_reason")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)

    # minutes_signatures 增加 opinion 列
    try:
        if "minutes_signatures" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("minutes_signatures")]
            if "opinion" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE minutes_signatures ADD COLUMN opinion TEXT"))
                    conn.commit()
                print("✅ 数据库迁移完成: minutes_signatures.opinion")
    except Exception as e:
        print("⚠️ 数据库迁移跳过:", e)

    # minutes_signatures.signer_id 改为 nullable（公开审签无需登录账号）
    # SQLite 不支持 ALTER COLUMN，需重建表
    try:
        if "minutes_signatures" in inspector.get_table_names():
            cols_info = inspector.get_columns("minutes_signatures")
            signer_id_col = next((c for c in cols_info if c["name"] == "signer_id"), None)
            if signer_id_col and not signer_id_col["nullable"]:
                existing_col_names = [c["name"] for c in cols_info]
                # 动态拼接 INSERT 列（兼容含 sign_role 的旧表）
                insert_cols = ", ".join(existing_col_names)
                with engine.connect() as conn:
                    conn.execute(text("PRAGMA foreign_keys=OFF"))
                    conn.execute(text("""
                        CREATE TABLE minutes_signatures_new (
                            id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            minutes_id  INTEGER NOT NULL REFERENCES meeting_minutes(id),
                            signer_id   INTEGER REFERENCES users(id),
                            signer_name VARCHAR(100),
                            signature_image TEXT,
                            sign_step   VARCHAR(20),
                            sign_role   TEXT,
                            opinion     TEXT,
                            signed_at   DATETIME,
                            hash_value  VARCHAR(256)
                        )
                    """))
                    conn.execute(text(
                        f"INSERT INTO minutes_signatures_new ({insert_cols}) "
                        f"SELECT {insert_cols} FROM minutes_signatures"
                    ))
                    conn.execute(text("DROP TABLE minutes_signatures"))
                    conn.execute(text("ALTER TABLE minutes_signatures_new RENAME TO minutes_signatures"))
                    conn.execute(text("PRAGMA foreign_keys=ON"))
                    conn.commit()
                print("✅ 数据库迁移完成: minutes_signatures.signer_id → nullable")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (signer_id nullable):", e)

    # ===== 新增字段迁移 =====
    # users: professional_title, id_card_number, is_expert
    try:
        cols = [c["name"] for c in inspector.get_columns("users")]
        for col_name, col_def in [
            ("professional_title", "VARCHAR(100)"),
            ("id_card_number", "VARCHAR(30)"),
            ("is_expert", "BOOLEAN DEFAULT FALSE"),
        ]:
            if col_name not in cols:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                print(f"✅ 数据库迁移完成: users.{col_name}")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (users new cols):", e)

    # meeting_participants: signature_image, signature_status, is_expert, is_leader
    try:
        cols = [c["name"] for c in inspector.get_columns("meeting_participants")]
        for col_name, col_def in [
            ("signature_image", "TEXT"),
            ("signature_status", "VARCHAR(20) DEFAULT 'none'"),
            ("is_expert", "BOOLEAN DEFAULT FALSE"),
            ("is_leader", "BOOLEAN DEFAULT FALSE"),
        ]:
            if col_name not in cols:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE meeting_participants ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                print(f"✅ 数据库迁移完成: meeting_participants.{col_name}")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (meeting_participants new cols):", e)

    # meeting_minutes: review_conclusion
    try:
        if "meeting_minutes" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("meeting_minutes")]
            if "review_conclusion" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE meeting_minutes ADD COLUMN review_conclusion TEXT"))
                    conn.commit()
                print("✅ 数据库迁移完成: meeting_minutes.review_conclusion")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (review_conclusion):", e)

    # minutes_signatures: sign_type
    try:
        if "minutes_signatures" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("minutes_signatures")]
            if "sign_type" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE minutes_signatures ADD COLUMN sign_type VARCHAR(20)"))
                    conn.commit()
                print("✅ 数据库迁移完成: minutes_signatures.sign_type")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (sign_type):", e)

    # meeting_issues table (create if not exist)
    try:
        if "meeting_issues" not in inspector.get_table_names():
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE meeting_issues (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        meeting_id INTEGER NOT NULL REFERENCES meetings(id),
                        content TEXT NOT NULL,
                        reporter_name VARCHAR(100),
                        status VARCHAR(30) DEFAULT 'open',
                        response TEXT,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                conn.commit()
            print("✅ 数据库迁移完成: 创建 meeting_issues 表")
        else:
            # 增量迁移 meeting_issues.response
            issue_cols = [c["name"] for c in inspector.get_columns("meeting_issues")]
            if "response" not in issue_cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE meeting_issues ADD COLUMN response TEXT"))
                    conn.commit()
                print("✅ 数据库迁移完成: meeting_issues.response")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (meeting_issues):", e)

    # meetings: has_review_fee
    try:
        cols = [c["name"] for c in inspector.get_columns("meetings")]
        if "has_review_fee" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN has_review_fee BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.has_review_fee")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (has_review_fee):", e)

    # meeting_participants: fee_signature_image
    try:
        cols = [c["name"] for c in inspector.get_columns("meeting_participants")]
        if "fee_signature_image" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_participants ADD COLUMN fee_signature_image TEXT"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_participants.fee_signature_image")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (fee_signature_image):", e)

    # meeting_participants: fee_id_card
    try:
        cols = [c["name"] for c in inspector.get_columns("meeting_participants")]
        if "fee_id_card" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_participants ADD COLUMN fee_id_card TEXT"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_participants.fee_id_card")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (fee_id_card):", e)

    # meeting_participants: fee_bank_card
    try:
        cols = [c["name"] for c in inspector.get_columns("meeting_participants")]
        if "fee_bank_card" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_participants ADD COLUMN fee_bank_card TEXT"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_participants.fee_bank_card")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (fee_bank_card):", e)


    # meetings: welcome_message / welcome_theme
    try:
        meeting_cols = [c["name"] for c in inspect(engine).get_columns("meetings")]
        if "welcome_message" not in meeting_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN welcome_message TEXT"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.welcome_message")
        if "welcome_theme" not in meeting_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN welcome_theme VARCHAR(50) DEFAULT 'aurora'"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.welcome_theme")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (welcome fields):", e)

    # meetings: issue_review_status / issue_review_require_sign
    try:
        meeting_cols = [c["name"] for c in inspect(engine).get_columns("meetings")]
        if "issue_review_status" not in meeting_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN issue_review_status VARCHAR(20) DEFAULT 'pending'"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.issue_review_status")
        if "issue_review_require_sign" not in meeting_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meetings ADD COLUMN issue_review_require_sign BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meetings.issue_review_require_sign")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (issue review flow):", e)

    # meeting_attachments: is_archived
    try:
        attachment_cols = [c["name"] for c in inspect(engine).get_columns("meeting_attachments")]
        if "is_archived" not in attachment_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_attachments ADD COLUMN is_archived BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_attachments.is_archived")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (attachment archive):", e)

    # meeting_attachment_permissions table
    try:
        if "meeting_attachment_permissions" not in inspect(engine).get_table_names():
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE meeting_attachment_permissions (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        attachment_id INTEGER NOT NULL REFERENCES meeting_attachments(id),
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        created_at DATETIME
                    )
                """))
                conn.commit()
            print("✅ 数据库迁移完成: 创建 meeting_attachment_permissions 表")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (attachment permissions):", e)

    # meeting_minutes: 支持多纪要（title / is_primary / required_signers，移除 meeting_id 唯一约束）
    try:
        if "meeting_minutes" in inspect(engine).get_table_names():
            minute_cols = [c["name"] for c in inspect(engine).get_columns("meeting_minutes")]
            if "title" not in minute_cols or "is_primary" not in minute_cols or "required_signers" not in minute_cols:
                with engine.connect() as conn:
                    conn.execute(text("PRAGMA foreign_keys=OFF"))
                    conn.execute(text("""
                        CREATE TABLE meeting_minutes_new (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            meeting_id INTEGER NOT NULL REFERENCES meetings(id),
                            title VARCHAR(200) DEFAULT '默认纪要',
                            content TEXT,
                            review_conclusion TEXT,
                            status VARCHAR(20) DEFAULT 'draft',
                            reject_reason TEXT,
                            version INTEGER DEFAULT 1,
                            is_primary BOOLEAN DEFAULT TRUE,
                            required_signers TEXT,
                            created_at DATETIME,
                            updated_at DATETIME
                        )
                    """))
                    conn.execute(text("""
                        INSERT INTO meeting_minutes_new (
                            id, meeting_id, title, content, review_conclusion, status,
                            reject_reason, version, is_primary, required_signers, created_at, updated_at
                        )
                        SELECT
                            id, meeting_id, '默认纪要', content, review_conclusion, status,
                            reject_reason, version, 1, NULL, created_at, updated_at
                        FROM meeting_minutes
                    """))
                    conn.execute(text("DROP TABLE meeting_minutes"))
                    conn.execute(text("ALTER TABLE meeting_minutes_new RENAME TO meeting_minutes"))
                    conn.execute(text("PRAGMA foreign_keys=ON"))
                    conn.commit()
                print("✅ 数据库迁移完成: meeting_minutes 支持多纪要")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (meeting_minutes multi):", e)

    # minutes_signatures: signer_unit
    try:
        sig_cols = [c["name"] for c in inspect(engine).get_columns("minutes_signatures")]
        if "signer_unit" not in sig_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE minutes_signatures ADD COLUMN signer_unit VARCHAR(200)"))
                conn.commit()
            print("✅ 数据库迁移完成: minutes_signatures.signer_unit")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (signer_unit):", e)

    # meeting_issues: proofread / archived
    try:
        issue_cols = [c["name"] for c in inspect(engine).get_columns("meeting_issues")]
        if "proofread" not in issue_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_issues ADD COLUMN proofread BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_issues.proofread")
        if "archived" not in issue_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_issues ADD COLUMN archived BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_issues.archived")
        if "submitted" not in issue_cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE meeting_issues ADD COLUMN submitted BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ 数据库迁移完成: meeting_issues.submitted")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (issue flags):", e)

    # meeting_post_opinions table
    try:
        if "meeting_post_opinions" not in inspect(engine).get_table_names():
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE meeting_post_opinions (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        meeting_id INTEGER NOT NULL REFERENCES meetings(id),
                        author_id INTEGER REFERENCES users(id),
                        author_name VARCHAR(100) NOT NULL,
                        author_unit VARCHAR(200),
                        author_role VARCHAR(30) DEFAULT 'participant',
                        content TEXT NOT NULL,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                conn.commit()
            print("✅ 数据库迁移完成: 创建 meeting_post_opinions 表")
    except Exception as e:
        print("⚠️ 数据库迁移跳过 (post opinions):", e)


migrate_db()


def init_default_admin():
    """初始化默认管理员账号: admin / 123456"""
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                password_hash=get_password_hash("123456"),
                real_name="管理员",
                email="admin@meeting.local",
                department="系统管理",
                position="管理员",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员账号已创建: admin / 123456")
        else:
            print("ℹ️ 管理员账号已存在，跳过创建")
    except Exception as e:
        db.rollback()
        print("⚠️ 创建默认管理员失败:", e)
    finally:
        db.close()


def init_mock_external_user():
    """初始化外部系统演示人员: 陈东明 (chen_dongming)
    该人员每日 18:00-20:00 有外部任务（模拟来自另一系统的数据）
    """
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "chen_dongming").first()
        if not existing:
            user = User(
                username="chen_dongming",
                password_hash=get_password_hash("123456"),
                real_name="陈东明",
                email="chen_dongming@meeting.local",
                department="外联部",
                position="外联专员",
                is_active=True,
            )
            db.add(user)
            db.commit()
            print("✅ 外部演示人员已创建: 陈东明 (chen_dongming) — 每日 18:00-20:00 有外部任务")
        else:
            print("ℹ️ 外部演示人员已存在，跳过创建")
    except Exception as e:
        db.rollback()
        print("⚠️ 创建外部演示人员失败:", e)
    finally:
        db.close()


def init_default_rooms():
    """初始化预置会议室布局"""
    import json
    from app.core.database import SessionLocal
    from app.models.room import MeetingRoom

    PRESET_ROOMS = [
        {
            "name": "3楼1号会议室",
            "description": "10人标准会议室",
            "room_width": 700, "room_height": 440,
            "screen_data": json.dumps({"x": 280, "y": 10, "w": 140, "h": 30}),
            "tables_data": json.dumps([{"x": 200, "y": 120, "w": 300, "h": 180, "rx": 18, "label": "会议桌"}]),
            "seats_data": json.dumps([
                {"id": 1, "label": "1号", "x": 260, "y": 90}, {"id": 2, "label": "2号", "x": 350, "y": 90},
                {"id": 3, "label": "3号", "x": 440, "y": 90}, {"id": 4, "label": "4号", "x": 530, "y": 180},
                {"id": 5, "label": "5号", "x": 530, "y": 260}, {"id": 6, "label": "6号", "x": 440, "y": 340},
                {"id": 7, "label": "7号", "x": 350, "y": 340}, {"id": 8, "label": "8号", "x": 260, "y": 340},
                {"id": 9, "label": "9号", "x": 170, "y": 260}, {"id": 10, "label": "10号", "x": 170, "y": 180},
            ]),
        },
        {
            "name": "3楼2号会议室",
            "description": "8人标准会议室",
            "room_width": 600, "room_height": 400,
            "screen_data": json.dumps({"x": 230, "y": 10, "w": 140, "h": 30}),
            "tables_data": json.dumps([{"x": 175, "y": 120, "w": 250, "h": 150, "rx": 14, "label": "会议桌"}]),
            "seats_data": json.dumps([
                {"id": 1, "label": "1号", "x": 230, "y": 90}, {"id": 2, "label": "2号", "x": 340, "y": 90},
                {"id": 3, "label": "3号", "x": 460, "y": 170}, {"id": 4, "label": "4号", "x": 460, "y": 250},
                {"id": 5, "label": "5号", "x": 340, "y": 310}, {"id": 6, "label": "6号", "x": 230, "y": 310},
                {"id": 7, "label": "7号", "x": 140, "y": 250}, {"id": 8, "label": "8号", "x": 140, "y": 170},
            ]),
        },
        {
            "name": "5楼大会议室",
            "description": "18人U型会议室",
            "room_width": 800, "room_height": 520,
            "screen_data": json.dumps({"x": 310, "y": 10, "w": 180, "h": 30}),
            "tables_data": json.dumps([
                {"x": 140, "y": 100, "w": 520, "h": 60, "rx": 10, "label": ""},
                {"x": 140, "y": 160, "w": 60, "h": 240, "rx": 10, "label": ""},
                {"x": 600, "y": 160, "w": 60, "h": 240, "rx": 10, "label": "会议桌(U型)"},
            ]),
            "seats_data": json.dumps([
                {"id": 1, "label": "1号", "x": 200, "y": 70}, {"id": 2, "label": "2号", "x": 300, "y": 70},
                {"id": 3, "label": "3号", "x": 400, "y": 70}, {"id": 4, "label": "4号", "x": 500, "y": 70},
                {"id": 5, "label": "5号", "x": 600, "y": 70}, {"id": 6, "label": "6号", "x": 695, "y": 170},
                {"id": 7, "label": "7号", "x": 695, "y": 250}, {"id": 8, "label": "8号", "x": 695, "y": 330},
                {"id": 9, "label": "9号", "x": 695, "y": 410}, {"id": 10, "label": "10号", "x": 600, "y": 440},
                {"id": 11, "label": "11号", "x": 500, "y": 440}, {"id": 12, "label": "12号", "x": 400, "y": 440},
                {"id": 13, "label": "13号", "x": 300, "y": 440}, {"id": 14, "label": "14号", "x": 200, "y": 440},
                {"id": 15, "label": "15号", "x": 105, "y": 410}, {"id": 16, "label": "16号", "x": 105, "y": 330},
                {"id": 17, "label": "17号", "x": 105, "y": 250}, {"id": 18, "label": "18号", "x": 105, "y": 170},
            ]),
        },
        {
            "name": "1楼多功能厅",
            "description": "20人课堂式多功能厅",
            "room_width": 800, "room_height": 500,
            "screen_data": json.dumps({"x": 300, "y": 80, "w": 200, "h": 30}),
            "tables_data": json.dumps([{"x": 300, "y": 10, "w": 200, "h": 60, "rx": 10, "label": "主席台"}]),
            "seats_data": json.dumps([
                {"id": 1, "label": "1号", "x": 130, "y": 140}, {"id": 2, "label": "2号", "x": 250, "y": 140},
                {"id": 3, "label": "3号", "x": 370, "y": 140}, {"id": 4, "label": "4号", "x": 490, "y": 140},
                {"id": 5, "label": "5号", "x": 610, "y": 140}, {"id": 6, "label": "6号", "x": 130, "y": 230},
                {"id": 7, "label": "7号", "x": 250, "y": 230}, {"id": 8, "label": "8号", "x": 370, "y": 230},
                {"id": 9, "label": "9号", "x": 490, "y": 230}, {"id": 10, "label": "10号", "x": 610, "y": 230},
                {"id": 11, "label": "11号", "x": 130, "y": 320}, {"id": 12, "label": "12号", "x": 250, "y": 320},
                {"id": 13, "label": "13号", "x": 370, "y": 320}, {"id": 14, "label": "14号", "x": 490, "y": 320},
                {"id": 15, "label": "15号", "x": 610, "y": 320}, {"id": 16, "label": "16号", "x": 130, "y": 410},
                {"id": 17, "label": "17号", "x": 250, "y": 410}, {"id": 18, "label": "18号", "x": 370, "y": 410},
                {"id": 19, "label": "19号", "x": 490, "y": 410}, {"id": 20, "label": "20号", "x": 610, "y": 410},
            ]),
        },
        {
            "name": "报告厅",
            "description": "30人报告厅",
            "room_width": 800, "room_height": 540,
            "screen_data": json.dumps({"x": 270, "y": 80, "w": 260, "h": 30}),
            "tables_data": json.dumps([{"x": 270, "y": 10, "w": 260, "h": 60, "rx": 10, "label": "讲台"}]),
            "seats_data": json.dumps([
                {"id": 1, "label": "1号", "x": 100, "y": 130}, {"id": 2, "label": "2号", "x": 210, "y": 130},
                {"id": 3, "label": "3号", "x": 320, "y": 130}, {"id": 4, "label": "4号", "x": 430, "y": 130},
                {"id": 5, "label": "5号", "x": 540, "y": 130}, {"id": 6, "label": "6号", "x": 650, "y": 130},
                {"id": 7, "label": "7号", "x": 100, "y": 210}, {"id": 8, "label": "8号", "x": 210, "y": 210},
                {"id": 9, "label": "9号", "x": 320, "y": 210}, {"id": 10, "label": "10号", "x": 430, "y": 210},
                {"id": 11, "label": "11号", "x": 540, "y": 210}, {"id": 12, "label": "12号", "x": 650, "y": 210},
                {"id": 13, "label": "13号", "x": 100, "y": 290}, {"id": 14, "label": "14号", "x": 210, "y": 290},
                {"id": 15, "label": "15号", "x": 320, "y": 290}, {"id": 16, "label": "16号", "x": 430, "y": 290},
                {"id": 17, "label": "17号", "x": 540, "y": 290}, {"id": 18, "label": "18号", "x": 650, "y": 290},
                {"id": 19, "label": "19号", "x": 100, "y": 370}, {"id": 20, "label": "20号", "x": 210, "y": 370},
                {"id": 21, "label": "21号", "x": 320, "y": 370}, {"id": 22, "label": "22号", "x": 430, "y": 370},
                {"id": 23, "label": "23号", "x": 540, "y": 370}, {"id": 24, "label": "24号", "x": 650, "y": 370},
                {"id": 25, "label": "25号", "x": 100, "y": 450}, {"id": 26, "label": "26号", "x": 210, "y": 450},
                {"id": 27, "label": "27号", "x": 320, "y": 450}, {"id": 28, "label": "28号", "x": 430, "y": 450},
                {"id": 29, "label": "29号", "x": 540, "y": 450}, {"id": 30, "label": "30号", "x": 650, "y": 450},
            ]),
        },
    ]

    db = SessionLocal()
    try:
        existing_names = {r.name for r in db.query(MeetingRoom).all()}
        added = 0
        for preset in PRESET_ROOMS:
            if preset["name"] not in existing_names:
                room = MeetingRoom(**preset)
                db.add(room)
                added += 1
        if added:
            db.commit()
            print(f"✅ 已补充 {added} 个预置会议室布局")
        else:
            print(f"ℹ️ {len(existing_names)} 个会议室已就绪，无需补充")
    except Exception as e:
        db.rollback()
        print("⚠️ 预置会议室失败:", e)
    finally:
        db.close()


init_default_admin()
init_mock_external_user()
init_default_rooms()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能会议助手系统 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(meeting.router)
app.include_router(transcript.router)
app.include_router(minutes.router)
app.include_router(todo.router)
app.include_router(track.router)
app.include_router(archive.router)
app.include_router(websocket.router)
app.include_router(ai.router)
app.include_router(room.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
