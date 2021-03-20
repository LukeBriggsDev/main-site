from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory('static', 'sitemap.xml')