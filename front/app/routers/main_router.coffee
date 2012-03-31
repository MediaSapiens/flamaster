{ProfileRouter} = require 'routers/profile_router'

{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'
{ProfileView} = require 'views/profile_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "layout"
    '!/': "layout"
    '!/signup': "signup"
    '!/login': "login"

  initialize: ->
    @profileRouter = new ProfileRouter mainRouter: @
        # @model.set model.toJSON(), silent: true

  layout: ->
    $('body').html app.homeView.render()
    @$container = $ '#content'

  signup: ->
    signupView = @renderDefault(SignupView)

  login: ->
    loginView = @renderDefault(LoginView)

  _ensureLayout: ->
    if $("home-view")?
      @layout()

  renderDefault: (ViewClass, options=undefined) ->
    @_ensureLayout()
    classView = options? and new ViewClass(options) or new ViewClass
    @inject classView.render()
    classView

  inject: (html) ->
    @$container.html html
