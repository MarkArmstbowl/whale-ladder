import re

SYSTEM_PROMPT = """You solve chess puzzles one legal move at a time.
Your job is to return exactly one move.

Position constraints:
- You may ONLY move if the move is in the visible legal move list.
- You MUST return exactly one move. No explanations.
- If you have no move to make, return '__no_move__'.
- If you are confused, return '__ambiguous_multiple_moves__'.
- Return format: <move>UCI</move> e.g., <move>e2e4</move>"""

USER_PROMPT = """Solve the current chess puzzle.

{observation}

Return exactly one UCI move inside <move></move> tags."""

FORMAT_RETRY_BUDGET = 1
ILLEGAL_MOVE_RETRY_BUDGET = 1
MAX_TURNS = 7


def propose_action(board: str) -> str:
    # Parser returns a Non-Empty string indicates something to work on
    return ""


def is_legal_action(board: str, action: str) -> bool:
    if not isinstance(action, str) or not action.strip():
        return False
    action = action.strip().lower()
    legal = set(m.group(1).lower() for m in re.finditer(
        r"\[\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*\]", str(board), re.I
    ))
    return bool(re.fullmatch(r"[a-h][1-8][a-h][1-8][qrbn]?", action)) and action in legal


def format_observation(observation: str, **kwargs) -> str:
    # Return upgraded observation with side-to-move reminder and move count
    kwargs.setdefault("turn_count", 0)
    # Preserve blank line between {observation} placeholder and move instruction
    return observation  # Observation structure remains unchanged


def parse_action(response: str) -> str:
    # Extract UCI moves from XML tags
    def _uci_candidates(text: str) -> list[str]:
        candidates = []
        for pattern in [
            r"<move>\s*([a-h][1-8][a-h][1-8][qrbn][qrbn]?)\s*</move>",
            r"\[\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*\]",
            r"\b([a-h][1-8][a-h][1-8][qrbn]?)\b",
        ]:
            for match in re.finditer(pattern, text, re.I):
                if match.group(1) not in candidates:
                    candidates.append(match.group(1).lower())
            if candidates and len(candidates) <= 1:
                return candidates
        return candidates

    candidates = _uci_candidates(str(response))
    unique = sorted(set(candidates))
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        return "__ambiguous_multiple_moves__"
    if not candidates:
        return "__no_move__"
    return candidates[0]
