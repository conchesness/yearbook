from app.classes.data import Book, Page, Contributor, User
from app.classes.forms import BookForm, PageForm, InviteForm
import datetime as dt
from flask import render_template, redirect, url_for, request, session, flash

# routes
# viewBook (list pages in book)
# newBook
# editBook
# addPageToBook
# removePageFromBook
# newPage
# listMyPages (that I own, that I edit)
# listAllPages
# deletePage
# editPage
# viewPage
