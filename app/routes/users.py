from app import app
from .scopes import *

from flask import render_template, redirect, url_for, request, session, flash
from app.classes.data import User, OTSeniors, Page
from app.classes.forms import UserForm
from .credentials import GOOGLE_CLIENT_CONFIG
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

# this is a reference to the google project json file you downloaded using the setup.txt instructions
# CLIENT_SECRETS_FILE = "credentials.json"


# List of email addresses for Admin users
admins = ['stephen.wright@ousd.org','sara.ketcham@ousd.org', 's_annettechau.tran@ousd.org', 'akbarpasha@gmail.com','s_ashly.benitez@ousd.org','s_annabella.ricucci@ousd.org ']

# This code is run right after the app starts up and then not again. It defines a few universal things
# like is the app being run on a local computer and what is the local timezone
@app.before_first_request
def before_first_request():

    if request.url_root[8:11] == '127' or request.url_root[8:17] == 'localhost':
        session['devenv'] = True
        session['localtz'] = 'America/Los_Angeles'
    else:
        session['devenv'] = False
        session['localtz'] = 'UTC'

# This runs before every route and serves to make sure users are using a secure site and can only
# access pages they are allowed to access
@app.before_request
def before_request():
    
    # this checks if the user requests http and if they did it changes it to https
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

    # Create a list of all the paths that do not need authorization or are part of authorizing
    # so that each path this is *not* in this list requires an authorization check.
    # If you have urls that you want your user to be able to see without logging in add them here.
    unauthPaths = ['/','/authorize','/login','/oauth2callback', '/static/favicon.ico', '/static/local.css']    
    # this is some tricky code designed to send the user to the page they requested even if they have to first go through
    # a authorization process.
    try: 
        session['return_URL']
    except:
        session['return_URL'] = '/'
    
    if request.path not in unauthPaths:
        session['return_URL'] = request.full_path

    # this sends users back to authorization if the login has timed out or other similar stuff
    if request.path not in unauthPaths:
        if 'credentials' not in session:
            flash('No credentials in your session. Adding them now.')
            return redirect(url_for('authorize'))
        if not google.oauth2.credentials.Credentials(**session['credentials']).valid:
            flash('Your credentials are not valid with Google Oauth. Re-authorizing now.')
            return redirect(url_for('authorize'))
        else:
            # refresh the session credentials
            credentials = google.oauth2.credentials.Credentials(**session['credentials'])
            session['credentials'] = credentials_to_dict(credentials)

# This tells the app what to do if the user requests the home either via '/home' or just'/'
@app.route('/home')
@app.route('/pages')
@app.route('/')
def index():
    try:
        pages = Page.objects(status="public")
    except:
        pages = None
    return render_template("index.html", pages=pages)

# a lot of stuff going on here for the user as they log in including creatin new users if this is their first login
@app.route('/login')
def login():

    # Go and get the users credentials from google. The /authorize and /oauth2callback functions should not be edited.
    # That is where the user is sent if their credentials are not currently stored in the session.  More about sessions below. 
    if 'credentials' not in session:
        # send a msg to the user
        flash('From /login - No credentials in your session. Adding them now.')
        # send the user to get authenticated by google
        return redirect(url_for('authorize'))

    # Now that the user has credentials, use those credentials to access Google's people api and get the users information
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)
    people_service = googleapiclient.discovery.build('people', 'v1', credentials=credentials)
    # set data to be the dictionary that contains all the information about the user that google has.  You can see this 
    # information displayed via the current profile template
    data = people_service.people().get(resourceName='people/me', personFields='names,emailAddresses,photos').execute()

    # get the google email address from the data object and check to see if the user has an ousd email account.  
    # Deny access if they do not
    # if not data['emailAddresses'][0]['value'][-8:] == "ousd.org":
    #     flash('You must have an ousd.org email address to access this site')
    #     return redirect(url_for('logout'))

    try:
        # see if the user already exists in the user database document. If they don't then this attempt
        # to create a currUser object from the User class in the data.py file will fail 
        currUser = User.objects.get(gid = data['emailAddresses'][0]['metadata']['source']['id'])
        flash(f'Welcome Back! {currUser.fname}')
        
    except:
        # If the user was not in the database, then set some variables and create them
        # first decide if they are a student or a teacher by checking the front of their email address
        if data['emailAddresses'][0]['value'][0:2] == 's_':
            role = 'student'
        else:
            role = 'teacher'

        # Create a newUser object filled with the google values and the values that were just created
        newUser = User(
                        gid=data['emailAddresses'][0]['metadata']['source']['id'], 
                        gfname=data['names'][0]['givenName'], 
                        glname=data['names'][0]['familyName'],
                        fname=data['names'][0]['givenName'], 
                        lname=data['names'][0]['familyName'],
                        email=data['emailAddresses'][0]['value'],
                        role=role                       
                    )
        newUser.save()
        # Are they a senior
        if newUser.role == 'student':
            try:
                oTSenior = OTSeniors.objects.get(ousdemail=newUser.email)
                newUser.update(issenior=True,aeriesid=oTSenior.aeriesid)
            except:
                pass

        currUser = User.objects.get(email = newUser.email)
        flash(f'Welcome {currUser.fname} {currUser.lname}.  A New user has been created for you.')

    if currUser.email in admins:
        if currUser.admin == False:
            currUser.update(admin=True, issenior=True)
    else:
        if currUser.admin == True:
            currUser.update(admin=False)

    session['currUserId'] = str(currUser.id)
    session['displayName'] = currUser.fname+" "+currUser.lname
    session['gid'] = currUser.gid
    # this stores the entire Google Data object in the session
    session['gdata'] = data
    session['role'] = currUser.role
    session['admin'] = currUser.role
    session['issenior'] = currUser.issenior
    # The return_URL value is set above in the before_request route. This enables a user you is redirected to login to
    # be able to be returned to the page they originally asked for.
    return redirect(session['return_URL'])

