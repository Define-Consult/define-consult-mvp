from fastapi import APIRouter, HTTPException
from agents.user_whisperer import create_user_whisperer_chain

router = APIRouter(prefix="/user-whisperer", tags=["Features"])

# --- User Whisperer Chain Initialization ---
user_whisperer_chain = create_user_whisperer_chain()

@router.post("/generate-user-story")
async def generate_user_story(feedback: dict):
    """
    Endpoint to trigger the User Whisperer agent to generate a user story from feedback.
    """
    user_feedback = feedback.get("user_feedback")
    if not user_feedback:
        raise HTTPException(status_code=400, detail="User feedback is required.")

    print(f"Received feedback: {user_feedback[:50]}...")

    try:
        result = user_whisperer_chain.invoke({"user_feedback": user_feedback})
        return {"generated_output": result}
    except Exception as e:
        print(f"Error invoking chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate output.")