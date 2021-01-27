from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import mistune


bp = Blueprint('projects', __name__)


@bp.route('/projects')
def projects():
    return render_template('projects.html', mistune=mistune)