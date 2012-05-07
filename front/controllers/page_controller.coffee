define [
  'chaplin/controller', 'models/user',
  'views/signup_view', 'views/dashboard_view', 'views/activation_view',
], (Controller, User, SignUpView, DashboardView, ActivationView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: ->
        @view = new DashboardView

    signup: ->
      nUser = User.extend urlRoot: '/account/sessions/'
      @view = new SignUpView model: new nUser

    dashboard: -> @view = new DashboardView

    activate: ->
      options = {}
      unless window.context?.user
        options.template = 'some_template'
      @view = new ActivationView options
