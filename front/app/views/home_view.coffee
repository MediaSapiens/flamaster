{SessionModel} = require 'models/session_model'
{NavView} = require 'views/nav_view'

class exports.HomeView extends Backbone.View
  id: 'home-view'
  template: require('./templates/home')

  initialize: ->
    @navView = new NavView
      model:
        index: ["Index", '!/']
        signup: ["Sign Up", '!/signup']
        login: ["Login", '!/login']
      session: @getCurrentUser()


  render: ->
    @$el.html @template
    @$el.find("#nav-container").html @navView.render()
    @el

  getCurrentUser: (options) ->
    @session = new SessionModel
    if options?
      @session.fetch
        success: options.success
        error: options.error
