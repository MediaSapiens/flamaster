define [
  'chaplin/controller', 'models/base_user',
  'views/signup_view', 'views/dashboard_view', 'views/activation_view',
], (Controller, BaseUser, SignUpView, DashboardView, ActivationView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: ->
        @view = new DashboardView

    signup: ->
      @view = new SignUpView model: new BaseUser

    dashboard: -> @view = new DashboardView

    activate: ->
      options = {}
      unless window.context?.user
        options.template = 'some_template'
      @view = new ActivationView options
