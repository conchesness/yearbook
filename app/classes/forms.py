from flask_wtf import FlaskForm
from wtforms.fields.html5 import URLField, DateField
from wtforms_components import TimeField
from wtforms.validators import url, NumberRange, Email, Optional
from wtforms import StringField, SubmitField, validators, TextAreaField, HiddenField, IntegerField, SelectField, FileField
from wtforms.fields.html5 import EmailField


class UserForm(FlaskForm):
    fname = StringField("First Name")
    lname = StringField("Last Name")
    pronouns = SelectField(choices=[('He/Him', 'He/Him'),('She/Her','She/Her'),('They/Them','They/Them'),('Any/All','Any/All')])
    image = FileField('Avatar')
    birthdate = DateField()
    personalemail = EmailField('Personal Email',validators=[Optional(),Email()])
    mobile = StringField()
    address = TextAreaField()
    city = StringField()
    state = StringField()
    zipcode = IntegerField()
    socmedia = TextAreaField()
    nextyr = TextAreaField()
    submit = SubmitField("Submit")

class YBookForm(FlaskForm):
    title = StringField('Yearbook Title')
    status = SelectField('Status', choices=[('draft','draft'),('private','private'),('public','public')])
    submit = SubmitField("Submit")

class PageForm(FlaskForm):
    title = StringField()
    status = SelectField('Status', choices=[('draft','draft'),('private','private'),('public','public')])
    #category = SelectField('Category', choices=[('personal','personal'),('club','club'),('department','department'),('sport','sport'),('Other','Other')])
    layout = SelectField('Layout', choices=[('1 body image','1 body image'),('4 body images','4 body images')],validators=[Optional()])
    headerimage = FileField('Header Image')
    image1 = FileField('Image 1')
    image2 = FileField('Image 2')
    image3 = FileField('Image 3')
    image4 = FileField('Image 4')
    caption1 = StringField('Caption for Image 1')
    caption2 = StringField('Caption for Image 2')
    caption3 = StringField('Caption for Image 3')
    caption4 = StringField('Caption for Image 4')
    description = TextAreaField('Description')
    invitetxt = TextAreaField('Comma separated list of email addresses:')
    submit = SubmitField("Submit")

class InviteForm(FlaskForm):
    email = EmailField('Other Email',validators=[Optional(),Email()])
    invitemsg = TextAreaField('Message')
    submit = SubmitField("Submit")

class SignForm(FlaskForm):
    content = TextAreaField("Body")
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    content = TextAreaField("Comment")
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    subject = StringField("Title")
    body = TextAreaField("Body")
    submit = SubmitField("Submit")

class EventForm(FlaskForm):
    title = StringField("Title")
    desc = StringField("Description")
    date = DateField("Date", format='%Y-%m-%d')
    time = TimeField("Time")
    submit = SubmitField("Submit")

class FeedbackForm(FlaskForm):
    url = StringField()
    subject = StringField('Subject')
    body = TextAreaField('Description')
    solution = TextAreaField('Solution')
    status = SelectField("Status", choices=[('4-New','4-New'),('1-In Progress','1-In Progress'),('2-Complete','2-Complete'),('3-Maybe Someday','3-Maybe Someday')], default='4-New')
    priority = SelectField("Priority", choices=[('1-High','1-High'),('2-Medium','2-Medium'),('3-Low','3-Low')], default='3-Low')
    submit = SubmitField('Submit')