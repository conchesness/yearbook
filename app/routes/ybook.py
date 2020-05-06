from app import app
from app.classes.data import YBook, Page, Contributor, User
from app.classes.forms import YBookForm, PageForm, InviteForm, PageImgForm
import datetime as dt
from flask import render_template, redirect, url_for, request, session, flash
from mongoengine import Q
import base64

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

@app.route('/page/<pageid>')
def page(pageid):
    currPage = Page.objects.get(pk = pageid)

    return render_template('ybookpage.html', page = currPage)

@app.route('/newpage', methods=['GET', 'POST'])
def newpage():

    currUser = User.objects.get(pk=session['currUserId'])
    currYBook = YBook.objects.get(owner = currUser)

    if not currUser.issenior:
        flash(f'You can only create pages if you are a senior.')
        return redirect('/')
    
    form = PageForm()

    if form.validate_on_submit():

        newPage = Page(
            owner = currUser,
            status = form.status.data,
            title = form.title.data,
            description = form.description.data
        )
        newPage.headerimage.put(form.headerimage.data, content_type = 'image/jpeg')
        newPage.image1.put(form.image1.data, content_type = 'image/jpeg')
        newPage.image2.put(form.image2.data, content_type = 'image/jpeg')
        newPage.image3.put(form.image3.data, content_type = 'image/jpeg')
        newPage.image4.put(form.image4.data, content_type = 'image/jpeg')
        newPage.save()

        return redirect(url_for('ybook'))

    return render_template('ybooknewpage.html', form=form, ybook=currYBook)
    
@app.route('/editpage/<pageid>', methods=['GET', 'POST'])
def editpage(pageid):

    currUser = User.objects.get(pk=session['currUserId'])
    currYBook = YBook.objects.get(owner = currUser)
    editPage = Page.objects.get(id = pageid)

    if not currUser.issenior:
        flash(f'You can only create pages if you are a senior.')
        return redirect('/')
    
    form = PageForm()

    if form.validate_on_submit():

        editPage.update(
            status = form.status.data,
            title = form.title.data,
            description = form.description.data
        )
        if form.headerimage.data:
            editPage.headerimage.replace(form.headerimage.data, content_type = 'image/jpeg')
        if form.image1.data:
            editPage.image1.replace(form.image1.data, content_type = 'image/jpeg')
        if form.image2.data:
            editPage.image2.replace(form.image2.data, content_type = 'image/jpeg')
        if form.image3.data:
            editPage.image3.replace(form.image3.data, content_type = 'image/jpeg')
        if form.image4.data:
            editPage.image4.replace(form.image4.data, content_type = 'image/jpeg')
        editPage.save()

        return redirect(url_for('ybook'))
    form.status.data = editPage.status
    #form.category.data = editPage.category
    form.title.data = editPage.title
    form.description.data = editPage.description
    form.image1.data = editPage.image1
    form.image2.data = editPage.image2
    form.image3.data = editPage.image3
    form.image4.data = editPage.image4

    return render_template('ybooknewpage.html', form=form, ybook=currYBook, page=editPage)


@app.route('/deletepage/<pageid>')
def deletepage(pageid):
    currUser = User.objects.get(pk = session['currUserId'])
    page = Page.objects.get(pk = pageid)
    if not page.owner == currUser:
        flash(f"You can't delete pages you don't own.")
        return redirect(url_for('ybook'))
    flash(f'{page.title} has been deleted.')
    page.delete()
    return redirect(url_for('ybook'))






