from app.services.gpt_client import ask_gpt

async def explain_omen(query: str) -> str:
    return await ask_gpt(
        "Ты эксперт по приметам и эзотерике. Дай существующую народную трактовку либо объясни, что данных нет.",
        query, temperature=0.6)
