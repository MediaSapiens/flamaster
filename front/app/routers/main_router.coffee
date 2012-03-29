{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'
{ProfileView} = require 'views/profile_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "layout"
    '!/': "layout"
    '!/signup': "signup"
    '!/login': "login"
    '!/profile/:id': "profile"

  layout: ->
    $('body').html app.homeView.render()
    @$container = $ '#content'

  signup: ->
    signupView = @_render(SignupView)

  login: ->
    loginView = @_render(LoginView)

  profile: (id) ->
    profileView = @_render(ProfileView, {id: id})


  _ensureLayout: ->
    if $("home-view")?
      @layout()

  _render: (ViewClass, options=undefined) ->
    @_ensureLayout()
    classView = options? and new ViewClass(options) or new ViewClass
    @$container.html classView.render()
    classView
