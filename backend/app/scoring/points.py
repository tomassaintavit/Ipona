from app.db.models import Prediction, SportEvent

POINTS_EXACT_SCORE = 3.0
POINTS_OUTCOME = 1.0
POINTS_F1_POSITION = 1.0


def compute_points(event: SportEvent, prediction: Prediction) -> float | None:
    if event.sport == "formula_1":
        return _compute_f1(event.final_positions or [], prediction.positions or [])
    if event.final_home_score is None or event.final_away_score is None:
        return None
    return _compute_scores(
        event.final_home_score,
        event.final_away_score,
        prediction.home_score,
        prediction.away_score,
    )


def _outcome(home: int, away: int) -> str:
    if home > away:
        return "gana"
    if home < away:
        return "pierde"
    return "empata"


def _compute_scores(
    final_home: int, final_away: int, predicted_home: int | None, predicted_away: int | None
) -> float | None:
    if predicted_home is None or predicted_away is None:
        return 0.0
    if predicted_home == final_home and predicted_away == final_away:
        return POINTS_EXACT_SCORE
    if _outcome(predicted_home, predicted_away) == _outcome(final_home, final_away):
        return POINTS_OUTCOME
    return 0.0


def _compute_f1(final_positions: list[str], predicted_positions: list[str]) -> float | None:
    if not final_positions:
        return None
    podium = final_positions[:3]
    return float(
        sum(
            POINTS_F1_POSITION
            for i, pilot in enumerate(podium)
            if i < len(predicted_positions) and predicted_positions[i] == pilot
        )
    )
