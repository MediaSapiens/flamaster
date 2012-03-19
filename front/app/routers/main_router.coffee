{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "layout"
    '/': "layout"
    '/signup': "signup"
    '/login': "login"

  layout: ->
    $('body').html app.homeView.render()
    @$container = $ '#content'

  signup: ->
    signupView = @_render(SignupView)

  login: ->
    loginView = @_render(LoginView)

  _ensureLayout: ->
    if $("home-view")?
      @layout()

  _render: (ViewClass) ->
    @_ensureLayout()
    classView = new ViewClass
    @$container.html classView.render()
    classView
