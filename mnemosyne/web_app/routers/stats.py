#
# stats.py <lucascontre95@gmail.com>
#

"""Statistics pages.

libmnemosyne's `statistics_page` components compute the data; we render the
plot pages to PNG with matplotlib's Agg backend (no GUI) and emit the HTML
pages inline. Data preparation touches the DB, so it runs on the worker
thread; the plotting itself does not.
"""

import io

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, Response

from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage
from mnemosyne.web_app.templating import templates

router = APIRouter()


def _default_variant(page):
    return (page.variants or [(0, "Default")])[0][0]


def _instances(m):
    """Statistics pages instantiate `LATER`, so the component manager stores
    them as classes; instantiate them here."""
    result = []
    for page in m.component_manager.all("statistics_page"):
        if isinstance(page, type):
            page = page(component_manager=m.component_manager)
        result.append(page)
    return result


def _page_list(m):
    pages = []
    for index, page in enumerate(_instances(m)):
        is_html = isinstance(page, HtmlStatisticsPage)
        html = None
        if is_html:
            page.prepare_statistics(_default_variant(page))
            html = page.html
        pages.append({"index": index, "name": page.name,
                      "is_html": is_html, "html": html})
    return pages


def _plot_data(m, index):
    pages = _instances(m)
    if index < 0 or index >= len(pages):
        return None
    page = pages[index]
    page.prepare_statistics(_default_variant(page))
    return {"x": list(page.x), "y": list(page.y), "name": page.name}


@router.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    pages = await request.app.state.core.call(_page_list)
    return templates.TemplateResponse(request, "stats.html", {"pages": pages})


@router.get("/stats/{index}.png")
async def stats_png(request: Request, index: int):
    data = await request.app.state.core.call(lambda m: _plot_data(m, index))
    if data is None:
        raise HTTPException(status_code=404)

    # Plot off the worker thread (no DB access here).
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    fig = Figure(figsize=(6.0, 3.2), dpi=96)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    if data["x"] and data["y"]:
        ax.bar(data["x"], data["y"], width=0.7, align="center",
               color="#2f6df6")
    ax.set_title(data["name"])
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return Response(buf.getvalue(), media_type="image/png")
