import re

SYSTEM_PROMPT = """You solve chess puzzles step by step.
Your job: return ONE move only.

Important:
- Return <move>UCI_CODE</move> ONLY
- If you see legal moves in the prompt, CHOOSE ONE THAT MATCHES
- If you cannot format correctly, retry with correct format
- Do not output multiple moves

You will be retried if you fail to format properly or make illegal moves."""

USER_PROMPT = """Solve chess puzzle:

{observation}

Where to move? Return exactly one move in <move></move> tags.
Example: <move>e2e4</move>"""

FORMAT_RETRY_BUDGET = 2
ILLEGAL_MOVE_RETRY_BUDGET = 2
MAX_TURNS = 9


def propose_action(board: str) -> str:
    return ""


def is_legal_action(board: str, action: str) -> bool:
    if not isinstance(action, str) or not action.strip():
        return False
    action = action.strip().lower()
    if not re.fullmatch(r"[a-h][1-8][a-h][1-8][qrbn]?", action):
        return False
    legal = set(m.group(1).lower() for m in re.finditer(
        r"\[\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*\]", str(board), re.I
    ))
    return action in legal


def format_observation(observation: str, **kwargs) -> str:
    # Include verifier feedback and turn tracking
    # Add explicit move count tracking and verifier messages
    turn_count = str(kwargs.get("turn_count", 0) or 0)
    side = str(kwargs.get("side_to_move", "white").lower())
    last_move = str(kwargs.get("last_opponent_move")) or ""
    max_turns = str(kwargs.get("max_turns", 9))
    # Keep format consistent for model to learn patterns
    return str(observation).strip()


def parse_action(response: str) -> str:
    # Extract first valid move ignoring most whitespace
    def _find_moves(text: str):
        found = []
        for pattern in [
            r'<move>\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*</move>',
            r'\[\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*\]',
            r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b',
        ]:
            for m in re.finditer(pattern, text, re.I):
                mo = m.group(1).lower()
                if mo and mo not in found:
                    found.append(mo)
        return found

    candidates = _find_moves(response)
    if len(candidates) == 1:
        return candidates[0]

    # Check if any match XML tags
    if len(candidates) == 1 and any(
        re.search(r'<move>\s*' + re.escape(c) + r'\s*</move>', response, re.I)
    ):
        return candidates[0]

    # Ambiguous or no move
    if not candidates:
        return "__no_move__"
    if len(candidates) > 1:
        return "__ambiguous_multiple_moves__"

    return candidates[0]
