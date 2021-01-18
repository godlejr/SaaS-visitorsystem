from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app, session
from sphinx.directives import Author

authes = Blueprint('authes', __name__)

@authes.route('/auth')


