{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "index"
    '!/': "index"
    '!/signup': "signup"
    '!/login': "login"

  initialize: -> true
  index: ->
    app.render()
    @redirectAuthenticated()

  signup: ->
    app.render(SignupView)
    @redirectAuthenticated()

  login: ->
    app.render(LoginView)
    @redirectAuthenticated()

  redirectAuthenticated: ->
    app.homeView.getCurrentUser
      success: (model, resp) ->
        unless model.get('is_anonymous')
          routePath = "!/profiles/#{model.get 'uid'}"
          app.router.navigate routePath, trigger: true
