{SignupView} = require 'views/signup_view'
{LoginView} = require 'views/login_view'
{ProfileWizardView} = require 'views/profile_wizard_view'

class exports.MainRouter extends Backbone.Router
  routes:
    '': "index"
    '!/': "index"
    '!/signup': "signup"
    '!/signup/complete': "signupComplete"
    '!/login': "login"
    '!/validate/:token': "activate"

  initialize: ->
    @signupView = new SignupView

  index: -> app.render()
  login: -> app.render(LoginView)
  signup: -> @bindInject @signupView, {action: 'signup:start'}
  signupComplete: -> @bindInject @signupView, {action: 'signup:complete'}
  activate: (token) -> @bindInject(new ProfileWizardView(), {token: token, action: 'activate:start'})



  bindInject: (view, options) ->
    mediator.on options.action, (model) =>
      app.inject view.render {action: options.action, model: model}
      mediator.off options.action

    mediator.on 'all', (action, model) ->
      console.log 'action:', action, model

    view.push options
