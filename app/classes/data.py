
from mongoengine import Document, EmailField, BooleanField, URLField, DateField, FileField, StringField, IntField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField, ListField, CASCADE
import datetime as d

class User(Document):
    # TODO fix where it puts displayName here
    gfname = StringField()
    glname = StringField() 
    email = EmailField()
    gid = StringField(unique=True)
    # App Admin, Student
    role = StringField()
    admin = BooleanField()
    pronouns = StringField()
    fname = StringField()
    lname = StringField()
    image = URLField()
    birthdate = DateField()
    personalemail = EmailField()
    meta = {
        'ordering': ['+lname', '+fname']
    }

class Contributor(EmbeddedDocument):
    user = ReferenceField('User')
    # Editor, Signer, ...
    role = StringField()
    # Invited, Accepted
    status = StringField()
    invitemsg = StringField()

class Book(Document):
    title = StringField()
    owner = ReferenceField('User')
    contributors = ListField(EmbeddedDocumentField(Contributor))
    pages = ListField(ReferenceField('Page'))
    # Draft, Private, Public
    status = StringField()

class Page(Document):
    owner = ReferenceField('User')
    # Draft, Private, Public
    status = StringField()
    # Club, Dept, Friends, ...
    category = StringField()
    contributors = ListField(EmbeddedDocumentField(Contributor))
    # If we have multiple layouts this could be a selectfield on the form
    # Initial layout will be header image and one body image
    layout = StringField()
    title = StringField()
    headerimage = FileField()
    images = ListField(FileField())
    description = StringField()

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
class Comment(Document):
    comment = StringField()
    createdate = DateTimeField(default=d.datetime.utcnow)
    modifydate = DateTimeField
    post = ReferenceField('Post',reverse_delete_rule=CASCADE)
    user = ReferenceField('User',reverse_delete_rule=CASCADE)
    
    meta = {
        'ordering': ['+createdate']
    }

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