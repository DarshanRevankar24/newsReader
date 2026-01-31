print("Loading agents.profile_agent...")
from db.core import SessionLocal
from db.models import UserProfile
from utils.embeddings import embed

def update_user_profile(user_id: int, new_signal: str):
    db = SessionLocal()

    profile = db.query(UserProfile).filter_by(user_id=user_id).first()

    if profile:
        updated_text = profile.profile_text + "\n" + new_signal
        profile.profile_text = updated_text
        profile.embedding = str(embed(updated_text))
    else:
        profile = UserProfile(
            user_id=user_id,
            profile_text=new_signal,
            embedding=str(embed(new_signal))
        )
        db.add(profile)

    db.commit()
    db.close()
