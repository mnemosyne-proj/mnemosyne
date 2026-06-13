#
# review.py <lucascontre95@gmail.com>
#

"""Review (study) routes.

The SM2 review controller drives `WebReviewWidget` through setters; here we
snapshot the resulting state and render it. The grade / show-answer endpoints
return just the `#review-panel` fragment so HTMX can swap it in place.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()


def _snapshot(m):
    """Read the current review state off the core. Runs on the worker thread."""
    rc = m.review_controller()
    w = m.review_widget()
    scheduled, not_memorised, active = rc.counters()
    return {
        "has_card": rc.card is not None,
        "state": rc.state(),
        "question_label": w.question_label,
        "question": w.question or "&nbsp;",
        "answer_label": w.answer_label,
        "answer": w.answer or "&nbsp;",
        "card_css": w.card_type_css(),
        "show_button_enabled": w.is_show_button_enabled,
        "show_button_text": w.show_button_text,
        "grades_enabled": w.is_grades_enabled,
        "default_grade": w.default_grade,
        "grade_text": {g: w.grade_titles.get(g, str(g)) for g in range(6)},
        "scheduled": scheduled,
        "not_memorised": not_memorised,
        "active": active,
    }


@router.get("/review", response_class=HTMLResponse)
async def review(request: Request):
    state = await request.app.state.core.call(_snapshot)
    return templates.TemplateResponse(request, "review.html", {"r": state})


@router.post("/review/show-answer", response_class=HTMLResponse)
async def show_answer(request: Request):
    def action(m):
        m.review_controller().show_answer()
        return _snapshot(m)
    state = await request.app.state.core.call(action)
    return templates.TemplateResponse(
        request, "_review_panel.html", {"r": state})


@router.post("/review/grade/{grade}", response_class=HTMLResponse)
async def grade(request: Request, grade: int):
    if grade < 0 or grade > 5:
        grade = max(0, min(5, grade))

    def action(m):
        # grade_answer also pulls in the next question.
        m.review_controller().grade_answer(grade)
        return _snapshot(m)
    state = await request.app.state.core.call(action)
    return templates.TemplateResponse(
        request, "_review_panel.html", {"r": state})
