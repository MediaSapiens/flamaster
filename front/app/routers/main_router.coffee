{SignupView} = require 'views/signup_view'
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
    @_ensureLayout()
    signupView = new SignupView
    @$container.html signupView.render()

  login: ->
    @_ensureLayout()
    true

  _ensureLayout: ->
    if $("home-view")?
      @layout()