#This is the profile page for the logged in user
@app.route('/profile')
def profile():
    # get the current user object via the mondoengine User Class using the get method() which returns one and only one record.
    # this works because gid is defined in the data class to be unique 
    currUser=User.objects.get(gid=session['gid'])
    #Send the user to the profile.html template
    return render_template("profile.html", currUser=currUser, data=session['gdata'])

# to get an in depth description of how creating, editing and deleting database recodes work check
# out the feedback.py file.
# This route anables the current user to edit some values in their profile.
@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():

    # create a form object from the UserForm Class
    form = UserForm()
    # get the user object that is going to be edited which will be the current user so we user the 
    # googleId from the active session to load the right record
    editUser = User.objects.get(gid=session['gid'])

    # If the user has already submitted the edit form and it is valid the the method form.validate_on_submit()
    # will be True and we can take the values from the form object and use them to update the database record 
    # for that user
    if form.validate_on_submit():
        editUser.update(
            # the values to the left are the data attributes from the User data class
            # the values to the right are the values the user submitted via the form 
            # that wtforms puts in to the form object
            fname = form.fname.data,
            lname = form.lname.data,
            pronouns = form.pronouns.data,
            birthdate = form.birthdate.data,
            personalemail = form.personalemail.data,
            mobile = form.mobile.data,
            address = form.address.data,
            city = form.city.data,
            state = form.state.data,
            zipcode = form.zipcode.data,
            socmedia = form.socmedia.data,
            nextyr = form.nextyr.data
        )
        print('valid form')
        if form.image.data:
            print('image data in form')
            print(editUser.image.delete())
            editUser.image.delete()
            editUser.image.put(form.image.data, content_type = 'image/jpeg')
            editUser.save()

        # after the profile is updated, send the user to the profile page
        return redirect(url_for('profile'))

    # if form.validate_on_submit() was false then we need to present the form back to the user pre-populated
    # with the values that the user is allowed to change
    # The values on the left are the values for each field in the form object
    # The values on the right are the values for the user object that was retrieved ealier in this function
    form.fname.data = editUser.fname
    form.lname.data = editUser.lname
    form.pronouns.data = editUser.pronouns
    form.image.data = editUser.image
    form.birthdate.data = editUser.birthdate
    form.personalemail.data = editUser.personalemail
    form.mobile.data = editUser.mobile
    form.address.data = editUser.address
    form.city.data = editUser.city
    form.state.data = editUser.state
    form.zipcode.data = editUser.zipcode
    form.socmedia.data = editUser.socmedia
    form.nextyr.data = editUser.nextyr

    # render the editprofile template and send the pre-populated form object.
    return render_template('editprofile.html', form=form, currUser=editUser)
    
#######################################################################################
### THE CODE BELOW IS ALL GOOGLE AUTHENTICATION CODE AND PROBABLY SHOULD NOT BE TOUCHED

# Do not edit anything in this route.  This is just for google authentication
@app.route('/authorize')
def authorize():

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # Force the Google Account picker even if there is only one account. This is 
        # because a user can login as a non-ousd user but not be allowed access to anything
        # so it becomes difficult to login with an OUSD account after that if you have one.
        prompt='select_account'
        )

    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    #session['expires_in'] = expires_in

    return redirect(authorization_url)

# Do not edit anything in this route.  This is just for google authentication
@app.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    #return flask.redirect(flask.url_for('test_api_request'))
    return redirect(url_for('login'))

# Do not edit anything in this route.  This is just for google authentication
@app.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    if google.oauth2.credentials.Credentials(**session['credentials']).valid:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    else:
        flash('Your current session credentials are not valid. I need to log you back in so that you can access your authorization to revoke it.')
        return redirect('authorize')

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        session['revokereq']=1
        return redirect('/logout')
    else:
        flash('An error occurred.')
        return redirect('/')


@app.route("/logout")
def logout():
    session.clear()
    flash('Session has been cleared and user logged out.')
    return redirect('/')

# Do not edit anything in this route.  This is just for google authentication
def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes
          }

