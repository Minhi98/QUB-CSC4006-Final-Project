from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email

# NOTE - FlaskForm fields must or should be unique; conflicts occur on pages with multiple forms.
#        Solution: Unique field names, or order the forms in such a way that the prioritised form is checked first

class BaseSearchForm(FlaskForm):
    search = SearchField(label='', render_kw={"placeholder": "Search"})
    
class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[InputRequired()])
    password = PasswordField(label='Password', render_kw={"placeholder": "********"}, validators=[InputRequired()])
    submit = SubmitField(label='Sign In', render_kw={'class': "btn btn-dark"})

class LogoutButton(FlaskForm):
    submit = SubmitField(label='Sign Out', render_kw={'class': "btn btn-dark"})

class ChangeDetailsForm(FlaskForm):
    ch_username = StringField(label='New Username')
    ch_password = PasswordField(label='New Password')
    ch_email = EmailField(label='New Email')
    ch_address = StringField(label='New Address')
    ch_submit = SubmitField(label='Confirm', render_kw={'class': "btn btn-dark"})

class RegistrationForm(FlaskForm):
    regusername = StringField(label='Username', validators=[InputRequired()])
    regpassword = PasswordField(label='Password', render_kw={"placeholder": "********"}, validators=[InputRequired()])
    regemail = EmailField(label='Email', render_kw={"placeholder": "user@example.com"}, validators=[InputRequired(), Email()])
    regaddress = StringField(label='Address', render_kw={"placeholder": "123 Street, Town, County, Postcode"})
    regsubmit = SubmitField(label='Confirm', render_kw={'class': "btn btn-dark"})

class DeleteAccountButton(FlaskForm):
    delete_button = SubmitField(label='Delete Account', render_kw={'class': "btn btn-danger"})

class AddToCartButton(FlaskForm):
    addButton = SubmitField(label='Add to Cart')
    item_id = 0
    