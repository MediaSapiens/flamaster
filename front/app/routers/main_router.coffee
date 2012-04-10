{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "layout"
    '!/': "layout"
    '!/signup': "signup"
    '!/login': "login"

  initialize: -> true
  layout: ->
    app.render()
    @redirectAuthenticated()

  signup: ->
    app.render(SignupView)
    @redirectAuthenticated()

  login: ->
    app.render(LoginView)
    @redirectAuthenticated()

  redirectAuthenticated: ->
    console.log app.profileRouter
    app.homeView.getCurrentUser
      success: (model, resp) ->
        unless model.get('is_anonymous')
          app.router.navigate "!/profiles/#{model.get 'uid'}", trigger: true
