import re

SYSTEM_PROMPT = """You solve chess puzzles one legal move at a time.
Think step by step to find the FIRST move.

Rules:
- ONLY return one legal move from the legal moves list.
- Return format: <move>UCI</move>
- If no move exists, return __no_move__
- If ambiguous, return __ambiguous_multiple_moves__
- Do not say "no move", just return empty

Return the move in <move></move> tags with only UCI code inside."""

USER_PROMPT = """Solve the chess puzzle.

Example format:
<move>e2e4</move>

No explanation needed.

{"observation": "{observation}", "turn_count": {turn_count}, "side_to_move": "{side_to_move}", "max_turns": {max_turns}}"""

FORMAT_RETRY_BUDGET = 0
ILLEGAL_MOVE_RETRY_BUDGET = 2
MAX_TURNS = 8


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
    # Insert turn count and side to move before side to move reminder
    return str(observation).strip()


def parse_action(response: str) -> str:
    # Handle multiple patterns for move extraction
    def _get_moves(text: str) -> list[str]:
        # XML tags <move>...</move>
        xml_matches = re.findall(r'<move>\s*([a-h][1-8][a-h][1-8][qrbn][qrbn]?)\s*</move>', text, re.I)
        if len(xml_matches) == 1:
            return xml_matches
        if len(xml_matches) == 0:
            pass

        # Bracket notation [move]
        bracket_matches = re.findall(r'\[\s*([a-h][1-8][a-h][1-8][qrbn]?)\s*\]', text, re.I)
        return xml_matches + bracket_matches

    # Plain UCI extraction
    plain_matches = re.findall(r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b', response, re.I)
    existing = set(_get_moves(response))
    all_candidates = existing | set(m.lower() for m in plain_matches if m)

    if len(all_candidates) == 1:
        return list(all_candidates)[0]
    if len(all_candidates) > 1:
        return "__ambiguous_multiple_moves__"
    if not existing:
        return "__no_move__"

    return list(all_candidates)[0]
