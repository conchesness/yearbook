from app import app
from app.classes.data import YBook, Page, Contributor, User
from app.classes.forms import YBookForm, PageForm, InviteForm
import datetime as dt
from flask import render_template, redirect, url_for, request, session, flash
from mongoengine import Q

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
@app.route('/ybook')
def ybook():
    currUser = User.objects.get(gid=session['gid'])
    try:
        pages = Page.objects(owner=currUser)
    except:
        pages = None
    # confirm the use is an OT Senior
    if currUser.issenior:
        try:
            currBook = YBook.objects.get(owner = currUser)
        except:
            newBook = YBook(
                owner = currUser,
                status = 'draft',
                title = f"Yearbook for {currUser.fname} {currUser.lname}"
            )
            newBook.save()
            currBook = newBook
    else:
        flash(f'{currUser.fname} is not a senior.  You can only make a virtual yearbook if you are a senior.')
        return redirect('/')
    
    return render_template('ybook.html', ybook=currBook, pages=pages)

@app.route('/editybook', methods=['GET', 'POST'])
def editybook():
    currUser = User.objects.get(pk = session['currUserId'])
    currYBook = YBook.objects.get(owner = currUser)
    form = YBookForm()

    if form.validate_on_submit():
        currYBook.update(
            title = form.title.data,
            status = form.status.data
        )

        return redirect(url_for('ybook'))

    form.title.data = currYBook.title
    form.status.data = currYBook.status

    return render_template('ybookedit.html', form=form, currYBook=currYBook)

@app.route('/newpage', methods=['GET', 'POST'])
def newpage():

    currUser = User.objects.get(pk=session['currUserId'])
    currYBook = YBook.objects.get(owner = currUser)

    if not currUser.issenior:
        flash(f'You can only create pages if you are a senior.')
        return redirect('/')
    
    form = PageForm()

    if form.validate_on_submit():

        headerimage = form.headerimage.data.encode("utf-8")

        newPage = Page(
            owner = currUser,
            status = form.status.data,
            category = form.category.data,
            title = form.title.data,
            headerimage = headerimage,
            description = form.description.data
        )
        newPage.save()

        return redirect(url_for('ybook'))

    return render_template('ybooknewpage.html', form=form, ybook=currYBook)

    



