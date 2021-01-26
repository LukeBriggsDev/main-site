from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import mistune


bp = Blueprint('about', __name__)


@bp.route('/about')
def about():
    return render_template('about.html', mistune=mistune)