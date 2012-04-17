{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "index"
    '!/': "index"
    '!/signup': "signup"
    '!/signup/complete': "signupComplete"
    '!/login': "login"

  initialize: ->
    @signupView = new SignupView

  index: ->
    app.render()

  signup: -> @bindInject @signupView, {action: 'signup:start'}
  signupComplete: -> @bindInject @signupView, {action: 'signup:complete'}


  login: ->
    app.render(LoginView)

  bindInject: (view, options) ->
    mediator.on options.action, (model) =>
      app.inject view.render {action: options.action, model: model}
      mediator.off options.action

    mediator.on 'all', (action, model) ->
      console.log 'action:', action, model

    view.push options
