def summarize_attempts(outcomes: list[str]) -> str:
    if not outcomes:
        return "No attempts"
    return ", ".join(outcomes)
