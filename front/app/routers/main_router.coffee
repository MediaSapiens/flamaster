{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "layout"
    '!/': "layout"
    '!/signup': "signup"
    '!/login': "login"

  initialize: -> true
  layout: -> app.render()
  signup: -> app.render(SignupView)
  login: -> app.render(LoginView)



