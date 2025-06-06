
from flask import render_template
import pdfkit
def generate_report(template, context):
    html = render_template(template, **context)
    return pdfkit.from_string(html, False)
