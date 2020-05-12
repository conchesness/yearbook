
from mongoengine import Document, EmailField, BooleanField, URLField, DateField, FileField, StringField, IntField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField, ListField, CASCADE
import datetime as d

class User(Document):
    gfname = StringField()
    glname = StringField() 
    email = EmailField()
    aeriesid = IntField()
    gid = StringField(unique=True)
    # App Admin, Student
    role = StringField()
    issenior = BooleanField(default=False)
    admin = BooleanField(default=False)
    pronouns = StringField()
    fname = StringField()
    lname = StringField()
    image = FileField()
    birthdate = DateField()
    personalemail = EmailField()
    mobile = StringField()
    address = StringField()
    city = StringField()
    state = StringField()
    zipcode = IntField()
    socmedia = StringField()
    nextyr = StringField()
    invitelist = ListField()
    meta = {
        'ordering': ['+lname', '+fname']
    }

class OTSeniors(Document):
    aeriesid = IntField()
    ousdemail = EmailField()

class Contributor(EmbeddedDocument):
    user = ReferenceField('User')
    # Editor, Signer, ...
    role = StringField()
    # Invited, Accepted
    status = StringField()
    invitemsg = StringField()

class YBook(Document):
    title = StringField()
    owner = ReferenceField('User')
    contributors = ListField(EmbeddedDocumentField(Contributor))
    pages = ListField(ReferenceField('Page'))
    # Draft, Private, Public
    status = StringField()

class Page(Document):
    owner = ReferenceField('User',reverse_delete_rule=CASCADE)
    # Draft, Private, Public
    status = StringField()
    # Club, Dept, Friends, ...
    category = StringField()
    contributors = ListField(EmbeddedDocumentField('Contributor'))
    # If we have multiple layouts this could be a selectfield on the form
    # Initial layout will be header image and one body image
    layout = StringField()
    title = StringField()
    headerimage = FileField()
    image1 = FileField()
    caption1 = StringField()
    image2 = FileField()
    caption2 = StringField()
    image3 = FileField()
    caption3 = StringField()
    image4 = FileField()
    caption4 = StringField()
    description = StringField()
    invitelist = ListField()
    meta = {
        'ordering': ['owner.lname']
    }

class Sign(Document):
    owner = ReferenceField('User',reverse_delete_rule=CASCADE)
    page = ReferenceField('Page',reverse_delete_rule=CASCADE)
    createdate = DateTimeField(default=d.datetime.utcnow)
    content = StringField()
    meta = {
        'ordering': ['-createdate']
    }

class Comment(Document):
    content = StringField()
    signature = ReferenceField('Sign',reverse_delete_rule=CASCADE)
    owner = ReferenceField('User',reverse_delete_rule=CASCADE)
    comment = ReferenceField('self')
    meta = {
        'ordering': ['+createdate']
    }

class Feedback(Document): 
    author = ReferenceField('User',reverse_delete_rule=CASCADE)
    createdate = DateTimeField(default=d.datetime.utcnow)
    modifydate = DateTimeField()
    url = StringField()
    subject = StringField()
    body = StringField()
    status = StringField()
    priority = StringField()
    solution = StringField()

    meta = {
        'ordering': ['+status','+priority', '+createdate']
    }

# TODO Repurpose Post as Signature
class Post(Document):
    user = ReferenceField('User',reverse_delete_rule=CASCADE) 
    feedback = ReferenceField('Feedback')
    subject = StringField()
    body = StringField()
    createdate = DateTimeField(default=d.datetime.utcnow)
    modifydate = DateTimeField()

    meta = {
        'ordering': ['+createdate']
    }

# TODO Delete/Hide Comment 


class Event(Document):
    owner = ReferenceField('User')
    title = StringField()
    desc = StringField()
    #date = DateTimeField(format='%Y-%m-%d')
    date = DateTimeField()
    #job = ReferenceField('Job',reverse_delete_rule=CASCADE)

    meta = {
        'ordering': ['+date']
    }